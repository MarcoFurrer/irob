from robodk import *
from robolink import *
from position import Position


class Jenga:
    def __init__(self, 
                 rts=None,
                 speed=100,
                 block_rows=2,
                 blocks:list = [],
                 ground_height = 0,
                 jenga_frame = None,
                 tower_frame = None,
                 jenga_start_pos:Position = Position(0, 0, 0, 0, 0, 0)
                 ):
        self.rts = rts
        self.speed = speed
        self.block_rows = block_rows
        self.blocks = blocks
        self.ground_height = ground_height
        self.jenga_frame = jenga_frame
        self.tower_frame = tower_frame
        self.safety_distance = 2
        self.block_width = 25  # Standard Jenga block width in mm
        self.block_height = 15  # Standard Jenga block height in mm
        self.jenga_start_pos = jenga_start_pos
        

    def get_jenga_pos(self, block_num):
        """
        Get the position of a block in a Jenga tower.
        Args:
            block_num (int): The block number (1-indexed).
        Returns:
            tuple: A tuple containing the x, y, z coordinates and rotation of the block.
        """
        # Calculate the layer and position within the layer
        layer = (block_num) // 3
        position = (block_num) % 3
        
        # Determine rotation based on layer
        rotation = layer % 2 == 0
        
        # Calculate x, y coordinates based on rotation
        if rotation:
            # Blocks along x-axis
            x = position * self.block_width
            y = 0
        else:
            # Blocks along y-axis
            x = 0
            y = position * self.block_width
        
        # Calculate z coordinate (height)
        z = layer * self.block_height
        
        return Position(x, y, z, 0,0,rotation*90) + self.jenga_start_pos

    
    def move_to_start(self):
        #TODO: in main.py logik machen
        """Move robot to home/safe position"""
        self.rts.robot.MoveJ(self.rts.robot.JointsHome())
        
        
    
    def grab_block(self, block):
        """Simple function that just moves to a block and grabs it
        Args:
            block: The RoboDK Item object representing the block
        """
        if not self.rts:
            print("No RTS object available")
            return
            
        # First move to a safer intermediate position
        print("Moving to safe intermediate position")
        self.rts.robot.MoveJ(self.rts.robot.JointsHome())
        
        # Get block position
        block_pos = block.PoseAbs()
        pos_xyz = block_pos.Pos()
        print(f"Block position: X={pos_xyz[0]:.1f}, Y={pos_xyz[1]:.1f}, Z={pos_xyz[2]:.1f}")
        
        # Try a modified approach - use the current robot orientation for better reachability
        try:
            # First approach: Use current orientation but move above the block
            print("Using alternative approach strategy...")
            current_pose = self.rts.robot.Pose()
            # Keep current orientation but change position
            approach_pos = transl(pos_xyz[0], pos_xyz[1], pos_xyz[2] + 50) * current_pose.inv() * current_pose
            
            # Move to approach position 
            print("Moving to modified approach position")
            self.rts.robot.MoveJ(approach_pos)
            
            # Move to grab position using linear motion
            print("Moving to grab position")
            grab_pos = transl(pos_xyz[0], pos_xyz[1], pos_xyz[2]) * current_pose.inv() * current_pose
            self.rts.robot.MoveL(grab_pos)
            
            # Activate vacuum to grab the block
            print("Activating vacuum")
            self.rts.setVacuum(1)
            
            # Small delay to ensure grip
            print("Waiting for vacuum to engage")
            pause(0.5)  # Using robodk.pause instead of RDK.pause
            
            # Move back up to approach position with block
            print("Moving back to approach position with block")
            self.rts.robot.MoveL(approach_pos)
            
        except Exception as e:
            print(f"Modified approach failed: {e}")
            print("Attempting direct grab...")
            
            try:
                # Try a more direct approach - sometimes simpler works better
                # Create a safe position directly above the current block
                current_pose = self.rts.robot.Pose()
                grab_pos = block_pos
                
                # Activate vacuum first (in simulation this might work)
                print("Activating vacuum")
                self.rts.setVacuum(1)
                
                print("Using direct grab")
                self.rts.robot.MoveJ(grab_pos)
                
                # Small delay
                pause(0.5)  # Using robodk.pause function
                
            except Exception as e2:
                print(f"Direct grab also failed: {e2}")
                raise
    
    def place_block_in_tower(self, block, block_index):
        """Place a block in the tower
        Args:
            block: The RoboDK Item object representing the block
            block_index: The index of the block to determine its position in the tower
        """
        if not self.rts or not self.tower_frame:
            print("RTS or tower frame not available")
            return
        
        # Use get_jenga_pos to get the position - reusing existing code for better consistency
        jenga_position = self.get_jenga_pos(block_index)
        print(f"Calculated tower position: X={jenga_position.x:.1f}, Y={jenga_position.y:.1f}, Z={jenga_position.z:.1f}, Rotation={jenga_position.rz:.1f}°")
        
        # Base position of the tower
        tower_pos = self.tower_frame.PoseAbs()
        print(f"Tower position: {tower_pos.Pos()}")
        
        # Convert Position object to pose matrix relative to tower position
        block_tower_pos = tower_pos * transl(jenga_position.x, jenga_position.y, jenga_position.z) * rotz(math.radians(jenga_position.rz))
        
        # Calculate approach position (100mm above for safety)
        approach_pos = block_tower_pos * transl(0, 0, 100)
        
        try:
            # Move to approach position
            print("Moving to tower approach position")
            self.rts.robot.MoveJ(approach_pos)
            
            # Move to placement position
            print("Moving to placement position")
            self.rts.robot.MoveL(block_tower_pos)
            
            # Release block
            print("Releasing vacuum grip")
            self.rts.setVacuum(0)
            
            # Small delay
            pause(0.5)  # Using robodk.pause function
            
            # Move back to approach position
            print("Moving back to approach position")
            self.rts.robot.MoveL(approach_pos)
            
        except Exception as e:
            print(f"Error during placement operation: {e}")
            raise
        
        
