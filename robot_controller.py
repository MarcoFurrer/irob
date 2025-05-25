from RTS import RTS
from jenga_constants import JengaConstants
from jenga_piece import JengaPiece


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
        self.rts.setVacuum(1, "dVacuum")
        
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
        self.rts.setVacuum(0, "dVacuum")
        
        # Attach piece to tower frame
        piece.attach_to_frame(tower_frame)
        
        # Move back up
        self.robot.MoveL(place_above_pose)
        
        # Reset speed and return home
        self.robot.setSpeed(50)
        self.move_to_home()