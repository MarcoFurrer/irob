# BEISPIELPROGRAMM: RTS-LIBRARY: IF-ABFRAGE VON DIGITALEM EINGANG.
# Führt 2 Bewegungen aus und gibt dann eine Nachricht einerseits
# in der Simulation, und andererseits auf dem Robotercontroller aus.

# Import der Librarys
from robolink import *
from robodk import *
from src.RTS import *

RDK = Robolink()

# Initialisierung aller Simulationsobjekte
r_tx240 = RDK.Item("Staubli TX2-40", ITEM_TYPE_ROBOT)
g_gripper = RDK.Item("LWS_VakuumGreifer_14")
f_magazine = RDK.Item("MagazineFrame", ITEM_TYPE_FRAME)
f_world = RDK.Item("world", ITEM_TYPE_FRAME)
f_robot = RDK.Item("Staubli TX2-40 Base", ITEM_TYPE_FRAME)
pHome = RDK.Item("pHome", ITEM_TYPE_TARGET)
block = RDK.Item("Jengastuck 1")


# Erstellen des RTS-Objektes.
RTS = RTS(RDK, r_tx240, g_gripper)

# Initialisieren der Verbindung des Vakuumgreifers.
RTS.addConnection("dVacuum","98FE10BA-0446-4B8A-A8CF-35B98F42725A","dio")

# Initialisieren der Verbindung des Vakuumsensors.
RTS.addConnection("dVacuumSensor","BFFF5B02-EDA8-4EAA-AB65-0D4DAB2D24C5","dio")

# Setzen der Verbindung dVacuum als Greifer des Roboters.
RTS.setGripperConnection("dVacuum")

# Berechnung und Bewegung zu den Punkten.
IntermediatePose = transl(254, -30, -190) * rotx(-pi) * rotz(pi)

r_tx240.MoveJ(pHome)
r_tx240.MoveJ(IntermediatePose)

BlockPosition = block.PoseAbs()
PickUpPosition = BlockPosition
PickUpPosition = PickUpPosition * rotx(-pi) * rotz(-pi/2)

PickApproachPosition= PickUpPosition * rotz(2*pi)
PickApproachPosition=PickApproachPosition * transl(0, 0, -50)

r_tx240.MoveJ(PickApproachPosition)
r_tx240.MoveL(PickUpPosition)

# Setzen des Vakuums. Setzt dies in der Simulation und
# auf dem Roboter (Insofern der Greifer richtig initialisiert wurden.)
RTS.setVacuum(1)

# If-Abfrage, ob das Vakuum wirklich gesetzt wurde.
RTS.ifConnection("dVacuumSensor", 1)

# Bewegt Roboter zu folgenden 4 Punkten, falls ein Vakuum gefunden wurde.
r_tx240.MoveL(PickApproachPosition)
r_tx240.MoveJ(IntermediatePose)
r_tx240.MoveJ(PickApproachPosition)
r_tx240.MoveL(PickUpPosition)

# Lässt den Block wieder los.
RTS.setVacuum(0)

# Else-Anweisung der obigen If-Anweisung
RTS.elseConnection()

# Folgende Aktionen werden ausgeführt, falls kein Vakuum gefunden wurde.
# Lässt den Block wieder los.
RTS.setVacuum(0)
# Bewegt den Roboter zur home-Position.
r_tx240.MoveJ(pHome)

# End-Schranke der If-Bedingung.
RTS.endIfConnection()