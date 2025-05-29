from RTS import RTS

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
        
        self.t_home = [0, 50, 50, 0, 60, 0]
        self.t_start = [0, 0, 90, 0, 90, 0]
        
        
        # Validate components
        if not self.robot.Valid():
            raise Exception("Robot 'Staubli TX2-40' not found in RoboDK")
        if not self.tool.Valid():
            raise Exception("Tool 'AROB_LWS_VakuumGreifer_14' not found in RoboDK")
    
    def initialize(self):
        """Initialize robot to start position"""
        self.robot.setJoints(self.t_start)
        self.robot.setPoseFrame(self.world_frame)
        self.robot.setSpeed(50, 50, 50, 75)
    
    def move_to_home(self):
        """Move robot to home position"""
        self.robot.MoveJ(self.t_home)
    
    def pick_piece(self, piece, pick_above_poses, pick_poses, speed=10):
        """Pick up a piece from the magazine"""
        # Support both JengaPiece objects and piece numbers
        piece_number = piece.number if hasattr(piece, 'number') else piece
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
    
    def place_piece(self, piece, place_above_pose, place_pose, tower_frame, speed=10):
        """Place a piece on the tower"""
        # Support both JengaPiece objects and piece numbers
        piece_number = piece.number if hasattr(piece, 'number') else piece
        print(f"Placing piece {piece_number}")
        
        # Move to home first
        self.move_to_home()
        
        # Move above target
        self.robot.MoveJ(place_above_pose)
        
        # Slow movement for precision
        self.robot.setSpeed(speed)
        
        # Move to placement position and release
        self.robot.MoveL(place_pose)
        self.rts.setVacuum(0, "dVacuum")
        
        # Attach piece to tower frame (if it's a JengaPiece object)
        if hasattr(piece, 'attach_to_frame'):
            piece.attach_to_frame(tower_frame)
        
        # Move back up
        self.robot.MoveL(place_above_pose)
        
        # Reset speed and return home
        self.robot.setSpeed(50)
        self.move_to_home()
    
    def move_piece(self, piece, magazine, tower, pick_above_poses, pick_poses, speed=10):
        """Complete move operation: pick from magazine and place on tower"""
        piece_number = piece.number if hasattr(piece, 'number') else piece
        print(f"Moving piece {piece_number} from magazine to tower")
        
        # Pick from magazine
        self.pick_piece(piece, pick_above_poses, pick_poses, speed)
        
        # Calculate placement position
        place_above, place = tower.get_placement_pose(piece)
        
        # Place on tower
        self.place_piece(piece, place_above, place, tower.frame, speed)