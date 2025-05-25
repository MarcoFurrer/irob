# JengaRobotSystem.py
# Object-oriented implementation of the working Jenga robot system

from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *
from RTS import RTS


class JengaConstants:
    """Constants for the Jenga robot system"""
    # Magazine layout
    OFFSET_X = 72.5
    OFFSET_Y_FIRST_ROW = 97.5
    OFFSET_Y_SECOND_ROW = 172.5
    Z_PICK = 15
    Z_OFFSET = 15
    COUNT_FIRST_ROW = 8
    COUNT_SECOND_ROW = 7
    
    # Jenga piece dimensions
    LENGTH = 75
    WIDTH = 25.5
    HEIGHT = 15
    
    # Tower placement
    OFFSET_TOOL = 0
    X_TOWER = 70
    Y_TOWER = 70
    
    # Robot positions
    T_HOME = [0, 50, 50, 0, 60, 0]
    T_START = [0, 0, 90, 0, 90, 0]


class JengaPiece:
    """Represents a single Jenga piece"""
    
    def __init__(self, rdk, number):
        self.number = number
        self.rdk = rdk
        self.piece = rdk.Item(f"Jengastuck {number}")
        
        if not self.piece.Valid():
            raise Exception(f"Jenga piece {number} not found in RoboDK")
    
    def attach_to_frame(self, frame):
        """Attach this piece to a specific frame (used for tower building)"""
        self.piece.setParentStatic(frame)


class VacuumGripper:
    """Handles vacuum gripper operations using RTS"""
    
    def __init__(self, rts):
        self.rts = rts
    
    def grab(self):
        """Activate vacuum to grab piece"""
        self.rts.setVacuum(1, "dVacuum")
    
    def release(self):
        """Deactivate vacuum to release piece"""
        self.rts.setVacuum(0, "dVacuum")


class Magazine:
    """Handles magazine frame and piece positioning"""
    
    def __init__(self, rdk, frame_name="MagazinFrame"):
        self.rdk = rdk
        self.frame = rdk.Item(frame_name)
        
        if not self.frame.Valid():
            raise Exception(f"Magazine frame '{frame_name}' not found in RoboDK")
    
    def get_pick_positions(self):
        """Generate all pickup positions for pieces in magazine"""
        pick_above, pick = {}, {}
        
        # First row (pieces 1-8)
        for i in range(JengaConstants.COUNT_FIRST_ROW):
            piece_num = i + 1
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_FIRST_ROW, JengaConstants.Z_OFFSET) * 
                rotx(pi)
            )
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_FIRST_ROW, JengaConstants.Z_PICK) * 
                rotx(pi)
            )
        
        # Second row (pieces 9-15)
        for i in range(JengaConstants.COUNT_SECOND_ROW):
            piece_num = i + 9
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_SECOND_ROW, JengaConstants.Z_OFFSET) * 
                rotx(pi)
            )
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_SECOND_ROW, JengaConstants.Z_PICK) * 
                rotx(pi)
            )
        
        return pick_above, pick


class Tower:
    """Handles tower frame and piece placement"""
    
    def __init__(self, rdk, frame_name="TowerFrame"):
        self.rdk = rdk
        self.frame = rdk.Item(frame_name)
        
        if not self.frame.Valid():
            raise Exception(f"Tower frame '{frame_name}' not found in RoboDK")
    
    def get_layer_configuration(self):
        """Define the tower layer configuration"""
        return [
            {
                "blocks": [1, 2, 3], 
                "x_offsets": [0, 0, 0], 
                "y_offsets": [JengaConstants.WIDTH, 0, -JengaConstants.WIDTH], 
                "rz": pi/2
            },
            {
                "blocks": [4, 5, 6], 
                "x_offsets": [JengaConstants.WIDTH, 0, -JengaConstants.WIDTH], 
                "y_offsets": [0, 0, 0], 
                "rz": pi
            },
            {
                "blocks": [7, 8, 9], 
                "x_offsets": [0, 0, 0], 
                "y_offsets": [JengaConstants.WIDTH, 0, -JengaConstants.WIDTH], 
                "rz": pi/2
            },
            {
                "blocks": [10, 11, 12], 
                "x_offsets": [JengaConstants.WIDTH, 0, -JengaConstants.WIDTH], 
                "y_offsets": [0, 0, 0], 
                "rz": pi
            },
            {
                "blocks": [13, 14, 15], 
                "x_offsets": [0, 0, 0], 
                "y_offsets": [JengaConstants.WIDTH, 0, -JengaConstants.WIDTH], 
                "rz": pi/2
            }
        ]
    
    def get_placement_pose(self, layer, position_index, x_offset, y_offset, rz):
        """Calculate placement pose for a piece"""
        z = (layer + 1) * JengaConstants.HEIGHT - JengaConstants.OFFSET_TOOL
        
        place_above = (
            self.frame.Pose() * 
            transl(JengaConstants.X_TOWER + x_offset, JengaConstants.Y_TOWER + y_offset, z + 30) * 
            rotz(rz) * 
            rotx(pi)
        )
        
        place = (
            self.frame.Pose() * 
            transl(JengaConstants.X_TOWER + x_offset, JengaConstants.Y_TOWER + y_offset, z) * 
            rotz(rz) * 
            rotx(pi)
        )
        
        return place_above, place


