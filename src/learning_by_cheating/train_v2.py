#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Training script for PA model using preprocessed data

사용법:
    # 기본 설정으로 학습
    python3 train_v2.py --pickle_file data/Preprocessing/LBC_20260331_145605_processed.pkl
    
    # 커스텀 설정
    python3 train_v2.py \\
        --pickle_file data/Preprocessing/LBC_20260331_145605_processed.pkl \\
        --batch_size 16 \\
        --epochs 50 \\
        --learning_rate 1e-3
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

_LBC_ROOT = Path(__file__).resolve().parent

import torch
import torch.nn as nn
import torch.optim as optim

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False
    print("⚠️  Warning: tensorboard not installed. Logging disabled.")
    print("   Install with: pip install tensorboard")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from model.pa_model import PAModel, PALoss
from dataset_v2 import create_dataloaders


class Trainer:
    """Trainer class for PA model"""
    
    def __init__(
        self,
        model,
        train_loader,
        val_loader,
        optimizer,
        loss_fn,
        device,
        save_dir,
        log_dir,
    ):
        """
        Initialize trainer
        
        Args:
            model: PA model
            train_loader: Training dataloader
            val_loader: Validation dataloader
            optimizer: Optimizer
            loss_fn: Loss function
            device: 'cuda' or 'cpu'
            save_dir: Directory to save checkpoints
            log_dir: Directory to save logs
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.device = device
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Tensorboard writer
        if TENSORBOARD_AVAILABLE:
            self.writer = SummaryWriter(log_dir)
        else:
            self.writer = None
        
        # Training state
        self.epoch = 0
        self.global_step = 0
        self.best_val_loss = float('inf')
        
        # Save config
        self.config = {
            'device': str(device),
            'model': 'PAModel',
            'num_parameters': sum(p.numel() for p in model.parameters()),
        }
    
    def train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, batch in enumerate(self.train_loader):
            bev_map = batch['bev_map'].to(self.device)      # (B, 3, 256, 256)
            velocity = batch['velocity'].to(self.device)    # (B, 1)
            waypoints_gt = batch['waypoints'].to(self.device)  # (B, 4, 2)
            
            # Forward pass
            self.optimizer.zero_grad()
            waypoints_pred, heatmaps = self.model(bev_map, velocity)
            
            # Loss computation
            loss = self.loss_fn(waypoints_pred, waypoints_gt)
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
            self.global_step += 1
            
            # Logging
            if (batch_idx + 1) % 10 == 0:
                avg_loss = total_loss / (batch_idx + 1)
                print(
                    f"Epoch {self.epoch:3d} | "
                    f"Batch {batch_idx+1:3d}/{len(self.train_loader)} | "
                    f"Loss: {avg_loss:.6f}"
                )
                
                if self.writer is not None:
                    self.writer.add_scalar(
                        'train/loss',
                        avg_loss,
                        self.global_step,
                    )
        
        return total_loss / len(self.train_loader)
    
    @torch.no_grad()
    def validate(self):
        """Validate on validation set"""
        self.model.eval()
        total_loss = 0.0
        
        for batch in self.val_loader:
            bev_map = batch['bev_map'].to(self.device)
            velocity = batch['velocity'].to(self.device)
            waypoints_gt = batch['waypoints'].to(self.device)
            
            # Forward pass
            waypoints_pred, heatmaps = self.model(bev_map, velocity)
            
            # Loss computation
            loss = self.loss_fn(waypoints_pred, waypoints_gt)
            total_loss += loss.item()
        
        avg_val_loss = total_loss / len(self.val_loader)
        
        if self.writer is not None:
            self.writer.add_scalar(
                'val/loss',
                avg_val_loss,
                self.global_step,
            )
        
        return avg_val_loss
    
    def save_checkpoint(self, name='latest'):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': self.epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'global_step': self.global_step,
            'config': self.config,
        }
        
        save_path = self.save_dir / f"checkpoint_{name}.pth"
        torch.save(checkpoint, save_path)
        print(f"✅ 저장됨: {save_path}")
    
    def load_checkpoint(self, checkpoint_path):
        """Load model checkpoint"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epoch = checkpoint.get('epoch', 0)
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        self.global_step = checkpoint.get('global_step', 0)
        print(f"✅ 로드됨: {checkpoint_path}")
    
    def train(self, num_epochs=50, save_interval=5, val_interval=1):
        """Train model"""
        print("=" * 70)
        print("🚀 학습 시작")
        print("=" * 70)
        
        for epoch in range(num_epochs):
            self.epoch = epoch
            
            # Train
            train_loss = self.train_epoch()
            print(f"Epoch {epoch:3d} | 학습 손실: {train_loss:.6f}")
            
            # Validate
            if (epoch + 1) % val_interval == 0:
                val_loss = self.validate()
                print(f"Epoch {epoch:3d} | 검증 손실: {val_loss:.6f}")
                
                # Save best model
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    print(f"         🏆 최고 성능 모델 저장 (손실: {val_loss:.6f})")
                    self.save_checkpoint('best')
            
            # Save periodic checkpoint
            if (epoch + 1) % save_interval == 0:
                self.save_checkpoint(f'epoch_{epoch:03d}')
            
            print("-" * 70)
        
        print("=" * 70)
        print("✅ 학습 완료")
        print("=" * 70)
        if self.writer is not None:
            self.writer.close()


