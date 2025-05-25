# test_reachability.py
# Quick test to check robot workspace and reachable positions

from robodk import robolink
from robodk import robomath
from robot_controller import RobotController

def test_robot_workspace():
    rdk = robolink.Robolink()
    robot_controller = RobotController(rdk)
    
    # Get home position
    robot_controller.move_to_home()
    home_pose = robot_controller.robot.Pose()
    home_coords = robomath.pose_2_xyzrpw(home_pose)
    print(f"Home position: {home_coords}")
    
    # Test some positions around home to see what's reachable
    test_positions = [
        [200, 200, -200, 0, 180, 0],  # closer position
        [150, 150, -250, 0, 180, 0],  # even closer
        [100, 0, -300, 0, 180, 0],    # straight ahead
        [0, 200, -300, 0, 180, 0],    # to the side
    ]
    
    for i, pos in enumerate(test_positions):
        try:
            print(f"\nTesting position {i+1}: {pos}")
            pose = robomath.xyzrpw_2_pose(pos)
            robot_controller.robot.MoveJ(pose)
            print(f"  ✓ Position {i+1} is REACHABLE")
        except Exception as e:
            print(f"  ✗ Position {i+1} is NOT reachable: {e}")
    
    # Return to home
    robot_controller.move_to_home()

if __name__ == "__main__":
    test_robot_workspace()
