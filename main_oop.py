# main_oop.py
# Simple main file using the object-oriented Jenga robot system

from JengaRobotSystem import JengaRobotSystem

def main():
    """Simple main function demonstrating the OOP system"""
    # Create and run the Jenga robot system
    system = JengaRobotSystem()
    system.build_tower()

if __name__ == "__main__":
    main()
