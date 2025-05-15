from robodk import *
from robolink import *

RDK = robolink.Robolink()

for i in range(1, 16):
    piece = RDK.Item(f"AROB_Jengastuck{i}")
    if not piece.Valid():
        print(f"[WARNING] AROB_Jengastuck{i} not found.")
        continue

    pose = piece.Pose()
    xyzrpw = Pose_2_KUKA(pose)  # Converts to [x,y,z,rx,ry,rz] in mm and deg

    print(f"Pose({xyzrpw[0]:.3f}, {xyzrpw[1]:.3f}, {xyzrpw[2]:.3f},  "
          f"{xyzrpw[3]:.3f}, {xyzrpw[4]:.3f}, {xyzrpw[5]:.3f})")
