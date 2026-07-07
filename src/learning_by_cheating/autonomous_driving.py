#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Autonomous driving script using trained PA model
Predicts waypoints and publishes control commands
"""

import sys
import math
import threading
from pathlib import Path

_LBC_ROOT = Path(__file__).resolve().parent

import numpy as np
import torch
import rospy
from morai_msgs.msg import CtrlCmd, EgoVehicleStatus
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import CompressedImage
from visualization_msgs.msg import Marker, MarkerArray
import cv2
from cv_bridge import CvBridge

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from model.pa_model import PAModel
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from model.pa_model import PAModel


class AutonomousDrivingController:
    """Autonomous driving controller using PA model"""
    
    def __init__(self, checkpoint_path, device='cuda'):
        """
        Initialize autonomous driving controller
        
        Args:
            checkpoint_path: Path to trained model checkpoint
            device: 'cuda' or 'cpu'
        """
        self.device = device
        self.debug = True  # Debug logging enabled
        
        # Load model
        print("Loading model...")
        self.model = PAModel(
            num_waypoints=4,
            bev_channels=3,
        ).to(device)
        
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        print("Model loaded successfully!")
        
        # Current vehicle state
        self.current_pos = np.array([0.0, 0.0])
        self.current_velocity = 0.0
        self.current_heading = 0.0
        self.current_wheel_angle = 0.0
        
        # BEV map (3 channels)
        self.bev_map = None
        self.bev_map_line = None
        self.bev_map_npc = None
        self.bev_map_path = None
        self.bev_lock = threading.Lock()
        
        # Control parameters
        self.target_speed = 2.0  # m/s
        self.max_steering_angle = 45.0 * np.pi / 180.0  # 45 degrees (radians)
        self.k_gain = 0.5  # Stanley controller gain
        self.Kp = 0.3  # PID P gain
        self.Ki = 0.05  # PID I gain
        self.Kd = 0.1  # PID D gain
        self.prev_speed_error = 0.0
        self.integral_speed_error = 0.0
        
        # ROS setup (초기화는 가장 먼저)
        rospy.init_node('autonomous_driving_controller', anonymous=True)
        
        # 이제 rospy.get_time() 호출 가능
        self.last_time = rospy.get_time()
        
        # Subscriber for ego vehicle status
        rospy.Subscriber(
            '/Ego_topic',
            EgoVehicleStatus,
            self.ego_callback,
            queue_size=1
        )
        
        # Subscriber for BEV map (3 channels: line, npc, path)
        rospy.Subscriber(
            '/map_line',
            OccupancyGrid,
            self.bev_line_callback,
            queue_size=1
        )
        rospy.Subscriber(
            '/map_npc',
            OccupancyGrid,
            self.bev_npc_callback,
            queue_size=1
        )
        rospy.Subscriber(
            '/map_path',
            OccupancyGrid,
            self.bev_path_callback,
            queue_size=1
        )
        
        # Publisher for control command
        self.ctrl_pub = rospy.Publisher(
            '/ctrl_cmd_0',
            CtrlCmd,
            queue_size=1
        )
        
        # Publisher for waypoint visualization (latch=True for initial subscribers)
        self.waypoint_marker_pub = rospy.Publisher(
            '/pa_waypoints',
            MarkerArray,
            queue_size=10,
            latch=True
        )
        
        print("ROS node initialized!")
        print("Waiting for BEV map (3 channels)...")
        
        # Wait for first BEV map
        timeout = 10
        start_time = rospy.get_time()
        while (self.bev_map_line is None or self.bev_map_npc is None or self.bev_map_path is None) and \
              (rospy.get_time() - start_time) < timeout:
            rospy.sleep(0.1)
        
        if self.bev_map_line is None or self.bev_map_npc is None or self.bev_map_path is None:
            rospy.logwarn("Some BEV map channels not received within timeout!")
        else:
            rospy.loginfo("All BEV map channels received successfully!")
    
    def ego_callback(self, msg):
        """Callback for ego vehicle status"""
        self.current_pos = np.array([msg.position.x, msg.position.y])
        self.current_heading = msg.heading * np.pi / 180.0  # Convert to radians
        
        # Calculate velocity magnitude
        vx = msg.velocity.x
        vy = msg.velocity.y
        self.current_velocity = math.sqrt(vx**2 + vy**2)
        self.current_wheel_angle = msg.wheel_angle
    
    def occupancy_to_numpy(self, msg):
        """Convert OccupancyGrid message to normalized numpy array"""
        width = msg.info.width
        height = msg.info.height
        data = np.array(msg.data, dtype=np.float32).reshape((height, width))
        # Normalize to [0, 1]
        data = np.clip(data / 100.0, 0.0, 1.0)
        return data
    
    def bev_line_callback(self, msg):
        """Callback for map_line (Channel 0)"""
        with self.bev_lock:
            self.bev_map_line = self.occupancy_to_numpy(msg)
    
    def bev_npc_callback(self, msg):
        """Callback for map_npc (Channel 1)"""
        with self.bev_lock:
            self.bev_map_npc = self.occupancy_to_numpy(msg)
    
    def bev_path_callback(self, msg):
        """Callback for map_path (Channel 2)"""
        with self.bev_lock:
            self.bev_map_path = self.occupancy_to_numpy(msg)
    
    def create_bev_map(self, width=256, height=256):
        """
        Get BEV map from ROS topic (3 channels: line, npc, path)
        
        Args:
            width: BEV map width (model expects 256x256)
            height: BEV map height (model expects 256x256)
        
        Returns:
            BEV map tensor (C, H, W)
        """
        with self.bev_lock:
            if self.bev_map_line is not None and self.bev_map_npc is not None and self.bev_map_path is not None:
                # Stack 3 channels
                bev_map = np.stack([
                    self.bev_map_line,   # Channel 0: road lines
                    self.bev_map_npc,    # Channel 1: NPC/obstacles
                    self.bev_map_path    # Channel 2: path
                ], axis=0).astype(np.float32)
            else:
                # Fallback: create dummy map if not all channels received
                bev_map = np.zeros((3, height, width), dtype=np.float32)
                bev_map[0, :, :] = 1.0  # All free space
                rospy.logwarn_throttle(5, "BEV map not fully available, using dummy map")
        
        # Ensure correct size (256x256 as model expects)
        if bev_map.shape[1] != height or bev_map.shape[2] != width:
            # Resize if needed
            bev_resized = np.zeros((3, height, width), dtype=np.float32)
            for c in range(3):
                bev_resized[c] = cv2.resize(
                    bev_map[c],
                    (width, height),
                    interpolation=cv2.INTER_LINEAR
                )
            bev_map = bev_resized
        
        return torch.from_numpy(bev_map).to(self.device)
    
    def predict_waypoints(self, bev_map, velocity):
        """
        Predict waypoints using PA model
        
        Args:
            bev_map: BEV map tensor (C, H, W)
            velocity: Current velocity (scalar)
        
        Returns:
            waypoints: Predicted waypoints (num_waypoints, 2) in meters
        """
        with torch.no_grad():
            # Add batch dimension
            bev_map = bev_map.unsqueeze(0)  # (1, C, H, W)
            
            # Check BEV map validity
            bev_sum = bev_map.sum().item()
            if bev_sum == 0:
                rospy.logwarn_throttle(5, "⚠️  BEV map is all zeros! Likely dummy map.")
            
            # Normalize velocity to [0, 1] (assuming max 30 km/h)
            velocity_kmh = velocity * 3.6  # m/s to km/h
            velocity_norm = np.clip(velocity_kmh / 30.0, 0.0, 1.0)
            
            # Create velocity tensor
            velocity_tensor = torch.tensor(
                [[velocity_norm]], 
                dtype=torch.float32, 
                device=self.device
            )  # (1, 1)
            
            try:
                # Forward pass
                waypoints_pred, heatmaps = self.model(bev_map, velocity_tensor)
                
                # Remove batch dimension and move to numpy
                # Model output: [-1, 1] normalized coordinates
                waypoints_norm = waypoints_pred[0].cpu().numpy()  # (num_waypoints, 2) in [-1, 1]
                
                # Convert from normalized [-1, 1] to meters (±16m)
                waypoints = waypoints_norm * 16.0  # (num_waypoints, 2) in meters
                
                # Validation checks
                if np.any(np.isnan(waypoints)) or np.any(np.isinf(waypoints)):
                    rospy.logwarn(f"❌ Invalid waypoints detected (NaN/Inf): {waypoints}")
                    return np.zeros((4, 2))
                
                # Debug logging
                if self.debug:
                    rospy.logdebug(
                        f"[Model] vel={velocity:.2f}m/s({velocity_norm:.2f}), "
                        f"bev_sum={bev_sum:.0f}, "
                        f"wp0=({waypoints[0][0]:+.2f}, {waypoints[0][1]:+.2f}), "
                        f"wp1=({waypoints[1][0]:+.2f}, {waypoints[1][1]:+.2f})"
                    )
                
            except Exception as e:
                rospy.logerr(f"❌ Model prediction failed: {e}")
                import traceback
                traceback.print_exc()
                return np.zeros((4, 2))
        
        return waypoints
    
    def waypoints_to_steering(self, waypoints):
        """
        Convert predicted waypoints to steering angle using Stanley method
        Base link coordinate system: lx=forward, ly=left
        
        Args:
            waypoints: Predicted waypoints (num_waypoints, 2) in meters [lx, ly]
        
        Returns:
            steering_angle: Steering angle (radians, clipped to max)
        """
        if len(waypoints) == 0:
            return 0.0
        
        # Use first waypoint for control
        # (closer points are more important for immediate control)
        lx = waypoints[0][0]  # Forward distance
        ly = waypoints[0][1]  # Lateral offset
        
        # Sanity check: if waypoints are NaN or invalid, return 0
        if not np.isfinite(lx) or not np.isfinite(ly):
            rospy.logwarn(f"Invalid waypoints detected: lx={lx}, ly={ly}")
            return 0.0
        
        # Clamp waypoints to reasonable range (±32m forward, ±32m lateral)
        lx = np.clip(lx, -32.0, 64.0)
        ly = np.clip(ly, -32.0, 32.0)
        
        # Current velocity (at least 0.5 m/s to avoid division by zero)
        v = max(0.5, self.current_velocity)
        
        # Heading error (angle to target waypoint)
        # If lx > 0, target heading is atan2(ly, lx)
        if lx > 0.1:
            target_heading = np.arctan2(ly, lx)
        else:
            # If waypoint is behind (lx < 0), focus on lateral error
            target_heading = 0.0
        
        # Lateral path error (base_link is at rear, so ly is lateral error)
        path_error = ly
        
        # Stanley control law:
        # steering = heading_error + atan(k_gain * path_error / velocity)
        try:
            steering_raw = target_heading + np.arctan(self.k_gain * path_error / v)
        except Exception as e:
            rospy.logwarn(f"Stanley calculation error: {e}")
            return 0.0
        
        # Limit steering angle
        steering_command = np.clip(
            steering_raw,
            -self.max_steering_angle,
            self.max_steering_angle
        )
        
        # Debug logging
        rospy.logdebug(
            f"Steering calc: lx={lx:.2f}, ly={ly:.2f}, heading={target_heading*180/np.pi:.1f}°, "
            f"path_err={path_error:.2f}, steering={steering_command*180/np.pi:.1f}°"
        )
        
        return steering_command
    
    def waypoints_to_throttle(self):
        """
        Generate throttle/brake command based on target speed using PID control
        
        Returns:
            accel: Acceleration command (0.0 to 1.0)
            brake: Brake command (0.0 to 1.0)
        """
        current_time = rospy.get_time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        if dt <= 0:
            dt = 0.02
        
        # Speed error
        speed_error = self.target_speed - self.current_velocity
        self.integral_speed_error += speed_error * dt
        
        # Clamp integral error
        self.integral_speed_error = np.clip(self.integral_speed_error, -10.0, 10.0)
        
        # PID output
        p_output = self.Kp * speed_error
        i_output = self.Ki * self.integral_speed_error
        d_output = self.Kd * ((speed_error - self.prev_speed_error) / max(dt, 0.02))
        self.prev_speed_error = speed_error
        
        total_output = p_output + i_output + d_output
        
        # Convert to accel/brake
        if total_output > 0:
            accel = np.clip(total_output, 0.0, 1.0)
            brake = 0.0
        else:
            accel = 0.0
            brake = np.clip(-total_output, 0.0, 1.0)
        
        return accel, brake
    
    def publish_control_command(self, steering, accel, brake):
        """
        Publish control command to vehicle
        
        Args:
            steering: Steering angle command (radians)
            accel: Acceleration command (0.0 to 1.0)
            brake: Brake command (0.0 to 1.0)
        """
        ctrl_cmd = CtrlCmd()
        
        # Safety: Double-check steering bounds (should already be clipped)
        steering_safe = np.clip(steering, -self.max_steering_angle, self.max_steering_angle)
        
        # MORAI expects steering in radians
        ctrl_cmd.steering = steering_safe
        ctrl_cmd.accel = np.clip(accel, 0.0, 1.0)
        ctrl_cmd.brake = np.clip(brake, 0.0, 1.0)
        ctrl_cmd.longlCmdType = 1  # 1=accel/brake mode, 2=velocity mode
        
        # Debug: warn if clipping occurred at publish time
        if abs(steering_safe) != abs(steering):
            rospy.logwarn(
                f"Steering re-clipped at publish: {steering*180/np.pi:.1f}° → {steering_safe*180/np.pi:.1f}°"
            )
        
        # Publish
        self.ctrl_pub.publish(ctrl_cmd)
    
    def publish_waypoint_markers(self, waypoints):
        """
        Publish waypoint markers for RViz visualization
        
        Args:
            waypoints: Predicted waypoints (num_waypoints, 2) in base_link frame
        """
        try:
            marker_array = MarkerArray()
            frame_id = "base_link"  # ← base_link으로 변경
            
            # 1. Line strip showing the path
            line_marker = Marker()
            line_marker.header.frame_id = frame_id
            line_marker.header.stamp = rospy.Time.now()
            line_marker.ns = "waypoint_path"
            line_marker.id = 0
            line_marker.type = Marker.LINE_STRIP
            line_marker.action = Marker.ADD
            line_marker.scale.x = 0.2
            line_marker.color.r = 0.0
            line_marker.color.g = 1.0
            line_marker.color.b = 0.0
            line_marker.color.a = 1.0
            line_marker.lifetime = rospy.Duration(0.5)
            line_marker.pose.orientation.w = 1.0
            
            # Add origin
            from geometry_msgs.msg import Point
            origin = Point()
            origin.x, origin.y, origin.z = 0.0, 0.0, 0.0
            line_marker.points.append(origin)
            
            # Add waypoints to line
            for wp in waypoints:
                p = Point()
                p.x = wp[0]
                p.y = wp[1]
                p.z = 0.05
                line_marker.points.append(p)
            
            marker_array.markers.append(line_marker)
            
            # 2. Sphere markers for each waypoint
            for i, waypoint in enumerate(waypoints):
                sphere = Marker()
                sphere.header.frame_id = frame_id
                sphere.header.stamp = rospy.Time.now()
                sphere.ns = "waypoint_point"
                sphere.id = i
                sphere.type = Marker.SPHERE
                sphere.action = Marker.ADD
                sphere.lifetime = rospy.Duration(0.5)
                
                # Position
                sphere.pose.position.x = waypoint[0]
                sphere.pose.position.y = waypoint[1]
                sphere.pose.position.z = 0.1
                sphere.pose.orientation.w = 1.0
                
                # Size
                size = 0.2 + 0.05 * i
                sphere.scale.x = size
                sphere.scale.y = size
                sphere.scale.z = size
                
                # Color: green to blue gradient
                sphere.color.r = 0.5 * (i / 4.0)
                sphere.color.g = 1.0 - (i / 4.0)
                sphere.color.b = 0.5 + 0.5 * (i / 4.0)
                sphere.color.a = 1.0
                
                marker_array.markers.append(sphere)
            
            # Publish
            self.waypoint_marker_pub.publish(marker_array)
            
            if self.debug and len(waypoints) > 0:
                rospy.logdebug(f"Published {len(waypoints)} waypoint markers")
            
        except Exception as e:
            rospy.logerr(f"❌ Failed to publish markers: {e}")
    
    def run(self, rate=10):
        """
        Main control loop
        
        Args:
            rate: Control loop frequency (Hz)
        """
        rate_obj = rospy.Rate(rate)
        
        print("Starting autonomous driving control loop...")
        print(f"Control frequency: {rate} Hz")
        print("Press Ctrl+C to stop")
        
        try:
            while not rospy.is_shutdown():
                # Create BEV map (dummy implementation)
                bev_map = self.create_bev_map()
                
                # Predict waypoints
                waypoints = self.predict_waypoints(bev_map, self.current_velocity)
                
                # Calculate steering angle from waypoints
                steering = self.waypoints_to_steering(waypoints)
                
                # Calculate throttle/brake
                accel, brake = self.waypoints_to_throttle()
                
                # Publish waypoint visualization
                self.publish_waypoint_markers(waypoints)
                
                # Publish control command
                self.publish_control_command(steering, accel, brake)
                
                # Detailed logging
                if self.debug:
                    rospy.loginfo(
                        f"[CTRL] V={self.current_velocity:.2f}m/s "
                        f"Steer={steering*180/np.pi:+.1f}° "
                        f"Accel={accel:.2f} Brake={brake:.2f} | "
                        f"WP: [{waypoints[0][0]:+.2f}m, {waypoints[0][1]:+.2f}m]"
                    )
                else:
                    rospy.loginfo(
                        f"Vel: {self.current_velocity:.2f}m/s | "
                        f"Target: {self.target_speed:.2f}m/s | "
                        f"Steering: {steering*180/np.pi:.1f}° | "
                        f"Accel: {accel:.3f}, Brake: {brake:.3f} | "
                        f"WP0: ({waypoints[0][0]:.2f}, {waypoints[0][1]:.2f})m"
                    )
                
                rate_obj.sleep()
        
        except KeyboardInterrupt:
            print("\nStopping autonomous driving control...")
        
        finally:
            # Stop the vehicle
            ctrl_cmd = CtrlCmd()
            ctrl_cmd.accel = 0.0
            ctrl_cmd.brake = 1.0
            ctrl_cmd.steering = 0.0
            self.ctrl_pub.publish(ctrl_cmd)
            print("Vehicle stopped safely")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous driving controller")
    parser.add_argument(
        '--checkpoint',
        type=str,
        default=str(_LBC_ROOT / 'checkpoints/pa_model_20260328_003844/checkpoint_best.pth'),
        help='Path to model checkpoint'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='cuda',
        help='Device to use (cuda or cpu)'
    )
    parser.add_argument(
        '--rate',
        type=int,
        default=10,
        help='Control loop frequency (Hz)'
    )
    parser.add_argument(
        '--target_speed',
        type=float,
        default=2.0,
        help='Target speed (m/s)'
    )
    
    args = parser.parse_args()
    
    # Create controller
    controller = AutonomousDrivingController(
        checkpoint_path=args.checkpoint,
        device=args.device
    )
    
    controller.target_speed = args.target_speed
    
    # Run control loop
    controller.run(rate=args.rate)


if __name__ == '__main__':
    main()
