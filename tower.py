from jenga_constants import JengaConstants   
from robodk.robomath import *

class Tower:
    """Handles tower frame and piece placement using dynamic formula"""
    
    def __init__(self, rdk, frame_name="TowerFrame"):
        self.rdk = rdk
        self.frame = rdk.Item(frame_name)
        
        if not self.frame.Valid():
            raise Exception(f"Tower frame '{frame_name}' not found in RoboDK")
        
        # Tower base position relative to frame origin
        self.base_x = 0
        self.base_y = 70
        self.base_z = -5
    
    def calculate_piece_position(self, piece_number):
        """
        Calculate position for a piece using dynamic formula
        Returns: (x_offset, y_offset, z, rotation_z)
        
        Jenga tower logic:
        - Even layers (0,2,4...): pieces run along X-axis, spaced in Y direction
        - Odd layers (1,3,5...): pieces run along Y-axis, spaced in X direction
        - When rotated, the LENGTH becomes the spacing distance between pieces
        """
        # Convert to 0-based indexing for calculations
        piece_index = piece_number - 1
        
        # Calculate layer (0-based) and position within layer
        layer = piece_index // 3
        index_in_layer = piece_index % 3
        
        # Determine if this is an even or odd layer (alternating orientations)
        is_even_layer = (layer % 2 == 0)
        
        # Calculate Z position
        z = (layer + 1) * JengaConstants.HEIGHT - self.base_z
        
        if is_even_layer:
            # Even layers: pieces aligned along X-axis (horizontally)
            # When rotated 90°, pieces are spaced by their WIDTH in the Y direction
            x_offset = 0
            y_offset = (index_in_layer - 1) * JengaConstants.WIDTH  # -WIDTH, 0, +WIDTH
            rotation_z = pi/2  # 90 degrees rotation
        else:
            # Odd layers: pieces aligned along Y-axis (vertically)  
            # When rotated 180°, pieces are spaced by their WIDTH in the X direction
            x_offset = (index_in_layer - 1) * JengaConstants.WIDTH  # -WIDTH, 0, +WIDTH
            y_offset = 0
            rotation_z = 0  # 0 degrees rotation (was pi, but 0 is more natural)
        
        return x_offset, y_offset, z, rotation_z
    
    def get_placement_pose(self, piece_number, hover_height=30):
        """Calculate placement pose for a piece using dynamic formula"""
        x_offset, y_offset, z, rotation_z = self.calculate_piece_position(piece_number)
        
        # Calculate absolute position
        abs_x = self.base_x + x_offset
        abs_y = self.base_y + y_offset
        abs_z = z
        
        # Create poses
        place_above = (
            self.frame.Pose() * 
            transl(abs_x, abs_y, abs_z + hover_height) * 
            rotz(rotation_z) * 
            rotx(pi)
        )
        
        place = (
            self.frame.Pose() * 
            transl(abs_x, abs_y, abs_z) * 
            rotz(rotation_z) * 
            rotx(pi)
        )
        
        return place_above, place
    
    def get_total_layers(self, total_pieces=15):
        """Calculate total number of layers needed"""
        return (total_pieces - 1) // 3 + 1
    
    def get_pieces_in_layer(self, layer, total_pieces=15):
        """Get list of piece numbers in a specific layer (0-based)"""
        pieces_in_layer = []
        for piece_num in range(1, total_pieces + 1):
            piece_layer = (piece_num - 1) // 3
            if piece_layer == layer:
                pieces_in_layer.append(piece_num)
        return pieces_in_layer
    
    def get_pieces_in_layer_objects(self, layer, piece_collection):
        """Get list of JengaPiece objects in a specific layer (0-based)"""
        piece_numbers = self.get_pieces_in_layer(layer, piece_collection.get_piece_count())
        return piece_collection.get_pieces_by_numbers(piece_numbers)
    
    def get_layer_for_piece(self, piece):
        """Get the layer number (0-based) for a given piece"""
        if hasattr(piece, 'number'):
            piece_number = piece.number
        else:
            piece_number = piece
        return (piece_number - 1) // 3
    
    def get_placement_pose_for_piece(self, piece, hover_height=30):
        """Calculate placement pose for a JengaPiece object"""
        piece_number = piece.number if hasattr(piece, 'number') else piece
        return self.get_placement_pose(piece_number, hover_height)