from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

from robot_controller import RobotController
from magazine import Magazine
from tower import Tower
from jenga_piece import JengaPiece
class JengaRobotSystem:
    """Main system coordinator"""
    
    def __init__(self):
        # Initialize RoboDK connection
        self.rdk = Robolink()
        
        # Initialize subsystems
        self.robot_controller = RobotController(self.rdk)
        self.magazine = Magazine(self.rdk)
        self.tower = Tower(self.rdk)
        
        # Create Jenga pieces
        self.pieces = {i: JengaPiece(self.rdk, i) for i in range(1, 16)}
    
    def debug_tower_layout(self):
        """Debug method to visualize the dynamic tower layout"""
        print("\n=== DYNAMIC TOWER LAYOUT DEBUG ===")
        total_layers = self.tower.get_total_layers(len(self.pieces))
        
        for layer in range(total_layers):
            pieces_in_layer = self.tower.get_pieces_in_layer(layer, len(self.pieces))
            print(f"\nLayer {layer + 1} (0-based: {layer}):")
            print(f"  Pieces: {pieces_in_layer}")
            
            for piece_num in pieces_in_layer:
                x_offset, y_offset, z, rotation_z = self.tower.calculate_piece_position(piece_num)
                is_even = (layer % 2 == 0)
                orientation = "Along X-axis (horizontal)" if is_even else "Along Y-axis (vertical)"
                
                print(f"  Piece {piece_num}:")
                print(f"    Position: x_offset={x_offset:.1f}, y_offset={y_offset:.1f}, z={z:.1f}")
                print(f"    Rotation: {rotation_z:.2f} rad ({rotation_z * 180 / pi:.0f}°)")
                print(f"    Orientation: {orientation}")
        
        print("=====================================\n")
    
    def build_tower(self):
        """Execute the complete tower building sequence using dynamic formula"""
        print("Starting Jenga tower construction...")
        
        # Initialize robot
        self.robot_controller.initialize()
        
        # Generate magazine pickup positions
        pick_above_poses, pick_poses = self.magazine.get_pick_positions()
        
        # Calculate total layers needed
        total_layers = self.tower.get_total_layers(len(self.pieces))
        
        # Build tower layer by layer using dynamic calculation
        for layer in range(total_layers):
            layer_pieces = self.tower.get_pieces_in_layer(layer, len(self.pieces))
            print(f"Building layer {layer + 1} with pieces: {layer_pieces}")
            
            for piece_number in layer_pieces:
                # Pick piece from magazine
                self.robot_controller.pick_piece(piece_number, pick_above_poses, pick_poses)
                
                # Calculate placement position using dynamic formula
                place_above, place = self.tower.get_placement_pose(piece_number)
                
                # Place piece on tower
                self.robot_controller.place_piece(
                    self.pieces[piece_number], 
                    place_above, 
                    place, 
                    self.tower.frame
                )
        
        print("Jenga tower construction completed!")
        self.robot_controller.move_to_home()

def main():
    """Simple main function demonstrating the OOP system"""
    # Create and run the Jenga robot system
    system = JengaRobotSystem()
    system.build_tower()

if __name__ == "__main__":
    main()
