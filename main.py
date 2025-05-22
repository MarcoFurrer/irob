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

     # ❗ Kollisionserkennung deaktivieren (nur zum Testen!)
    rdk.setCollisionActive(False)

    # Koordinatenursprünge
    magazine_frame = [330, -100, -300]
    tower_frame = [120, 200, -300]

    # Objekte erzeugen
    magazine = Magazine(magazine_frame, rdk=rdk, name="MagazineFrame")
    tower = Tower(tower_frame, rdk=rdk, name="TowerFrame")
    robot = RobotController(rdk)
    gripper = Gripper(rdk)
    
    jenga_pieces = [JengaPiece(rdk, i) for i in range(1, 16)]
    
    robot.move_to_start()
    
    for piece in jenga_pieces:
        robot.GrabAtPos(piece, gripper)
        robot.ReleaseAtPos(piece, gripper)
        
    robot.move_to_start()

if __name__ == "__main__":
    main()

