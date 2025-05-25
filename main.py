from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

from robot_controller import RobotController
from magazine import Magazine
from tower import Tower
from jenga_piece_collection import JengaPiece, JengaPieceCollection


class JengaRobotSystem:
    """Object-oriented Jenga robot system"""
    
    def __init__(self, piece_count=15):
        """Initialize the complete Jenga robot system"""
        # Create RoboDK connection
        self.rdk = Robolink()
        
        # Initialize subsystems
        self.robot_controller = RobotController(self.rdk)
        self.magazine = Magazine(self.rdk)
        self.tower = Tower(self.rdk)
        
        # Create piece collection (more OOP than list)
        self.pieces = JengaPieceCollection(self.rdk, piece_count)
        
        print(f"Initialized Jenga robot system with {len(self.pieces)} pieces")
    
    def initialize_system(self):
        """Initialize the robot and prepare for operation"""
        print("Initializing robot system...")
        self.robot_controller.initialize()
        
        # Generate magazine pickup positions
        self.pick_above_poses, self.pick_poses = self.magazine.get_pick_positions()
        print("Magazine pickup positions generated")
    
    def build_tower_simple(self):
        """Simple approach: process pieces in order"""
        print("Starting Jenga tower construction (simple approach)...")
        
        self.initialize_system()
        
        # Process each piece in order using OOP approach
        for piece in self.pieces:  # Uses __iter__ method of JengaPieceCollection
            print(f"Processing {piece}")
            
            # Pick piece from magazine
            self.robot_controller.pick_piece(piece, self.pick_above_poses, self.pick_poses)
            
            # Calculate placement position using the piece object
            place_above, place = self.tower.get_placement_pose_for_piece(piece)
            
            # Place piece on tower
            self.robot_controller.place_piece(piece, place_above, place, self.tower.frame)
        
        print("Jenga tower construction completed!")
        self.robot_controller.move_to_home()
    
    def build_tower_by_layers(self):
        """Layer-by-layer approach: more structured building"""
        print("Starting Jenga tower construction (layer-by-layer approach)...")
        
        self.initialize_system()
        
        # Calculate total layers needed
        total_layers = self.tower.get_total_layers(len(self.pieces))
        
        # Build tower layer by layer using OOP approach
        for layer in range(total_layers):
            # Get pieces for this layer as objects (not just numbers)
            layer_pieces = self.tower.get_pieces_in_layer_objects(layer, self.pieces)
            
            print(f"Building layer {layer + 1} with pieces: {[str(p) for p in layer_pieces]}")
            
            for piece in layer_pieces:
                print(f"Processing {piece} for layer {layer + 1}")
                
                # Use the new integrated move_piece method
                self.robot_controller.move_piece(
                    piece, 
                    self.magazine, 
                    self.tower, 
                    self.pick_above_poses, 
                    self.pick_poses
                )
        
        print("Jenga tower construction completed!")
        self.robot_controller.move_to_home()
    
    def debug_piece_info(self):
        """Debug method to show piece information"""
        print("\n=== PIECE COLLECTION DEBUG ===")
        print(f"Total pieces: {len(self.pieces)}")
        print(f"Piece count: {self.pieces.get_piece_count()}")
        
        print("\nAll pieces:")
        for piece in self.pieces:
            layer = self.tower.get_layer_for_piece(piece)
            print(f"  {piece} -> Layer {layer + 1}")
        
        print("\nPieces by layer:")
        total_layers = self.tower.get_total_layers(len(self.pieces))
        for layer in range(total_layers):
            layer_pieces = self.tower.get_pieces_in_layer_objects(layer, self.pieces)
            print(f"  Layer {layer + 1}: {[str(p) for p in layer_pieces]}")
        print("===============================\n")


def main():
    """Main function with improved OOP design"""
    import sys
    
    try:
        # Create the complete system
        system = JengaRobotSystem()
        
        # Check for different modes
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == "debug":
                system.debug_piece_info()
            elif mode == "simple":
                system.build_tower_simple()
            elif mode == "layers":
                system.build_tower_by_layers()
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: debug, simple, layers")
        else:
            # Default: layer-by-layer approach
            system.build_tower_by_layers()
            
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
