# BEISPIELPROGRAMM: RTS-LIBRARY: VAKUUMGREIFER ANSTEUERN
# Führt eine Bewegung zu einem Jenga-Stein aus, saugt diesen an und
# setzt den Stein dann wieder ab.

# Import der Librarys
from robolink import *
from robodk import *
from src.RTS import *

RDK = Robolink()

# Initialisierung aller Simulationsobjekte
rRobot = RDK.Item('Staubli TX2-40')
pHome = RDK.Item('pHome')
p1 = RDK.Item('p1')
p2 = RDK.Item('p2')
p3 = RDK.Item('p3')

# Erstellen des RTS-Objektes. Falls das Programm keinen Greifer nutzt, muss dieser nicht zwingend übergeben werden.
RTS = RTS(RDK,rRobot)

# Führt 5 Bewegungen aus.
rRobot.MoveJ(pHome)
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Erzeugt auf dem Controller eine Abfrage. Alle folgenden Befehle werden in der Simulation ausgeführt,
# also die welche beim Drücken von "OK" ausgeführt werden UND die, welche beim Drücken von "Abbrechen"
# ausgeführt werden.
RTS.ifConfirm("Bewegung nochmals ausführen?")

# Folgende Bewegungen werden ausgeführt, falls auf dem Controller "OK" gedrückt wurde.
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Schranke für die Else-Anweisung.
RTS.elseConfirm()

# Folgende Bewegungen werden ausgeführt, falls auf dem Controller "Abbrechen" gedrückt wurde.
rRobot.MoveJ(p3)
rRobot.MoveJ(p2)
rRobot.MoveJ(p1)
rRobot.MoveJ(pHome)

# End-Schranke der If-Abfrage
RTS.endIfConfirm()
