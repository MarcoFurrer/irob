from robodk import *
from robolink import *
import numpy as np
from src.jenga import *
import src.RTS as RTS

BLOCKS = 15

RDK = robolink.Robolink()

robot = RDK.Item("Staubli TX2-90L", ITEM_TYPE_ROBOT)
gripper = RDK.Item("LWS_VakuumGreifer_14")

# RTS-Objekt erstellen und Greifer konfigurieren
rts = RTS.RTS(RDK, robot, gripper)
rts.addConnection("dVacuum", "98FE10BA-0446-4B8A-A8CF-35B98F42725A", "dio")
rts.setGripperConnection("dVacuum")

magazine_frame = RDK.Item("Magazine")
tower_frame = RDK.Item("Tower")

# Blockobjekte automatisch erstellen
blocks = [RDK.Item(f"Block{i}") for i in range(BLOCKS)]
blocks_by_name = {f"block{i}": block for i, block in enumerate(blocks)}

# Jenga-Klasse initialisieren
jenga = Jenga(robot, rts)

if __name__ == "__main__":
    jenga.move_to_start()

    # Beispiel: gezielt Block 7 greifen und platzieren
    target_block = blocks[7]
    block_pose = target_block.PoseAbs()
    jenga.pick_block_at_pose(block_pose)
    jenga.place_block_in_tower(target_block, 7)


    # Alle Blockpositionen anzeigen
    print("\nAktuelle Blockpositionen (XYZ in mm):")
    for i, block in enumerate(blocks):
        pos = block.PoseAbs().Pos()
        print(f"Block{i}: X={pos[0]:.1f}, Y={pos[1]:.1f}, Z={pos[2]:.1f}")

    jenga.move_to_start()