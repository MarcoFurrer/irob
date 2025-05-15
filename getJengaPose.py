from robodk import *
from robolink import *

RDK = robolink.Robolink()

for i in range(1, 16):
    piece = RDK.Item(f"AROB_Jengastuck{i}")
    if not piece.Valid():
        print(f"[WARNING] AROB_Jengastuck{i} not found.")
        continue

    pose = piece.Pose()
    xyzrpw = Pose_2_KUKA(pose)  
    print(f"Pose({xyzrpw[0]:.3f}, {xyzrpw[1]:.3f}, {xyzrpw[2]:.3f},  "
          f"{xyzrpw[3]:.3f}, {xyzrpw[4]:.3f}, {xyzrpw[5]:.3f})")
    

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
        
        # Determine rotation based on layer (alternating)
        # True for even layers (0, 2, 4...), False for odd layers (1, 3, 5...)
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

        pose_new = KUKA_2_Pose(xyzrpw)  # Konvertiere zurück in RoboDK-Pose (4x4-Matrix)
        piece.setPose(pose_new)# Converts to [x,y,z,rx,ry,rz] in mm and deg