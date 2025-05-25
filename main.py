from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

from robot_controller import RobotController
from magazine import Magazine
from tower import Tower
from jenga_piece import JengaPiece



def main():
    """Simple main function demonstrating the OOP system"""
    # Create and run the Jenga robot system
    rdk = Robolink()
    
    # Initialize subsystems
    robot_controller = RobotController(rdk)
    magazine = Magazine(rdk)
    tower = Tower(rdk)
    
    # Create Jenga pieces
    pieces = [JengaPiece(rdk, i) for i in range(1, 16)]
    print("Starting Jenga tower construction...")
        
    # Initialize robot
    robot_controller.initialize()
    
    # Generate magazine pickup positions
    pick_above_poses, pick_poses = magazine.get_pick_positions()
    
    # Calculate total layers needed
    total_layers = tower.get_total_layers(len(pieces))
    
    # Build tower layer by layer using dynamic calculation
    for layer in range(total_layers):
        layer_pieces = tower.get_pieces_in_layer(layer, len(pieces))
        print(f"Building layer {layer + 1} with pieces: {layer_pieces}")
        
        for piece_number in layer_pieces:
            # Pick piece from magazine
            robot_controller.pick_piece(piece_number, pick_above_poses, pick_poses)
            
            # Calculate placement position using dynamic formula
            place_above, place = tower.get_placement_pose(piece_number)
            
            # Place piece on tower
            robot_controller.place_piece(
                pieces[piece_number], 
                place_above, 
                place, 
                tower.frame
            )
    
    print("Jenga tower construction completed!")
    robot_controller.move_to_home()

if __name__ == "__main__":
    main()
