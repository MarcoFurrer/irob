# BEISPIELPROGRAMM: RTS-LIBRARY: CONTROLLERNACHRICHT ANZEIGEN.
# Führt 2 Bewegungen aus und gibt dann eine Nachricht einerseits
# in der Simulation, und andererseits auf dem Robotercontroller aus.

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


# Erstellen des RTS-Objektes. Falls im Programm kein Greifer genutzt wird, muss auch nicht zwingend einer übergeben werden.
RTS = RTS(RDK,rRobot)

# Führt 2 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)

# Gibt auf Controller und der Simulation die Nachricht "Nachricht1" aus.
RTS.boxAlert("Nachricht 1")

# Führt 2 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)

# Gibt auf Controller und der Simulation die Nachricht "Nachricht2" aus.
RTS.boxAlert("Nachricht 2")

# Führt 2 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)

# Gibt auf Controller und der Simulation die Nachricht "Programm ist fertig" aus.
RTS.boxAlert("Programm ist fertig")
