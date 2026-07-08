#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Privileged Agent (PA) Model Implementation
Based on "Learning by Cheating" paper (Pathak et al., 2020)

Modified for custom dataset:
- BEV Map: 3 channels (map_line, map_npc, map_path) instead of 7
- BEV Resolution: 256×256 instead of 320×320
- Inputs: BEV map, velocity, target waypoints
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import numpy as np


class PAModel(nn.Module):
    """
    Privileged Agent (PA) Model for autonomous driving
    
    Input:
    - BEV Map: (B, 3, 256, 256) - 3 binary channels (map_line, map_npc, map_path)
    - Velocity: (B, 1) - scalar velocity
    
    Output:
    - Waypoints: (B, K, 2) - K future waypoints in vehicle coordinates
    """
    
    def __init__(
        self,
        num_waypoints=4,
        bev_channels=3,
        bev_size=256,
        crop_size=192,
        feature_dim=512,
    ):
        """
        Initialize PA Model
        
        Args:
            num_waypoints: Number of future waypoints to predict (K)
            bev_channels: Number of BEV channels (3: map_line, map_npc, map_path)
            bev_size: Input BEV resolution (256×256)
            crop_size: Crop size for network input (192×192)
            feature_dim: Feature dimension after backbone
        """
        super().__init__()
        
        self.num_waypoints = num_waypoints
        self.bev_channels = bev_channels
        self.bev_size = bev_size
        self.crop_size = crop_size
        self.feature_dim = feature_dim
        self.heatmap_size = crop_size // 4  # 48×48 after backbone downsampling
        
        # ========== 1. Backbone: ResNet-18 ==========
        resnet18 = models.resnet18(pretrained=False)
        
        # Modify first conv to accept 3 BEV channels instead of 3 RGB
        original_conv = resnet18.conv1
        self.backbone = nn.Sequential(
            nn.Conv2d(bev_channels, 64, kernel_size=7, stride=2, padding=3, bias=False),
            resnet18.bn1,
            resnet18.relu,
            resnet18.maxpool,
            resnet18.layer1,
            resnet18.layer2,
            resnet18.layer3,
            resnet18.layer4,
            nn.AdaptiveAvgPool2d(output_size=1),  # Global average pooling
        )
        
        # Backbone output: 512 channels (ResNet-18 final layer depth)
        backbone_output_dim = 512
        
        # ========== 3. Velocity Encoder ==========
        self.velocity_encoder = nn.Sequential(
            nn.Linear(1, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 64),
        )
        
        # Combine features
        context_dim = backbone_output_dim + 64  # backbone + velocity
        
        # ========== 4. Feature Expansion ==========
        # Expand context vector to spatial feature map
        self.feature_expansion = nn.Sequential(
            nn.Linear(context_dim, feature_dim),
            nn.ReLU(inplace=True),
        )
        
        # ========== 5. Up-convolutional Layers ==========
        # Expand from feature_dim to spatial heatmap
        # Input: (B, feature_dim) -> Output: (B, num_waypoints, heatmap_size, heatmap_size)
        
        self.decoder = nn.Sequential(
            # Upsample: 1×1 -> 12×12
            nn.ConvTranspose2d(feature_dim, 256, kernel_size=12, stride=12, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            # Upsample: 12×12 -> 24×24
            nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            # Upsample: 24×24 -> 48×48
            nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
        )
        
        # ========== 6. Single Output Head ==========
        # Single head (no command branching)
        self.head = nn.Conv2d(64, num_waypoints, kernel_size=1)
        
        # Heatmap activation (sigmoid for [0,1] range)
        self.heatmap_activation = nn.Sigmoid()
    
    def forward(self, bev_map, velocity):
        """
        Forward pass
        
        Args:
            bev_map: (B, 3, 256, 256) - BEV map
            velocity: (B, 1) - current velocity
        
        Returns:
            waypoints: (B, K, 2) - predicted waypoints in vehicle coordinates
            heatmaps: (B, K, H, W) - intermediate heatmaps
        """
        batch_size = bev_map.shape[0]
        
        # ===== Step 1: Crop BEV map to center region =====
        # From 256×256 to 192×192 (keeping center)
        if self.bev_size != self.crop_size:
            offset = (self.bev_size - self.crop_size) // 2
            bev_map = bev_map[
                :,
                :,
                offset:offset + self.crop_size,
                offset:offset + self.crop_size,
            ]
        
        # ===== Step 2: Backbone (ResNet-18) =====
        backbone_features = self.backbone(bev_map)  # (B, 512, 1, 1)
        backbone_features = backbone_features.view(batch_size, -1)  # (B, 512)
        
        # ===== Step 3: Encode velocity =====
        velocity_features = self.velocity_encoder(velocity)  # (B, 64)
        
        # ===== Step 4: Combine context =====
        context = torch.cat([backbone_features, velocity_features], dim=1)  # (B, 576)
        
        # ===== Step 5: Expand to feature map =====
        features = self.feature_expansion(context)  # (B, feature_dim)
        features = features.view(batch_size, -1, 1, 1)  # (B, feature_dim, 1, 1)
        
        # ===== Step 6: Decode to heatmaps =====
        decoded_features = self.decoder(features)  # (B, 64, 48, 48)
        
        # ===== Step 7: Get heatmaps from head =====
        heatmaps = self.head(decoded_features)  # (B, K, 48, 48)
        heatmaps = self.heatmap_activation(heatmaps)
        
        # ===== Step 8: Soft-argmax to get waypoints =====
        waypoints = self._soft_argmax(heatmaps)  # (B, K, 2)
        
        return waypoints, heatmaps
    
    def _soft_argmax(self, heatmaps):
        """
        Convert heatmaps to 2D coordinates using soft-argmax
        
        Differentiable operation for end-to-end learning:
        ŵ_k = Σ_{x,y} [x, y]^T · h_{x,y} / Σ_{x,y} h_{x,y}
        
        Args:
            heatmaps: (B, K, H, W) - heatmaps for K waypoints
        
        Returns:
            waypoints: (B, K, 2) - (x, y) coordinates normalized to [-1, 1]
        """
        batch_size, num_waypoints, height, width = heatmaps.shape
        
        # Create coordinate grids
        yy, xx = torch.meshgrid(
            torch.linspace(-1, 1, height, device=heatmaps.device),
            torch.linspace(-1, 1, width, device=heatmaps.device),
            indexing='ij'
        )
        
        # Normalize heatmaps to sum to 1
        heatmaps_sum = heatmaps.sum(dim=(2, 3), keepdim=True) + 1e-8
        normalized_heatmaps = heatmaps / heatmaps_sum
        
        # Compute weighted coordinates
        waypoints = torch.zeros(batch_size, num_waypoints, 2, device=heatmaps.device)
        
        for k in range(num_waypoints):
            hm = normalized_heatmaps[:, k, :, :]  # (B, H, W)
            
            # Weighted sum of x coordinates
            waypoints[:, k, 0] = (hm * xx.unsqueeze(0)).sum(dim=(1, 2))
            
            # Weighted sum of y coordinates
            waypoints[:, k, 1] = (hm * yy.unsqueeze(0)).sum(dim=(1, 2))
        
        return waypoints


class PALoss(nn.Module):
    """
    Loss function for PA model training
    
    Weighted L1 distance between predicted and ground-truth waypoints:
    L = sum_k (weight_k * ||w_pred_k - w_gt_k||_2)
    
    Closer waypoints (k=0) have higher weights to prioritize accurate near-term predictions
    """
    
    def __init__(self, reduction='mean', waypoint_weights=None):
        """
        Args:
            reduction: 'mean' or 'sum'
            waypoint_weights: (K,) tensor or list of weights for each waypoint
                             Default: [1.0, 0.8, 0.6, 0.4] (emphasize closer waypoints)
        """
        super().__init__()
        self.reduction = reduction
        
        # Default weights: closer waypoints have higher importance
        if waypoint_weights is None:
            waypoint_weights = [1.0, 0.8, 0.6, 0.4]
        
        if isinstance(waypoint_weights, list):
            waypoint_weights = torch.tensor(waypoint_weights, dtype=torch.float32)
        
        self.register_buffer('waypoint_weights', waypoint_weights)
    
    def forward(self, waypoints_pred, waypoints_gt):
        """
        Compute weighted L2 distance loss
        
        Args:
            waypoints_pred: (B, K, 2) - predicted waypoints
            waypoints_gt: (B, K, 2) - ground-truth waypoints
        
        Returns:
            loss: scalar loss value
        """
        # Ensure weights are on the same device as predictions
        weights = self.waypoint_weights.to(waypoints_pred.device)
        
        # Compute L2 distance for each waypoint: sqrt((x1-x2)^2 + (y1-y2)^2)
        distances = torch.sqrt(torch.sum((waypoints_pred - waypoints_gt) ** 2, dim=2))  # (B, K)
        
        # Apply waypoint-specific weights
        weighted_distances = distances * weights.unsqueeze(0)  # (B, K) * (K,) -> (B, K)
        
        # Aggregate across batch and waypoints
        if self.reduction == 'mean':
            loss = weighted_distances.mean()
        elif self.reduction == 'sum':
            loss = weighted_distances.sum()
        else:
            raise ValueError(f"Unknown reduction: {self.reduction}")
        
        return loss


def create_pa_model(
    num_waypoints=4,
    bev_channels=3,
    device='cuda'
):
    """
    Create PA model
    
    Args:
        num_waypoints: Number of waypoints to predict
        bev_channels: Number of BEV channels (3: map_line, map_npc, map_path)
        device: 'cuda' or 'cpu'
    
    Returns:
        model: PA model instance
    """
    model = PAModel(
        num_waypoints=num_waypoints,
        bev_channels=bev_channels,
    )
    model = model.to(device)
    return model


if __name__ == "__main__":
    # Test model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Create model
    model = create_pa_model(
        num_waypoints=4,
        bev_channels=3,
        device=device
    )
    
    print("=" * 60)
    print("PA Model Architecture (Single Head)")
    print("=" * 60)
    print(model)
    
    # Create dummy inputs
    batch_size = 2
    bev_map = torch.randn(batch_size, 3, 256, 256).to(device)
    velocity = torch.randn(batch_size, 1).to(device)
    
    # Forward pass
    waypoints, heatmaps = model(bev_map, velocity)
    
    print("\n" + "=" * 60)
    print("Forward Pass Test")
    print("=" * 60)
    print(f"Input BEV shape: {bev_map.shape}")
    print(f"Input velocity shape: {velocity.shape}")
    print(f"Output waypoints shape: {waypoints.shape}")
    print(f"Output heatmaps shape: {heatmaps.shape}")
    print(f"Waypoints range: [{waypoints.min():.3f}, {waypoints.max():.3f}]")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print("\n" + "=" * 60)
    print("Model Parameters")
    print("=" * 60)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
