from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *
from RTS import RTS

# ---------------------------------------------
# Konfiguration
# ---------------------------------------------
class JengaConfig:
    LENGTH = 75
    WIDTH = 25.5
    HEIGHT = 15
    OFFSET_TOOL = 0
    X_TOWER = 70
    Y_TOWER = 70
    Z_PICK = 15
    Z_OFFSET = 15
    OFFSET_X = 72.5
    OFFSET_Y_FIRST_ROW = 97.5
    OFFSET_Y_SECOND_ROW = 172.5
    COUNT_FIRST_ROW = 8
    COUNT_SECOND_ROW = 7

cfg = JengaConfig()

# ---------------------------------------------
# RoboDK Initialisierung
# ---------------------------------------------
RDK = Robolink()
bot = RDK.Item('Staubli TX2-40')
tool = RDK.Item('AROB_LWS_VakuumGreifer_14')
worldFrame = RDK.Item("World")
pickFrame = RDK.Item("MagazinFrame")
placeFrame = RDK.Item("TowerFrame")

homeTarget = [0, 50, 50, 0, 60, 0]
startTarget = [0, 0, 90, 0, 90, 0]

RTS = RTS(RDK, bot, tool)
RTS.addConnection('dVacuum', '98FE10BA-0446-4B8A-A8CF-35B98F42725A', 'dio')
RTS.setGripperConnection('dVacuum')
RTS.addConnection('dVaccumSensor', '98FE10BA-0446-4B8A-A8CF-35B98F42725B', 'aio')

jenga_container = {f"Jengas{i+1}": RDK.Item(f"Jengastuck {i+1}") for i in range(15)}

# ---------------------------------------------
# Positionsgenerierung
# ---------------------------------------------
def generate_positions():
    pick_above, pick = {}, {}
    rows = [
        (cfg.COUNT_FIRST_ROW, cfg.OFFSET_Y_FIRST_ROW, 0),
        (cfg.COUNT_SECOND_ROW, cfg.OFFSET_Y_SECOND_ROW, cfg.COUNT_FIRST_ROW)
    ]
    for count, y_offset, index_offset in rows:
        for i in range(count):
            key = index_offset + i + 1
            pos_above = pickFrame.Pose() * transl(cfg.OFFSET_X + i * 25, y_offset, cfg.Z_OFFSET) * rotx(pi)
            pos = pickFrame.Pose() * transl(cfg.OFFSET_X + i * 25, y_offset, cfg.Z_PICK) * rotx(pi)
            pick_above[f"Jenga{key}above"] = pos_above
            pick[f"Jenga{key}"] = pos
    return pick_above, pick

# ---------------------------------------------
# Turmstruktur definieren
# ---------------------------------------------
def generate_tower_structure():
    return [
        {"rz": pi/2, "offsets": [(0, cfg.WIDTH), (0, 0), (0, -cfg.WIDTH)]},
        {"rz": pi,   "offsets": [(cfg.WIDTH, 0), (0, 0), (-cfg.WIDTH, 0)]},
        {"rz": pi/2, "offsets": [(0, cfg.WIDTH), (0, 0), (0, -cfg.WIDTH)]},
        {"rz": pi,   "offsets": [(cfg.WIDTH, 0), (0, 0), (-cfg.WIDTH, 0)]},
        {"rz": pi/2, "offsets": [(0, cfg.WIDTH), (0, 0), (0, -cfg.WIDTH)]},
    ]

# ---------------------------------------------
# Pick & Place
# ---------------------------------------------
def pick_jenga(jenga_number, pick_above, pick, speed=10):
    bot.MoveJ(homeTarget)
    bot.MoveJ(pick_above[f"Jenga{jenga_number}above"])
    bot.setSpeed(speed)
    bot.MoveL(pick[f"Jenga{jenga_number}"])
    RTS.setVacuum(1, "dVacuum")
    bot.MoveL(pick_above[f"Jenga{jenga_number}above"])
    bot.setSpeed(50)

def place_jenga(jenga_number, x, y, z, rz, speed=10):
    place_above = placeFrame.Pose() * transl(x, y, z + 30) * rotz(rz) * rotx(pi)
    place = placeFrame.Pose() * transl(x, y, z) * rotz(rz) * rotx(pi)

    bot.MoveJ(homeTarget)
    bot.MoveJ(place_above)
    bot.setSpeed(speed)
    bot.MoveL(place)
    RTS.setVacuum(0, "dVacuum")
    jenga_container[f"Jengas{jenga_number}"].setParentStatic(placeFrame)
    bot.MoveL(place_above)
    bot.setSpeed(50)
    bot.MoveJ(homeTarget)

def move_block(jenga_number, pick_above, pick, place_pose):
    pick_jenga(jenga_number, pick_above, pick)
    place_jenga(jenga_number, *place_pose)

# ---------------------------------------------
# Turmaufbau
# ---------------------------------------------
def build_jenga_tower(pick_above, pick):
    structure = generate_tower_structure()
    block_id = 1
    for layer, layer_info in enumerate(structure):
        z = (layer + 1) * cfg.HEIGHT - cfg.OFFSET_TOOL
        for (dx, dy) in layer_info["offsets"]:
            print(f"[INFO] Platziere Block {block_id} auf Ebene {layer + 1}")
            move_block(block_id, pick_above, pick,
                       (cfg.X_TOWER + dx, cfg.Y_TOWER + dy, z, layer_info["rz"]))
            block_id += 1

# ---------------------------------------------
# Hauptfunktion
# ---------------------------------------------
def main():
    bot.setJoints(startTarget)
    bot.setPoseFrame(worldFrame)
    bot.setSpeed(50, 50, 50, 75)
    pick_above, pick = generate_positions()
    build_jenga_tower(pick_above, pick)

if __name__ == "__main__":
    main()
