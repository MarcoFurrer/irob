# robot_controller.py

import time
import numpy as np
from robodk import xyzrpw_2_pose
from robodk import robolink
from jenga_piece import JengaPiece

class RobotController:
    def __init__(self, rdk, robot_name="Staubli TX2-90L"):
        self.rdk = rdk
        self.robot = rdk.Item(robot_name, robolink.ITEM_TYPE_ROBOT)

        # Targets aus RoboDK laden
        self.target_start = rdk.Item("start_position", robolink.ITEM_TYPE_TARGET)
        self.target_idle = rdk.Item("idle_position", robolink.ITEM_TYPE_TARGET)
        self.target_home = rdk.Item("home_position", robolink.ITEM_TYPE_TARGET)

        # Fehler prüfen
        if not self.target_start.Valid():
            raise Exception("Target 'start_position' wurde in RoboDK nicht gefunden.")
        if not self.target_idle.Valid():
            raise Exception("Target 'idle_position' wurde in RoboDK nicht gefunden.")
        if not self.target_home.Valid():
            raise Exception("Target 'home_position' wurde in RoboDK nicht gefunden.")

    def move_to_pose(self, pose):
        """Bewegt den Roboter zu einer gegebenen Pose (6-Werte-Liste)"""
        self.robot.MoveJ(xyzrpw_2_pose(pose))
        
    def move_to_start(self):
        """Bewegt zu RoboDK-Target 'start_position'"""
        self.robot.MoveJ(self.target_start)

    def move_to_idle(self):
        """Bewegt zu RoboDK-Target 'idle_position'"""
        self.robot.MoveJ(self.target_idle)

    def move_to_home(self):
        """Bewegt zu RoboDK-Target 'home_position'"""
        self.robot.MoveJ(self.target_home)

    def move_above(self, piece: JengaPiece, z_offset=30):
        """Fährt über die Zielposition (z + offset)"""
        pos = piece.position.copy()
        pos[2] += z_offset
        pose = pos + piece.orientation
        self.move_to_pose(pose)

    def move_exact(self, piece: JengaPiece):
        """Fährt exakt zur Position des Steins"""
        pose = piece.get_pose()
        self.move_to_pose(pose)
