import time
import numpy as np
from robodk import robolink
from robodk import robomath
from jenga_piece_collection import JengaPiece
from gripper import Gripper
from tower import Tower
from magazine import Magazine
from RTS import RTS


class RobotController:
    def __init__(self, rdk, robot_name="Staubli TX2-40"):
        self.rdk = rdk
        self.rts = RTS(self.rdk,
                       rdk.Item("Staubli TX2-40", robolink.ITEM_TYPE_ROBOT),
                       rdk.Item("AROB_LWS_VakuumGreifer_14", robolink.ITEM_TYPE_TOOL)
                       )
        self.rts.addConnection('dVacuum', '98FE10BA-0446-4B8A-A8CF-35B98F42725A', 'dio')
        self.rts.setGripperConnection('dVacuum')
        self.rts.addConnection('dVaccumSensor', '98FE10BA-0446-4B8A-A8CF-35B98F42725B', 'aio')

        # Targets aus RoboDK laden
        self.target_home = rdk.Item("home", robolink.ITEM_TYPE_TARGET)

        # Fehler prüfen
        if not self.target_home.Valid():
            raise Exception("Target 'home' wurde in RoboDK nicht gefunden.")

    def move_to_pose(self, pose):
        """Bewegt den Roboter zu einer gegebenen Pose (4x4 Matrix oder 6-Werte-Liste)"""
        if isinstance(pose, list) and len(pose) == 6:
            pose = robomath.xyzrpw_2_pose(pose)
        self.rts.MoveJ(pose)

    def move_to_home(self):
        """Bewegt zu RoboDK-Target 'home_position'"""
        print(f"[HOME] Moving to home position")
        self.rts.MoveJ(self.target_home)

    def grab_from_magazine(self, piece: JengaPiece, magazine: Magazine, gripper: Gripper, hover_height: float = 30.0):
        """
        Greift ein Jenga-Stück aus dem Magazin:
        1. fährt über das Stück im Magazin (hover)
        2. senkt sich ab
        3. greift
        4. hebt wieder an
        """
        print(f"[GRAB] Grabbing piece {piece.number} from magazine")
        
        # Get absolute position of piece in magazine
        piece_pose = magazine.get_piece_position_absolute(piece)
        
        # Create hover position (above the piece)
        piece_coords = robomath.pose_2_xyzrpw(piece_pose)
        hover_coords = piece_coords.copy()
        hover_coords[2] += hover_height  # Add Z offset
        hover_pose = robomath.xyzrpw_2_pose(hover_coords)
        
        # Debug output
        print(f"[DEBUG] Piece position: {piece_coords}")
        print(f"[DEBUG] Hover position: {robomath.pose_2_xyzrpw(hover_pose)}")
        
        # Move above piece
        print(f"[GRAB] Moving above piece {piece.number} in magazine")
        self.rts.MoveJ(hover_pose)
        
        # Move to piece
        print(f"[GRAB] Moving to piece {piece.number}")
        self.rts.MoveL(piece_pose)
        
        # Grab piece
        gripper.close()
        print(f"[GRAB] Gripper closed on piece {piece.number}")
        
        # Move back up
        self.rts.MoveL(hover_pose)

    def place_on_tower(self, piece: JengaPiece, tower: Tower, gripper: Gripper, hover_height: float = 30.0):
        """
        Platziert ein Jenga-Stück auf dem Turm:
        1. fährt über die Zielposition im Turm (hover)
        2. senkt sich ab
        3. lässt los
        4. hebt wieder an
        """
        print(f"[PLACE] Placing piece {piece.number} on tower")
        
        # Get absolute position for tower placement
        target_pose = tower.get_next_target_absolute(piece)
        
        # Create hover position (above the target)
        target_coords = robomath.pose_2_xyzrpw(target_pose)
        hover_coords = target_coords.copy()
        hover_coords[2] += hover_height  # Add Z offset
        hover_pose = robomath.xyzrpw_2_pose(hover_coords)
        
        # Debug information
        print(f"[DEBUG] Tower target position: {target_coords}")
        print(f"[DEBUG] Tower hover position: {hover_coords}")
        
        # Move above target position
        print(f"[PLACE] Moving above tower position for piece {piece.number}")
        self.robot.MoveJ(hover_pose)
        
        # Move to target position
        print(f"[PLACE] Moving to tower position")
        self.rts.MoveL(target_pose)
        
        # Release piece
        gripper.open()
        print(f"[PLACE] Released piece {piece.number}")
        
        # Move back up
        self.rts.MoveL(hover_pose)

    # Legacy methods for backward compatibility
    def move_above(self, piece: JengaPiece, z_offset=30):
        """Legacy: Fährt über die aktuelle Position des Stücks"""
        pos = robomath.pose_2_xyzrpw(piece.piece.Pose())
        hover_coords = pos.copy()
        hover_coords[2] += z_offset
        hover_pose = robomath.xyzrpw_2_pose(hover_coords)
        self.rts.MoveJ(hover_pose)

    def move_exact(self, piece: JengaPiece):
        """Legacy: Fährt exakt zur aktuellen Position des Steins"""
        piece_pose = piece.piece.Pose()
        self.robot.MoveJ(piece_pose)

    def GrabAtPos(self, piece: JengaPiece, gripper: Gripper, hover_height: float = 30.0):
        """Legacy method - use grab_from_magazine instead"""
        self.move_above(piece, z_offset=hover_height)
        self.move_exact(piece)
        gripper.close()
        self.move_above(piece, z_offset=hover_height)

    def ReleaseAtPos(self, piece: JengaPiece, gripper: Gripper, hover_height: float = 30.0):
        """Legacy method - use place_on_tower instead"""
        tower = Tower(rdk=self.rdk)
        target_pose = tower.get_next_target_absolute(piece)
        self.robot.MoveJ(target_pose)
        gripper.open()
        
        self.move_to_home()
        
    def debug_frames_info(self, magazine: Magazine, tower: Tower, piece: JengaPiece):
        """Debug function to verify frame transformations"""
        print("\n=== FRAME DEBUG INFO ===")
        
        # Robot base info
        robot_base = self.rdk.Item("Staubli TX2-40 Base")
        robot_pose = robot_base.Pose()
        print(f"Robot Base Frame: {robomath.pose_2_xyzrpw(robot_pose)}")
        
        # Magazine frame info
        mag_pose = magazine.frame.Pose()
        print(f"Magazine Frame: {robomath.pose_2_xyzrpw(mag_pose)}")
        
        # Tower frame info
        tower_pose = tower.frame.Pose()
        print(f"Tower Frame: {robomath.pose_2_xyzrpw(tower_pose)}")
        
        # Example piece positions
        mag_local = magazine.get_piece_position_local(piece)
        mag_absolute = magazine.get_piece_position_absolute(piece)
        print(f"Piece {piece.number} in Magazine (local): {robomath.pose_2_xyzrpw(robomath.xyzrpw_2_pose(mag_local))}")
        print(f"Piece {piece.number} in Magazine (absolute): {robomath.pose_2_xyzrpw(mag_absolute)}")
        
        tower_local = tower.get_next_target_local(piece)
        tower_absolute = tower.get_next_target_absolute(piece)
        print(f"Piece {piece.number} in Tower (local): {tower_local}")
        print(f"Piece {piece.number} in Tower (absolute): {robomath.pose_2_xyzrpw(tower_absolute)}")
        
        print("========================\n")

if __name__ == "__main__":
    rdk = robolink.Robolink()
    robot = RobotController(rdk)
    gripper = Gripper(rdk)
    
    # Beispiel Jenga-Stück
    piece = JengaPiece(rdk, 1)
    

    robot.GrabAtPos(piece, gripper)
    time.sleep(2)  # Simuliere eine Pause
    robot.ReleaseAtPos(piece, gripper)
