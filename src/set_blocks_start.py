from robodk import *
from robolink import *

from src.jenga import Jenga
import numpy as np
import src.RTS as RTS

# Number of blocks to reset
BLOCKS = 15

# Initialize RoboDK 
RDK = robolink.Robolink()

# Get robot and gripper with the correct names
robot = RDK.Item("Staubli TX2-90L")
gripper = RDK.Item("AROB_LWS_VakuumGreifer_14")

# Initialize RTS object
RTS = RTS.RTS(RDK, robot, gripper)

# Set up the vacuum gripper connection
RTS.addConnection("dVacuum","98FE10BA-0446-4B8A-A8CF-35B98F42725A","dio")
RTS.setGripperConnection("dVacuum")

# Get magazine and tower frame references with correct names
magazine_frame = RDK.Item('MagazinFrame')
tower_frame = RDK.Item('TowerFrame')

# Initialize Jenga class - pass the robot name as string since that's what Jenga expects
jenga = Jenga("Staubli TX2-90L", amout_of_blocks=BLOCKS)

# Add RTS to jenga object (needed for vacuum control)
jenga.rts = RTS

# Get all blocks with correct naming convention
blocks = []
for i in range(BLOCKS):
    block = RDK.Item(f'AROB_Jengastuck{i}')
    if block.Valid():
        blocks.append(block)
    else:
        print(f"Warning: AROB_Jengastuck{i} not found")

def reset_blocks_to_start():
    """Reset all blocks to their starting positions in the magazine"""
    print(f"Resetting {len(blocks)} blocks to starting positions...")
    
    # Move robot to home position
    jenga.move_to_start()
    
    # For each block
    for i, block in enumerate(blocks):
        print(f"Resetting block {i}...")
        
        # Calculate magazine position for this block
        # Calculate the row and column of the block in the magazine
        row = i // (BLOCKS // 2)  # Assuming 2 rows
        col = i % (BLOCKS // 2)
        
        # Calculate position in magazine frame
        magazine_pos = magazine_frame.PoseAbs()
        block_pos = magazine_pos * transl(col * 25, row * 25, 15)
        
        # Add rotation for proper block orientation (flat)
        block_pos = block_pos * rotx(np.pi/2)
        
        # Pick up the block from current position
        jenga.pick_block(block)
        
        # Move to magazine position and place block
        # Calculate approach position
        approach_pos = block_pos * transl(0, 0, 50)
        
        # Move to approach position
        jenga.robot.MoveJ(approach_pos)
        
        # Move to placement position
        jenga.robot.MoveL(block_pos)
        
        # Release block
        jenga.rts.setVacuum(0)
        
        # Small delay
        pause(0.2)
        
        # Move back to approach position
        jenga.robot.MoveL(approach_pos)
        
        # Update block position in RoboDK
        block.setPose(block_pos)
    
    # Return to home position when done
    jenga.move_to_start()
    print("All blocks reset to starting positions")

if __name__ == "__main__":
    reset_blocks_to_start()