def main(args):
    """Main training function"""
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🖥️  Device: {device}")
    
    # Create dataloaders
    print("\n📖 데이터 로드 중...")
    train_loader, val_loader = create_dataloaders(
        pickle_file=args.pickle_file,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        train_ratio=args.train_ratio,
        num_waypoints=args.num_waypoints,
    )
    
    print(f"   학습 샘플: {len(train_loader.dataset)}")
    print(f"   검증 샘플: {len(val_loader.dataset)}")
    
    # Create model
    print("\n🏗️  모델 생성 중...")
    model = PAModel(
        num_waypoints=args.num_waypoints,
        bev_channels=3,
        bev_size=256,  # 전처리된 데이터는 320×320을 256으로 resize
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   파라미터 수: {total_params:,}")
    
    # Create optimizer and loss function
    optimizer = optim.Adam(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    
    # Enhanced loss function with waypoint importance weighting
    # Closer waypoints (경로 시작점)에 더 높은 가중치 적용
    # [1.0, 0.8, 0.6, 0.4] → 첫 번째 waypoint가 4번째보다 2.5배 중요
    waypoint_weights = [1.0, 0.8, 0.6, 0.4]
    loss_fn = PALoss(reduction='mean', waypoint_weights=waypoint_weights)
    
    # Create trainer
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = Path(args.save_dir) / f"pa_model_{timestamp}"
    log_dir = Path(args.log_dir) / f"pa_model_{timestamp}"
    
    print(f"\n💾 체크포인트 저장 경로: {save_dir}")
    
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        loss_fn=loss_fn,
        device=device,
        save_dir=save_dir,
        log_dir=log_dir,
    )
    
    # Load checkpoint if specified
    if args.checkpoint:
        trainer.load_checkpoint(args.checkpoint)
    
    # Train
    trainer.train(
        num_epochs=args.epochs,
        save_interval=args.save_interval,
        val_interval=args.val_interval,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PA 모델 학습 (전처리된 데이터 사용)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 기본 설정으로 학습
  python3 train_v2.py --pickle_file data/Preprocessing/LBC_20260331_145605_processed.pkl
  
  # 커스텀 설정
  python3 train_v2.py \\
    --pickle_file data/Preprocessing/LBC_20260331_145605_processed.pkl \\
    --batch_size 16 \\
    --epochs 50 \\
    --learning_rate 1e-3
        """
    )
    
    # Data
    parser.add_argument(
        '--pickle_file',
        type=str,
        required=True,
        help='전처리된 pickle 파일 경로 (필수)'
    )
    parser.add_argument(
        '--batch_size',
        type=int,
        default=32,
        help='배치 크기 (기본: 32)'
    )
    parser.add_argument(
        '--num_workers',
        type=int,
        default=4,
        help='데이터 로딩 워커 수 (기본: 4)'
    )
    parser.add_argument(
        '--train_ratio',
        type=float,
        default=0.8,
        help='학습 데이터 비율 (기본: 0.8)'
    )
    
    # Model
    parser.add_argument(
        '--num_waypoints',
        type=int,
        default=4,
        help='예측할 waypoint 수 (기본: 4)'
    )
    
    # Training
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='에포크 수 (기본: 50)'
    )
    parser.add_argument(
        '--learning_rate',
        type=float,
        default=1e-3,
        help='학습률 (기본: 1e-3)'
    )
    parser.add_argument(
        '--weight_decay',
        type=float,
        default=1e-5,
        help='가중치 감쇠 (기본: 1e-5)'
    )
    
    # Checkpoint
    parser.add_argument(
        '--checkpoint',
        type=str,
        default=None,
        help='복구할 체크포인트 경로 (선택사항)'
    )
    parser.add_argument(
        '--save_dir',
        type=str,
        default=str(_LBC_ROOT / 'checkpoints'),
        help='체크포인트 저장 경로'
    )
    parser.add_argument(
        '--log_dir',
        type=str,
        default=str(_LBC_ROOT / 'logs'),
        help='로그 저장 경로'
    )
    parser.add_argument(
        '--save_interval',
        type=int,
        default=5,
        help='N 에포크마다 체크포인트 저장 (기본: 5)'
    )
    parser.add_argument(
        '--val_interval',
        type=int,
        default=1,
        help='N 에포크마다 검증 (기본: 1)'
    )
    
    args = parser.parse_args()
    main(args)
