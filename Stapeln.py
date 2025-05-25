from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *
from RTS import RTS

# Verbindung zu RoboDK herstellen
RDK = Robolink()

# Roboter, Werkzeug und Frames initialisieren
r_robot = RDK.Item('Staubli TX2-40')
tl_tool = RDK.Item('AROB_LWS_VakuumGreifer_14')
f_world = RDK.Item("World")
f_pick = RDK.Item("MagazinFrame")
f_place = RDK.Item("TowerFrame")

# Anfangs- und Home-Positionen des Roboters definieren
t_home = [0, 50, 50, 0, 60, 0]
t_start = [0, 0, 90, 0, 90, 0]

# RTS-Verbindung und Greifer initialisieren
RTS = RTS(RDK, r_robot, tl_tool)
RTS.addConnection('dVacuum', '98FE10BA-0446-4B8A-A8CF-35B98F42725A', 'dio')
RTS.setGripperConnection('dVacuum')
RTS.addConnection('dVaccumSensor', '98FE10BA-0446-4B8A-A8CF-35B98F42725B', 'aio')

# Offsets für das Aufnehmen und Platzieren von Jenga-Blöcken
OFFSET_X = 72.5
OFFSET_Y_FIRST_ROW = 97.5
OFFSET_Y_SECOND_ROW = 172.5
Z_PICK = 15
Z_OFFSET = 15
COUNT_FIRST_ROW, COUNT_SECOND_ROW = 8, 7
LENGTH, WIDTH, HEIGHT = 75, 25.5, 15
OFFSET_TOOL = 0
X_TOWER, Y_TOWER = 70, 70

# Jenga-Blöcke in einem Container speichern
jenga_container = {f"Jengas{i+1}": RDK.Item(f"Jengastuck {i+1}") for i in range(15)}

# Positionen für das Aufnehmen der Blöcke generieren
def generate_positions():
    pick_above, pick = {}, {}
    for i in range(COUNT_FIRST_ROW):
        # Position oberhalb und direkt am Block in der ersten Reihe
        pick_above[f"Jenga{i+1}above"] = f_pick.Pose() * transl(OFFSET_X + i * 25, OFFSET_Y_FIRST_ROW, Z_OFFSET) * rotx(pi)
        pick[f"Jenga{i+1}"] = f_pick.Pose() * transl(OFFSET_X + i * 25, OFFSET_Y_FIRST_ROW, Z_PICK) * rotx(pi)
    for i in range(COUNT_SECOND_ROW):
        # Position oberhalb und direkt am Block in der zweiten Reihe
        pick_above[f"Jenga{i+9}above"] = f_pick.Pose() * transl(OFFSET_X + i * 25, OFFSET_Y_SECOND_ROW, Z_OFFSET) * rotx(pi)
        pick[f"Jenga{i+9}"] = f_pick.Pose() * transl(OFFSET_X + i * 25, OFFSET_Y_SECOND_ROW, Z_PICK) * rotx(pi)
    return pick_above, pick

# Jenga-Block aufnehmen
def pick_jenga(jenga_number, pick_above, pick, speed=10):
    r_robot.MoveJ(t_home)  # Roboter in Home-Position bewegen
    r_robot.MoveJ(pick_above[f"Jenga{jenga_number}above"])  # Über dem Block positionieren
    r_robot.setSpeed(speed)  # Geschwindigkeit reduzieren
    r_robot.MoveL(pick[f"Jenga{jenga_number}"])  # Block greifen
    RTS.setVacuum(1, "dVacuum")  # Vakuum aktivieren
    r_robot.MoveL(pick_above[f"Jenga{jenga_number}above"])  # Zurück nach oben
    r_robot.setSpeed(50)  # Geschwindigkeit zurücksetzen

# Jenga-Block platzieren
def place_jenga(jenga_number, x, y, z, rz, speed=10):
    # Zielposition oberhalb und direkt am Platz definieren
    place_above = f_place.Pose() * transl(x, y, z + 30) * rotz(rz) * rotx(pi)
    place = f_place.Pose() * transl(x, y, z) * rotz(rz) * rotx(pi)
    r_robot.MoveJ(t_home)  # Roboter in Home-Position bewegen
    r_robot.MoveJ(place_above)  # Über der Zielposition positionieren
    r_robot.setSpeed(speed)  # Geschwindigkeit reduzieren
    r_robot.MoveL(place)  # Block absetzen
    
    RTS.setVacuum(0, "dVacuum")  # Vakuum deaktivieren
    
    # Block statisch im Tower-Frame fixieren
    jenga_container[f"Jengas{jenga_number}"].setParentStatic(f_place)
    
    r_robot.MoveL(place_above)  # Zurück nach oben
    r_robot.setSpeed(50)  # Geschwindigkeit zurücksetzen
    r_robot.MoveJ(t_home)  # Zurück in die Home-Position

# Jenga-Turm aufbauen
def build_jenga_tower(pick_above, pick):
    # Definiert die Reihenfolge und Positionen der Blöcke im Turm
    positions = [
        {"blocks": [1, 2, 3], "x_offsets": [0, 0, 0], "y_offsets": [WIDTH, 0, -WIDTH], "rz": pi/2},
        {"blocks": [4, 5, 6], "x_offsets": [WIDTH, 0, -WIDTH], "y_offsets": [0, 0, 0], "rz": pi},
        {"blocks": [7, 8, 9], "x_offsets": [0, 0, 0], "y_offsets": [WIDTH, 0, -WIDTH], "rz": pi/2},
        {"blocks": [10, 11, 12], "x_offsets": [WIDTH, 0, -WIDTH], "y_offsets": [0, 0, 0], "rz": pi},
        {"blocks": [13, 14, 15], "x_offsets": [0, 0, 0], "y_offsets": [WIDTH, 0, -WIDTH], "rz": pi/2},
    ]
    for layer, pos in enumerate(positions):
        z = (layer + 1) * HEIGHT - OFFSET_TOOL  # Z-Höhe der Ebene
        for i, block in enumerate(pos["blocks"]):
            pick_jenga(block, pick_above, pick)  # Block aufnehmen
            place_jenga(block, X_TOWER + pos["x_offsets"][i], Y_TOWER + pos["y_offsets"][i], z, pos["rz"])  # Block platzieren

# Hauptfunktion
def main():
    r_robot.setJoints(t_start)  # Roboter in Startposition bewegen
    r_robot.setPoseFrame(f_world)  # Frame setzen
    r_robot.setSpeed(50, 50, 50, 75)  # Geschwindigkeit initialisieren
    pick_above, pick = generate_positions()  # Positionen generieren

    build_jenga_tower(pick_above, pick)  # Turm bauen

if __name__ == "__main__":
    main()
