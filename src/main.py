# main.py

import time
from robodk import robolink

from magazine import Magazine
from jenga_piece import JengaPiece
from tower import Tower
from robot_controller import RobotController
from gripper import Gripper


def main():
    # Initialisierung RoboDK API
    rdk = robolink.Robolink()
    rdk.setSimulationSpeed(0.1)

     # ❗ Kollisionserkennung deaktivieren (nur zum Testen!)
    rdk.setCollisionActive(False)

    # Initialize frame-aware objects
    magazine = Magazine(name="MagazineFrame", rdk=rdk)
    tower = Tower(name="TowerFrame", rdk=rdk)
    robot = RobotController(rdk)
    gripper = Gripper(rdk)
    
    jenga_pieces = [JengaPiece(rdk, i) for i in range(1, 16)]
    
    robot.move_to_home()
    
    # Frame-aware pick and place sequence
    for piece in jenga_pieces:
        print(f"Processing piece {piece.number}:")
        print(f"  1. Grabbing from magazine frame...")
        robot.grab_from_magazine(piece, magazine, gripper)
        
        print(f"  2. Placing on tower frame...")
        robot.place_on_tower(piece, tower, gripper)
        
        print(f"  3. Returning to home...")
        robot.move_to_home()
        print(f"Piece {piece.number} completed!\n")
    
    print("All pieces moved from magazine to tower!")
    robot.move_to_home()

def debug_mode():
    """Debug mode to verify frame calculations"""
    rdk = robolink.Robolink()
    
    magazine = Magazine(name="MagazineFrame", rdk=rdk)
    tower = Tower(name="TowerFrame", rdk=rdk)
    robot = RobotController(rdk)
    
    # Test with first piece
    test_piece = JengaPiece(rdk, 1)
    
    # Debug frame information
    robot.debug_frames_info(magazine, tower, test_piece)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        debug_mode()
    else:
        main()

