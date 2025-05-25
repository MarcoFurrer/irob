from jenga_piece import JengaPiece
import numpy as np
from robodk import robomath

class Tower:
    def __init__(self, name="TowerFrame", rdk=None):
        """
        Tower class that handles coordinate transformations properly
        """
        self.rdk = rdk
        self.frame = rdk.Item(name)
        
        if not self.frame.Valid():
            raise Exception(f"Tower frame '{name}' not found in RoboDK")

        # Offset relative to tower frame origin
        self.offset_x = 70.711 
        self.offset_y = 70.711
        self.offset_z = 0
        self.max_pieces = 15

    def get_next_target_local(self, piece: JengaPiece):
        """Returns target position in tower frame local coordinates"""
        if piece.number >= self.max_pieces:
            raise StopIteration("Tower is full.")

        layer = piece.number // 3  # Layer (0-based)
        index_in_layer = piece.number % 3
        is_even_layer = (layer % 2 == 0)

        return [
            index_in_layer * piece.width + self.offset_x if is_even_layer else self.offset_x + piece.width/2,
            self.offset_y if is_even_layer else self.offset_y + index_in_layer * piece.width, 
            self.offset_z + layer * piece.height, 
            0, 
            0, 
            0 if is_even_layer else np.pi / 2
        ]
    
    def get_next_target_absolute(self, piece: JengaPiece):
        """Returns target position in robot base coordinates (absolute)"""
        # Get local coordinates in tower frame
        local_coords = self.get_next_target_local(piece)
        
        # Convert to pose matrix in tower frame
        local_pose = robomath.xyzrpw_2_pose(local_coords)
        
        # Transform to absolute coordinates (robot base frame)
        tower_frame_pose = self.frame.Pose()
        absolute_pose = tower_frame_pose * local_pose
        
        return absolute_pose
    
    def get_next_target(self, piece: JengaPiece):
        """Legacy method - returns absolute pose"""
        return self.get_next_target_absolute(piece)
        
if __name__ == "__main__":
    from robodk import robolink
    rdk = robolink.Robolink()
    tower = Tower(rdk=rdk)
    jenga_pieces = [JengaPiece(rdk, i) for i in range(15)]
    for piece in jenga_pieces:
        print(f"Piece {piece.number} target position: {tower.get_next_target(piece)}")
    print(f"Tower frame: {tower.frame.Name()} at {tower.frame.Pose()}")