if __name__=="__main__":
    import RTS as RTS
    
    RDK = robolink.Robolink()
    robot = RDK.Item("Staubli TX2-40")
    gripper = RDK.Item("LWS_VakuumGreifer_14")
    piece = RDK.Item("AROB_JengaStuck10")
    tower_frame = RDK.Item('TowerFrame')
    jenga_frame = RDK.Item('JengaPieces')

    # Create RTS object and configure gripper
    rts = RTS.RTS(RDK, robot, gripper)
    rts.addConnection("dVacuum", "98FE10BA-0446-4B8A-A8CF-35B98F42725A", "dio")
    rts.setGripperConnection("dVacuum")
    
    jenga = Jenga(rts=rts, blocks=[piece], jenga_frame=jenga_frame, tower_frame=tower_frame)
    
    try:
        # Set robot speed to a lower value for safety
        robot.setSpeed(20)  # 20% of normal speed
        
        # Move to starting position
        print("Moving to home position")
        jenga.move_to_start()
        
        # Grab the block using the grab_block function
        print("Grabbing the Jenga block")
        try:
            jenga.grab_block(piece)
            print("Successfully grabbed the piece")
        except Exception as e:
            print(f"Error during block grabbing: {e}")
            print("Moving back to home position and exiting")
            jenga.move_to_start()
            exit(1)
            
        # Place the block in the Jenga tower
        print("Placing the block in the Jenga tower")
        try:
            # Place in position 0 (bottom layer, first position)
            jenga.place_block_in_tower(piece, 0)
            print("Successfully placed the piece in the tower")
        except Exception as e:
            print(f"Error during block placement: {e}")
            # Try to turn off vacuum in case of error
            try:
                rts.setVacuum(0)
                print("Released vacuum grip")
            except:
                pass
    
        # Return to home position
        print("Returning to home position")
        jenga.move_to_start()
        
    except Exception as e:
        print(f"Error in main program: {e}")
        # Try to return to a safe position
        try:
            robot.setSpeed(10)  # Slower speed for recovery
            robot.MoveJ(robot.JointsHome())
        except:
            print("Could not return to home position")
    
    finally:
        # Always try to restore robot speed
        try:
            robot.setSpeed(100)
        except:
            pass
