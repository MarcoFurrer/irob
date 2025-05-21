# main.py

import time
from robodk import robolink

from magazine import Magazine
from tower import Tower
from robot_controller import RobotController
from gripper import Gripper
from jenga_logic import GrabAtPos, ReleaseAtPos

def main():
    # Initialisierung RoboDK API
    rdk = robolink.Robolink()

     # ❗ Kollisionserkennung deaktivieren (nur zum Testen!)
    rdk.setCollisionActive(False)

    # Koordinatenursprünge
    magazine_frame = [330, -100, -300]
    tower_frame = [120, 200, -300]

    # Objekte erzeugen
    magazine = Magazine(magazine_frame)
    tower = Tower(tower_frame)
    robot = RobotController(rdk)
    gripper = Gripper(rdk)

    # Startposition anfahren
    robot.move_to_start()
    robot.move_to_idle()

    # 15 Steine verarbeiten
    for _ in range(15):
        source_piece = magazine.get_next_piece()
        target_piece = tower.get_next_target()

        GrabAtPos(robot, source_piece, gripper)
        ReleaseAtPos(robot, target_piece, gripper)

    # Abschluss
    robot.move_to_start()

if __name__ == "__main__":
    main()

