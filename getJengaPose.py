from robodk import *
from robolink import *

def get_jenga_pose(block_num, block_width=75.0, block_height=15.0, start_offset=[0, 0, 0, 0, 0, 0]):
    """
    Berechnet die Pose eines Jenga-Blocks basierend auf dessen Nummer.

    Args:
        block_num (int): Blocknummer von 0 bis 14.
        block_width (float): Breite eines Blocks in mm.
        block_height (float): Höhe eines Blocks in mm.
        start_offset (list): Startversatz [x, y, z, rx, ry, rz].

    Returns:
        Mat: Pose (4x4-Matrix) für RoboDK.
    """
    layer = block_num // 3
    position = block_num % 3
    rotation = layer % 2 == 0  # Gerade Ebene = Ausrichtung in X

    if rotation:
        x = (position - 1) * block_width
        y = 0
        rz = 0
    else:
        x = 0
        y = (position - 1) * block_width
        rz = 90

    z = layer * block_height

    # Startoffset hinzufügen
    x += start_offset[0]
    y += start_offset[1]
    z += start_offset[2]
    rx = start_offset[3]
    ry = start_offset[4]
    rz += start_offset[5]

    return KUKA_2_Pose([x, y, z, rx, ry, rz])

RDK = robolink.Robolink()

# Startposition (z. B. wie aus Screenshot)
start_offset = [325.0, -100.0, -340.0, 0.0, 0.0, 90.0]

for i in range(15):
    piece = RDK.Item(f"AROB_Jengastuck{i+1}")
    if not piece.Valid():
        print(f"[WARNING] AROB_Jengastuck{i+1} not found.")
        continue

    pose = get_jenga_pose(i, start_offset=start_offset)
    piece.setPose(pose)

    # Debug-Ausgabe
    xyzrpw = Pose_2_KUKA(pose)
    print(f"Pose({xyzrpw[0]:.3f}, {xyzrpw[1]:.3f}, {xyzrpw[2]:.3f},  "
          f"{xyzrpw[3]:.3f}, {xyzrpw[4]:.3f}, {xyzrpw[5]:.3f})")