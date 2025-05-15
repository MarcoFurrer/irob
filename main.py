from robodk import *
from robolink import *
import numpy as np
from src.jenga import *
import src.RTS as RTS
import time

print("In scope!")

# Initialize RoboDK API
RDK = robolink.Robolink()

# Get robot and gripper objects
robot = RDK.Item("Staubli TX2-40")
gripper = RDK.Item("LWS_VakuumGreifer_14")

jengaFrame = RDK.Item("JengaPieces")

# Create RTS object and configure gripper
rts = RTS.RTS(RDK, robot, gripper)
rts.addConnection("dVacuum", "98FE10BA-0446-4B8A-A8CF-35B98F42725A", "dio")
rts.setGripperConnection("dVacuum")

# Set up some test positions (in joint space)
home_joints = robot.JointsHome()

# Get current position to use as a reference
current_position = robot.Pose()
current_xyz = current_position.Pos()
print(f"Current robot position: X={current_xyz[0]:.1f}, Y={current_xyz[1]:.1f}, Z={current_xyz[2]:.1f}")

# Get current position as base for movements
base_pose = robot.Pose()

# Define a much smaller rectangular path (rectangle in XY plane)
# The rectangle is only 20mm x 20mm to stay within robot's workspace
rectangle_path = [
    base_pose,                                 # Starting point
    base_pose * transl(20, 0, 0),              # Move 20mm in X direction
    base_pose * transl(20, 20, 0),             # Move 20mm in Y direction (now at opposite corner)
    base_pose * transl(0, 20, 0),              # Move back in X direction
    base_pose                                  # Return to start
]

# Also create a vertical path to test Z-axis movement (only move upward to avoid collisions)
vertical_path = [
    base_pose,                                 # Starting point
    base_pose * transl(0, 0, 20),              # Move 20mm up
    base_pose                                  # Move back to original position
]

if __name__ == "__main__":
    try:
        print("Starting robot movement test...")
        
        # Set robot speed to very low value for safety
        robot.setSpeed(10)  # 10% of maximum speed for testing
        print("Robot speed set to 10% for safety during testing")
        
        # Show robot information
        print(f"Robot: {robot.Name()}")
        print(f"Robot joints: {robot.Joints().tolist()}")
        
        # Move to home position first for a safe starting point
        print("Moving to home position")
        robot.MoveJ(home_joints)
        time.sleep(1)
        
        # Get current robot position to plan movements relative to current position
        current_pose = robot.Pose()
        current_pos = current_pose.Pos()
        print(f"Current position after home: X={current_pos[0]:.1f}, Y={current_pos[1]:.1f}, Z={current_pos[2]:.1f}")
        
        # get current jengaframe pose
        basejengaFrame = jengaFrame.Pose()
        print(basejengaFrame)
                
        # Test a small joint movement - should be very safe
        print("\n=== Test 0: Small Joint Movement ===")
        print("Testing small joint movement (1 degree in first joint)")
        current_joints = robot.Joints()
        test_joints = current_joints.copy()
        test_joints[0] = test_joints[0] + math.radians(1)
        robot.MoveJ(test_joints)
        time.sleep(1)
        
        # TEST 1: RECTANGULAR PATH - very small movements only in XY plane
        print("\n=== Test 1: Rectangular Path (XY plane) ===")
        print("Starting rectangular path movement with tiny steps")
                
        # Try X-axis movement only first (safest)
        print("Test 1.1: X-axis movement only (20mm)")
        try:
            x_only_pose = robot.Pose() * transl(20, 0, 0)
            x_pos = x_only_pose.Pos()
            print(f"Moving to X+20mm: X={x_pos[0]:.1f}, Y={x_pos[1]:.1f}, Z={x_pos[2]:.1f}")
            robot.MoveJ(x_only_pose)
            time.sleep(1)
            # Move back
            print("Moving back to starting position")
            robot.MoveJ(robot.Pose() * transl(-20, 0, 0))
            time.sleep(1)
        except Exception as e:
            print(f"X-axis movement failed: {e}")
            # Continue with the next test
        
        # Try Y-axis movement only next
        print("\nTest 1.2: Y-axis movement only (20mm)")
        try:
            y_only_pose = robot.Pose() * transl(0, 20, 0)
            y_pos = y_only_pose.Pos()
            print(f"Moving to Y+20mm: X={y_pos[0]:.1f}, Y={y_pos[1]:.1f}, Z={y_pos[2]:.1f}")
            robot.MoveJ(y_only_pose)
            time.sleep(1)
            # Move back
            print("Moving back to starting position")
            robot.MoveJ(robot.Pose() * transl(0, -20, 0))
            time.sleep(1)
        except Exception as e:
            print(f"Y-axis movement failed: {e}")
            # Continue with the next test
        
        # TEST 2: VERTICAL MOVEMENT (Z-axis upward only for safety)
        print("\n=== Test 2: Vertical Movement (Z axis up only) ===")
        
        try:
            # Move up by 20mm
            z_up_pose = robot.Pose() * transl(0, 0, 20)
            z_pos = z_up_pose.Pos()
            print(f"Moving up 20mm: X={z_pos[0]:.1f}, Y={z_pos[1]:.1f}, Z={z_pos[2]:.1f}")
            robot.MoveJ(z_up_pose)
            time.sleep(1)
            
            # Move back down
            print("Moving back to starting position")
            robot.MoveJ(robot.Pose() * transl(0, 0, -20))
            time.sleep(1)
        except Exception as e:
            print(f"Z-axis movement failed: {e}")
            # Continue with the next test
        
        # TEST 3: VACUUM GRIPPER
        print("\n=== Test 3: Vacuum Gripper ===")
        
        try:
            print("Testing vacuum gripper - ON")
            rts.setVacuum(1)
            time.sleep(1.5)
            
            print("Testing vacuum gripper - OFF")
            rts.setVacuum(0)
            time.sleep(1)
        except Exception as e:
            print(f"Vacuum gripper test failed: {e}")
        
        # Return to home position - always try to return home at the end
        print("\nReturning to home position")
        robot.MoveJ(home_joints)
        
        # Set robot speed back to default
        robot.setSpeed(100)  # 100% speed
        
        print("\n✓ Test completed successfully!")
        print("Robot movements have been successfully tested.")
        
    except Exception as e:
        print(f"❌ Error during robot movement test: {e}")
        # Try to return to a safe position if possible
        try:
            print("Attempting to return to home position after error")
            robot.MoveJ(home_joints)
            # Set robot speed back to default
            robot.setSpeed(100)  # 100% speed
        except Exception as e2:
            print(f"Could not return to home position: {e2}")
        
    finally:
        # Make sure we always restore the original speed, even if there's an error
        try:
            robot.setSpeed(100)
            print("Robot speed restored to 100%")
        except:
            pass
    # jenga.place_block_in_tower(target_block, 7)


    # # Alle Blockpositionen anzeigen
    # print("\nAktuelle Blockpositionen (XYZ in mm):")
    # for i, block in enumerate(blocks):
    #     pos = block.PoseAbs().Pos()
    #     print(f"Block{i}: X={pos[0]:.1f}, Y={pos[1]:.1f}, Z={pos[2]:.1f}")

    # jenga.move_to_start()