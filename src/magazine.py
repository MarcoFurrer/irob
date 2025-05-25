# magazine.py

import numpy as np
from jenga_piece import JengaPiece
from robodk import robomath

class Magazine:
    def __init__(self, name="MagazineFrame", rdk=None):
        """
        Magazine class that handles coordinate transformations properly
        """
        self.rdk = rdk
        self.frame = rdk.Item(name)
        
        if not self.frame.Valid():
            raise Exception(f"Magazine frame '{name}' not found in RoboDK")

        # Layout parameters (relative to magazine frame)
        # Adjusted for robot reachability - keep pieces close to robot workspace
        self.offset_x = 20  # Reduced from 40
        self.offset_y = 30  # Reduced from 60
        self.middle_offset = 10  # Reduced from 20
        self.max_pieces = 15

    def get_piece_position_local(self, piece: JengaPiece):
        """Returns position in magazine frame local coordinates"""
        if piece.number > self.max_pieces:
            raise ValueError(f"Piece {piece.number} exceeds maximum {self.max_pieces}")

        # Calculate position in magazine frame
        piece_index = piece.number - 1  # 0-based for calculation
        
        # Base position calculation - adjusted to be within robot reach
        base_x = -(10 - self.middle_offset) - piece.length / 2  # Much closer to frame origin
        base_y = 20 + piece.width / 2  # Positive Y to move closer to robot
        base_z = 150  # Much higher Z position

        if piece_index == 0:
            pos = [base_x, base_y, base_z]
        elif (piece_index + 1) % 2 == 0:
            pos = [base_x, base_y + (piece_index // 2) * piece.width, base_z]
        else:
            pos = [base_x - piece.length, base_y + (piece_index // 2) * piece.width, base_z]

        return [pos[0], pos[1], pos[2], 0, 0, 180]  # [x, y, z, rx, ry, rz] - Try 180° Z rotation
    
    def get_piece_position_absolute(self, piece: JengaPiece):
        """Returns position in robot base coordinates (absolute)"""
        # Get local coordinates in magazine frame
        local_coords = self.get_piece_position_local(piece)
        
        # Convert to pose matrix in magazine frame
        local_pose = robomath.xyzrpw_2_pose(local_coords)
        
        # Transform to absolute coordinates (robot base frame)
        magazine_frame_pose = self.frame.Pose()
        absolute_pose = magazine_frame_pose * local_pose
        
        return absolute_pose


if __name__ == "__main__":
    from robodk import robolink
    rdk = robolink.Robolink()
    magazine = Magazine(rdk=rdk)
    print(f"Magazine frame: {magazine.frame.Name()} at {magazine.frame.Pose()}")
        
        