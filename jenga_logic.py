# jenga_logic.py

from jenga_piece import JengaPiece
from robot_controller import RobotController
from gripper import Gripper

def GrabAtPos(robot_ctrl: RobotController, piece: JengaPiece, gripper: Gripper, hover_height: float = 30):
    """
    Greift ein Jenga-Stück sicher:
    1. fährt über das Stück (hover)
    2. senkt sich ab
    3. greift
    4. hebt wieder an
    5. geht in Idle-Position
    """
    robot_ctrl.move_above(piece, z_offset=hover_height)
    robot_ctrl.move_exact(piece)
    gripper.close()
    robot_ctrl.move_above(piece, z_offset=hover_height)
    #robot_ctrl.move_to_idle()


def ReleaseAtPos(robot_ctrl: RobotController, piece: JengaPiece, gripper: Gripper, hover_height: float = 30):
    """
    Platziert ein Jenga-Stück sicher:
    1. fährt über die Zielposition (hover)
    2. senkt sich ab
    3. lässt los
    4. hebt wieder an
    5. geht in Idle-Position #brauchen wir nicht
    """
    robot_ctrl.move_above(piece, z_offset=hover_height)
    robot_ctrl.move_exact(piece)
    gripper.open()
    #robot_ctrl.move_above(piece, z_offset=hover_height)
    #robot_ctrl.move_to_idle()