class RobotController:
    """Main robot controller handling movement and coordination"""
    
    def __init__(self, rdk):
        self.rdk = rdk
        
        # Initialize robot and tool
        self.robot = rdk.Item('Staubli TX2-40')
        self.tool = rdk.Item('AROB_LWS_VakuumGreifer_14')
        self.world_frame = rdk.Item("World")
        
        # Initialize RTS system
        self.rts = RTS(rdk, self.robot, self.tool)
        self.rts.addConnection('dVacuum', '98FE10BA-0446-4B8A-A8CF-35B98F42725A', 'dio')
        self.rts.setGripperConnection('dVacuum')
        self.rts.addConnection('dVaccumSensor', '98FE10BA-0446-4B8A-A8CF-35B98F42725B', 'aio')
        
        # Initialize gripper
        self.gripper = VacuumGripper(self.rts)
        
        # Validate components
        if not self.robot.Valid():
            raise Exception("Robot 'Staubli TX2-40' not found in RoboDK")
        if not self.tool.Valid():
            raise Exception("Tool 'AROB_LWS_VakuumGreifer_14' not found in RoboDK")
    
    def initialize(self):
        """Initialize robot to start position"""
        self.robot.setJoints(JengaConstants.T_START)
        self.robot.setPoseFrame(self.world_frame)
        self.robot.setSpeed(50, 50, 50, 75)
    
    def move_to_home(self):
        """Move robot to home position"""
        self.robot.MoveJ(JengaConstants.T_HOME)
    
    def pick_piece(self, piece_number, pick_above_poses, pick_poses, speed=10):
        """Pick up a piece from the magazine"""
        print(f"Picking up piece {piece_number}")
        
        # Move to home first
        self.move_to_home()
        
        # Move above piece
        self.robot.MoveJ(pick_above_poses[f"Jenga{piece_number}above"])
        
        # Slow movement for precision
        self.robot.setSpeed(speed)
        
        # Move to piece and grab
        self.robot.MoveL(pick_poses[f"Jenga{piece_number}"])
        self.gripper.grab()
        
        # Move back up
        self.robot.MoveL(pick_above_poses[f"Jenga{piece_number}above"])
        
        # Reset speed
        self.robot.setSpeed(50)
    
    def place_piece(self, piece: JengaPiece, place_above_pose, place_pose, tower_frame, speed=10):
        """Place a piece on the tower"""
        print(f"Placing piece {piece.number}")
        
        # Move to home first
        self.move_to_home()
        
        # Move above target
        self.robot.MoveJ(place_above_pose)
        
        # Slow movement for precision
        self.robot.setSpeed(speed)
        
        # Move to placement position and release
        self.robot.MoveL(place_pose)
        self.gripper.release()
        
        # Attach piece to tower frame
        piece.attach_to_frame(tower_frame)
        
        # Move back up
        self.robot.MoveL(place_above_pose)
        
        # Reset speed and return home
        self.robot.setSpeed(50)
        self.move_to_home()


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
    
    def build_tower(self):
        """Execute the complete tower building sequence"""
        print("Starting Jenga tower construction...")
        
        # Initialize robot
        self.robot_controller.initialize()
        
        # Generate magazine pickup positions
        pick_above_poses, pick_poses = self.magazine.get_pick_positions()
        
        # Get tower configuration
        layer_configs = self.tower.get_layer_configuration()
        
        # Build tower layer by layer
        for layer_num, layer_config in enumerate(layer_configs):
            print(f"Building layer {layer_num + 1}")
            
            for i, piece_number in enumerate(layer_config["blocks"]):
                # Pick piece from magazine
                self.robot_controller.pick_piece(piece_number, pick_above_poses, pick_poses)
                
                # Calculate placement position
                place_above, place = self.tower.get_placement_pose(
                    layer_num,
                    i,
                    layer_config["x_offsets"][i],
                    layer_config["y_offsets"][i],
                    layer_config["rz"]
                )
                
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
    """Main function to run the Jenga robot system"""
    try:
        system = JengaRobotSystem()
        system.build_tower()
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
