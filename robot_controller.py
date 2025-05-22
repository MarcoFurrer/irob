# robot_controller.py

import time
import numpy as np
from robodk import xyzrpw_2_pose
from robodk import robolink
from jenga_piece import JengaPiece
from robodk import pose_2_xyzrpw
from gripper import Gripper


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
        print(self.target_home)
        self.robot.MoveJ(self.target_home)

    def move_above(self, piece: JengaPiece, z_offset=30):
        """Fährt über die Zielposition (z + offset)"""
        pos = pose_2_xyzrpw(piece.piece.Pose())
        print(
            f"[MOVE_ABOVE] Bewege Roboter über die Position {pos} des Steins mit z_offset={z_offset}."
        )
        self.robot.MoveJ(
            [
                pos[0],  # X from original pose
                pos[1],  # Y from original pose
                pos[2] + z_offset,  # Z + offset
                piece.orientation[0],  # RX from orientation
                piece.orientation[1],  # RY from orientation
                piece.orientation[2],  # RZ from orientation
            ]
        )

    def move_exact(self, piece: JengaPiece):
        """Fährt exakt zur Position des Steins"""
        pos = pose_2_xyzrpw(piece.piece.Pose())
        print(f"[MOVE_EXACT] Bewege Roboter mit Stein {piece.number} nach {pos}.")
        self.robot.MoveJ(
            [
                pos[0],  # X from original pose
                pos[1],  # Y from original pose
                pos[2],  # Z + offset
                piece.orientation[0],  # RX from orientation
                piece.orientation[1],  # RY from orientation
                piece.orientation[2],  # RZ from orientation
            ]
        )
        

    def GrabAtPos(
        self, piece: JengaPiece, gripper: Gripper, hover_height: float = 30.0
    ):
        """
        Greift ein Jenga-Stück sicher:
        1. fährt über das Stück (hover)
        2. senkt sich ab
        3. greift
        4. hebt wieder an
        5. geht in Idle-Position
        """
        self.move_above(piece, z_offset=hover_height)
        self.move_exact(piece)
        gripper.close()
        self.move_above(piece, z_offset=hover_height)
        self.move_to_idle()

    def ReleaseAtPos(
        self, piece: JengaPiece, gripper: Gripper, hover_height: float = 30.0
    ):
        """
        Platziert ein Jenga-Stück sicher:
        1. fährt über die Zielposition (hover)
        2. senkt sich ab
        3. lässt los
        4. hebt wieder an
        5. geht in Idle-Position
        """
        self.move_above(piece, z_offset=hover_height)
        self.move_exact(piece)
        gripper.open()
        self.move_above(piece, z_offset=hover_height)
        self.move_to_idle()
