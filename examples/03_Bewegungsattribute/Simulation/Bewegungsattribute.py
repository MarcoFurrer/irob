# BEISPIELPROGRAMM: RTS-LIBRARY: BEWEGUNGSATTRIBUTE SETZEN.
# Führt 4 Bewegungen aus, und ändert dann ein Bewegungsattribut.
# Hat KEINE Auswirkung auf die Simulationsattribute, nur auf das Roboterprogramm.

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

RTS.setMovementParameter(30, 30, 30, 30, 30)

# Führt 5 Bewegungen aus
rRobot.MoveJ(pHome)
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Setzt die maximale Rotationsgeschwindigkeit des Tools. Hat keine Auswirkung auf die Simulation.
RTS.setRotationalSpeedTool(1000)

# Führt 4 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Setzt die maximale Lineargeschwindigkeit des Tools. Hat keine Auswirkung auf die Simulation.
RTS.setTranslationalSpeedTool(1000)

# Führt 4 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Setzt die Lineareschwindigkeit des Roboters in % der Nenngeschwindigkeit. Hat keine Auswirkung auf die Simulation.
RTS.setSpeedPercentageJoints(100)

# Führt 4 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Setzt die Achsbeschleunigung des Roboters in % der Nennbeschleunigung. Hat keine Auswirkung auf die Simulation.
RTS.setAccelerationPercentageJoints(100)

# Führt 4 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)

# Setzt die Achsverzögerung des Roboters in % der Nennverzögerung. Hat keine Auswirkung auf die Simulation.
RTS.setDeccelerationPercentageJoints(100)

# Führt 4 Bewegungen aus
rRobot.MoveJ(p1)
rRobot.MoveJ(p2)
rRobot.MoveJ(p3)
rRobot.MoveJ(pHome)
