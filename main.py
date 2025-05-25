from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

from robot_controller import RobotController
from magazine import Magazine
from tower import Tower
from jenga_piece_collection import JengaPiece, JengaPieceCollection


def main():
    """Main function for Jenga tower construction"""
    try:
        # Create RoboDK connection
        rdk = Robolink()
        
        # Initialize subsystems
        robot_controller = RobotController(rdk)
        magazine = Magazine(rdk)
        tower = Tower(rdk)
        
        # Create piece collection
        pieces = JengaPieceCollection(rdk, 15)
        print(f"Initialized Jenga robot system with {len(pieces)} pieces")
        
        # Initialize robot system
        print("Initializing robot system...")
        robot_controller.initialize()
        
        # Generate magazine pickup positions
        pick_above_poses, pick_poses = magazine.get_pick_positions()
        print("Magazine pickup positions generated")
        
        # Start tower construction
        print("Starting Jenga tower construction...")
        
        # Process each piece in order using clean iteration
        for piece in pieces:  # Uses __iter__ method of JengaPieceCollection
            print(f"Processing {piece} for layer {tower.get_layer_for_piece(piece)+1}")
            
            # Move piece from magazine to tower
            robot_controller.move_piece(
                piece, 
                magazine, 
                tower, 
                pick_above_poses, 
                pick_poses
            )
        
        print("Jenga tower construction completed!")
        robot_controller.move_to_home()
            
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
