# BEISPIELPROGRAMM: RTS-LIBRARY: ENDLOSSCHLEIFE
# Führt auf dem Roboter einen Bewegungsablauf unendlich viele male aus.
# In der Simulation wird dieser Bewegungsablauf nur einmal durchlaufen.

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

# Erstellen des RTS-Objektes. Falls im Programm kein Greifer genutzt wird, muss auch nicht zwingend einer übergeben werden.
RTS = RTS(RDK,rRobot)

# Bewegung zum home-Punkt
rRobot.MoveJ(pHome)

# Beginn der Endlosschleife
RTS.whileEndless("endlessWhile")

# Bewegungen innerhalb der Endlosschleife
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Ende der Endlosschleife
RTS.endWhileEndless("endlessWhile")
