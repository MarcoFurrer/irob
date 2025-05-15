# Copyright 2015-2020 - HSLU - https://www.hslu.ch
# Creator: Janis Perren
# Date: 24. 03. 2021
# --------------- DESCRIPTION ----------------
# This file defines functions to improve the usability of RoboDK with Stäubli robots.
# --------------------------------------------

import os, time
from robodk import *   
from inspect import getframeinfo, stack

lIOTypes = ["dio","aio","sio"]
conditions = ["==","!=","<",">","<=",">="]
class Helloworld:
    def __init__(self):
        pass

class RTS:
    
    """
        Die Klasse RTS wird genutzt, um Funktionen an den Postprozessor zu schicken, welche
        in der Grundversion von RoboDK nicht verfügbar sind. Ausserdem beinhaltet sie einige 
        Funktionen, welche die Programmierung erleichtert.

    Args:
        RDK (Item): Dies muss ein gültiges Robolink()-Objekt sein, welches in der Simulation genutzt wird.
        robot (Item): Dies muss ein gültiger Roboter sein, welcher in der Simulation genutzt wird.
        gripper (Item, optional): Falls ein Greifer genutzt wird, muss dieser hier übergeben werden.
        
    Example:
    
        .. code-block:: python
            
            from robolink import *             # robolink library importieren.
            from robodk import *               # robodk library importieren.
            
            RDK = Robolink()                   # Robolinkobjekt erstellen.
            robot  = RDK.Item('robotername')   # Roboter der Simulation wird initialisiert.
            gripper = RDK.Item('gripper')      # Robotergreifer wird initialisiert.
            RTS = RTS(RDK, robot, gripper)     # Objekt der Klasse RTS wird initialisiert.
    """
        
    def __init__(self, RDK, robot, gripper=False):
        self.RDK = RDK
        self.robot = robot
        self.gripper = gripper
        self.connections = []
        self.whileLoops = []
        self.robot.setAcceleration(1) 
        self.ifConnectionCount = 0
        self.ifConfirmCount = 0
        
    # I/O Funktionen # 

    def addConnection(self, connectionName, link, type):
        """
            Möchte ein Anschluss (digital, analog, seriell) auf dem physischen Roboter genutzt werden,
            muss dieser Anschluss zuerst definiert werden. Dazu ist der zugehörige Link nötigt,
            welcher den Anschluss eindeutig auf dem Roboter zuweist. Wurde bereits ein Anschluss mit 
            dem gewählten Namen initialisiert, wird ein Fehler angezeigt.
            
            Hat keinen Einfluss auf die Simulation.

        Args:
            connectionName (string): Einmaliger Name des Anschlusses (nur für die Programmierung).
            link (string): Link, welcher den Anschluss auf dem Roboter zugewiesen ist.
            type (string): Typ des Anschlusses. Gültig sind "dio" -> digitaler Ein- oder Ausgang, "aio" -> analoger Ein- oder Ausgang, "sio" -> serieller Ein- oder Ausgang.
        
        .. seealso:: :func:`~RTS.checkConnectionName`
        
        Example:
        
            .. code-block:: python
                
                # Initialisiert den Vakuumgreifer mit dem gegebenen Link.
                RTS.addConnection('dVacuum', '98FE10BA-0446-4B8A-A8CF-35B98F42725A', 'dio')   
                      
                # Initialisiert Sensor der Vakuums mit dem gegebenen Link.
                RTS.addConnection('dVacuumSensor', '98FE10BA-0446-4B8A-A8CF-35B98F42725B', 'aio')   
            
        """
        if connectionName not in self.connections:
            if type in lIOTypes:
                self.RDK.RunCode("addConnection('%s','%s','%s')" % (connectionName, link, type))
                self.connections.append(connectionName)
            else:
                debug("Der Anschlusstyp %s ist nicht erlaubt. Benutze dio (digital), aio (analog), sio (serial)." % type)
        else:
            debug("Der Anschluss %s wurde bereits initialisiert, bitte verwende einen anderen Namen." % connectionName)

    #implemented
    def setVacuum(self, bVacuumState, connectionName=False):
        """
            Diese Funktion setzt das Vakuum einerseits in RoboDK (über AttachClosest() und DetachAll()),
            andererseits wird der Ausgang am realen Robotergreifer gesetzt. Wurde vor dem Aufruf dieser Funktion der Greifer
            nicht initialisiert (über setGripperConnection(...)), muss der Anschlussname über die Variable
            connectionName übergeben werden. Wird keine gültige Verbindung angegeben, wird ein Fehler angezeigt. 
            
        Args:
            bVacuumState (bool): Zu setzender Status des Vakuumgreifers.
            connectionName (string, optional): Anschlussname, falls der Greifer nicht über setGripperConnection(...) initialisiert wurde. Defaultwert = False.

        Returns:
            Item: Gibt das angesogene oder losgelassene Teil als Objekt zurück. Nur in der Simulation nutzbar.
        """
        if not self.gripper:
            debug("Initialisiere zuerst den Greifer der Simulation über RTS.setGripper(...).")
        else:
            if not connectionName:
                connectionName = self.gripperConnection
            if self.checkConnectionName(connectionName):
                self.setOutput(connectionName, bVacuumState)
                if bVacuumState:
                    return self.gripper.AttachClosest()
                else:
                    return self.gripper.DetachAll()

    def setOutput(self, connectionName, value):
        """
            Setzt den Anschluss auf einen bestimmten Wert. Wurde der Anschluss nicht initialisiert, wird ein Fehler ausgegeben.
            
            Hat keinen Einfluss auf die Simulation.

        Args:
            connectionName (string): Anschlussname, muss initialisiert sein.
            value ([type]): Wert, auf welchen der Anschluss gesetzt werden soll.
        """
        if self.checkConnectionName(connectionName):
            self.RDK.RunCode("setOutput('%s','%s')" % (connectionName, str(value)))

    # --------- IF-Functions Connection ---------- #

    def ifConnection(self, connectionName, value, condition='=='):
        """
            Erzeugt im Roboterprogramm eine if-Abfrage mit dem gegenen Anschluss und dem bestimmten Wert.
            Wurde der Anschluss nicht initialisiert, wird ein Fehler ausgegeben. Beim Erstellen einer if-Anfrage
            wird eine Variable hochgezählt, welche beim Schliessen der Abfrage wieder heruntergezählt wird. Wurden
            bis am Ende des Programmes nicht alle if-Abfragen geschlossen, wird ein Fehler angezeigt.
            
            Hat keinen Einfluss auf die Simulation. Nach dem Öffnen der Abfrage drüfen KEINE Einzüge
            gemacht werden, wie dies bei einer gewöhnliche if-Abfrage in Python gemacht wird. Damit eine if-Abfrage 
            in das Roboterprogramm geschrieben wird, muss der Inhalt der if-Abfrage in der Simulation zwingend
            ausgeführt werden. Eine if-Abfrage der Simulation (Standard-Python-Abfrage) kann NICHT mit einer if-Abfrage
            über diese Funktion kombiniert werden. Siehe dazu das Beispiel.

        Args:
            connectionName (string): Anschlussname, muss initialisiert sein.
            value ([type]): Der zu vergleichende Wert.
            condition (str, optional): Bedingung der if-Abfrage. Möglich sind "==","!=","<",">","<=",">=". Defaultwert = "==".
            
        .. seealso:: :func:`~RTS.elseIfConnection`, :func:`~RTS.elseConnection`, :func:`~RTS.endIfConnection`, :func:`~RTS.setVacuum`
        
        Example:
        
            .. code-block:: python
                       
                RTS.setVacuum("dVacuum",1)      # Greift ein Teil mit dem initialisierten Vakuumgreifer.
                RTS.ifConnection("dSensor", 1)  # dSensor = initialisierter digitaler Eingang.
                                                # Überprüft, ob der Vakuumgreifer ein Vakuum erzeugt hat.
                                                        
                robot.MoveL(target1)            # Bewegt den Roboter zu target1 (Ablageort des Blocks).   
                RTS.setVacuum("dVacuum",0)      # Lässt das Teil wieder los.

                RTS.elseConnection()
                
                # Folgender Code wird ausgeführt, falls das Vakuum nicht erzeugt wurde.
                RTS.setVacuum("dVacuum",0)      # Vakuum wird wieder deaktiviert, da kein Teil vorhanden.

                RTS.endIfConnection()           # Das Ende der If-Abfrage.
                
                # ACHTUNG: FOLGENDER CODE FUNKTIONIERT NICHT!
                # Der Inhalt der If-Abfrage i==6 wird gar nie in der Simulation ausgeführt.
                # Nur Code, der in der Simulation effektiv ausgeführt wird, kann dem Postprozessor
                # übergeben werden!
                
                var i = 5 
                # Der Inhalt folgender Abfrage wird gar nie erst ausgeführt!
                If i==6:                            
                    RTS.ifConnection("dSensor", 1)  # Es wird geprüft, ob dSensor auf 1 gesetzt ist.
                    robot.MoveL(target1)            # Bewegt den Roboter zum Punkt target1.
                    RTS.endIfConnection()           # Das Ende der If-Abfrage.
        """
        if self.checkConnectionName(connectionName):
            if self.checkCondition(condition):
                self.RDK.RunCode("ifConnection('%s', '%s', '%s')" % (connectionName, value, condition))
                self.ifConnectionCount += 1
    
    def elseIfConnection(self, connectionName, value, condition='=='):
        """
            Ermöglicht das Hinzufügen einer elseIf-Abfrage nach einer if-Abfrage durch RTS.ifConnection(...). Wurde vor dem 
            Aufruf dieser Funktion noch keine if-Abfrage durch RTS.ifConnection(...) geöffnet, wird ein Fehler ausgegeben.
            
            Die Bedingungen dieser Funktion sind identisch mit denen der RTS.ifConnection(...)-Methode. Siehe Abschnitt zwei
            zur Dokumentation von RTS.ifConnection(...).
            
            Hat keinen Einfluss auf die Simulation.
            
        Args:
            connectionName (string): Anschlussname, muss initialisiert sein.
            value ([type]): Der zu vergleichende Wert.
            condition (str, optional): Bedingung des Vergleichs. Möglich sind "==","!=","<",">","<=",">=". Defaultwert = "==".
            
        .. seealso:: :func:`~RTS.ifConnection`, :func:`~RTS.elseConnection`, :func:`~RTS.endIfConnection`
        """
        if self.ifConnectionCount < 1:
            debug("Öffne eine if-Abfrage mit ifConnection(...) vor dem Aufruf von elseIfConnection()")
        else:
            if self.checkConnectionName(connectionName):
                if self.checkCondition(condition):
                    self.RDK.RunCode("elseIfConnection('%s', '%s', '%s')" % (connectionName, value, condition))
    
    def elseConnection(self):
        """
            Fügt eine else-Bedingung hinzu, welche ausgeführt wird, insofern die Bedingung der vorherigen if-Abfrage
            nicht erfüllt wurde. 
            
            Die Bedingungen dieser Funktion sind identisch mit denen der RTS.ifConnection(...)-Methode. Siehe Abschnitt zwei
            zur Dokumentation von RTS.ifConnection(...).
            
            Hat keinen Einfluss auf die Simulation.
            
        .. seealso:: :func:`~RTS.ifConnection`, :func:`~RTS.elseIfConnection`, :func:`~RTS.endIfConnection`
        """
        if self.ifConnectionCount < 1:
            debug("Öffne eine if-Abfrage mit ifConnection(...) vor dem Aufruf von elseConnection()")
        else:
            self.RDK.RunCode("elseConnection()")
    
    def endIfConnection(self): 
        """
            Schliesst eine geöffnete if-Abfrage durch RTS.ifConnection(...). Wurde vor dem Aufruf keine if-Abfrage
            geöffnet, wird ein Fehler angezeigt.
            
            Hat keinen Einfluss auf die Simulation.
            
        .. seealso:: :func:`~RTS.ifConnection`, :func:`~RTS.elseIfConnection`, :func:`~RTS.elseConnection`
        """
        if self.ifConnectionCount < 1:
            debug("Öffne eine if-Abfrage mit ifConnection(...) vor dem Aufruf von endIfConnection()")
        else:
            self.ifConnectionCount -= 1
            self.RDK.RunCode("endIfConnection()")
            
    # --------- IF-Functions User Input ---------- #
    
    def ifConfirm(self, message):
        """
            Erzeugt im Roboterprogramm eine if-Abfrage, welche ein Feld auf dem Robotercontroller öffnet, auf welchem
            man entweder OK (True) oder Abbrechen (False) drücken kann. Beim Erstellen einer if-Anfrage
            wird eine Variable hochgezählt, welche beim Schliessen der Abfrage wieder heruntergezählt wird. Wurden
            bis am Ende des Programmes nicht alle if-Abfragen geschlossen, wird ein Fehler angezeigt.
            
            Die Bedingungen dieser Funktion sind identisch mit denen der RTS.ifConnection(...)-Funktion. Siehe Abschnitt zwei
            zur Dokumentation von RTS.ifConnection(...).
            
            Hat keinen Einfluss auf die Simulation.

        Args:
            message (string): Text, welcher auf dem Robotercontroller angezeigt wird.
            
        .. seealso:: :func:`~RTS.elseConfirm`, :func:`~RTS.endIfConfirm`
            
        Example:
        
            .. code-block:: python
            
                RTS.ifConfirm("Weiter?")  # Erzeugt auf Robotercontroller ein Feld mit Abfrage.
                                          # Führt nachfolgenden Code aus, falls "OK" gedrückt.

                robot.MoveJ(target1)      # Roboter bewegt sich zum Punkt target 1.

                RTS.elseConfirm()         # Führt folgenden Code aus, falls Abfrage abgelehnt wurde.      

                robot.MoveJ(target2)      # Der Roboter bewegt sich zum Punkt target 2.

                RTS.endIfConfirm()        # Das Ende der If-Abfrage.
        """
        self.RDK.RunCode("ifConfirm('%s')" % message)
        self.ifConfirmCount += 1

    def elseConfirm(self):
        """
            Fügt eine else-Bedingung zu, welche ausgeführt wird, insofern die Bedingung der vorherigen if-Abfrage
            durch RTS.ifConfirm(...) nicht erfüllt wurde.
            
            Hat keinen Einfluss auf die Simulation.
            
        .. seealso:: :func:`~RTS.ifConfirm`, :func:`~RTS.endIfConfirm`
        """
        if self.ifConfirmCount < 1:
            debug("Öffne eine if-Abfrage mit ifConfirm(...) vor dem Aufruf von elseConfirm()")
        else:
            self.RDK.RunCode("elseConfirm()")
    
    def endIfConfirm(self): 
        """
            Schliesst eine if-Abfrage, welche durch RTS.ifConfirm(...) geöffnet wurde. Wurde vor dem Aufruf keine if-Abfrage
            geöffnet, wird ein Fehler angezeigt.
            
            Hat keinen Einfluss auf die Simulation.
            
        .. seealso:: :func:`~RTS.ifConfirm`, :func:`~RTS.elseConfirm`
        """
        if self.ifConfirmCount < 1:
            debug("Öffne eine if-Abfrage mit ifConfirm(...) vor dem Aufruf von endIfConfirm()")
        else:
            self.ifConfirmCount -= 1
            self.RDK.RunCode("endIfConfirmCount()")
        
    # ----------- loop ----------- # 
    
    def whileConnection(self, connectionName, value, condition, whileName):
        """
            Erzeugt im Robterprogramm eine While-Schleife mit dem gegenen Anschluss und dem gebenen Wert.
            Gibt es bereits eine While-Schleife mit dem gewählten Namen, wird ein Fehler ausgegeben.
            Wurde der Anschluss nicht initialisiert, wird ein Fehler ausgegeben. Kann in eine bestehende
            while oder for-Schleife der Simulation eingefügt werden, muss dort aber an erster Stelle stehen.
            Kann auch frei stehend implementiert werden.
            
            !!! Funktioniert in einer while oder for-Schleife der
            Simulation NUR, wenn der Inhalt der Schleife unabhängig von einer sich ändernden Variable durch 
            die Schleife ist. Diese ändernde Variable kann zum Beispiel die inkrement-Variable (meistens i) sein.
            Siehe dazu das Beispiel. !!!
         
            Hat keinen Einfluss auf die Simulation.

        Args:
            connectionName (string): Anschlussname, muss initialisiert sein.
            value (int): Wert, mit welchem der Wert des Anschlusses verglichen wird.
            condition (string): Bedingung der While-Schleife. Möglich sind "==","!=","<",">","<=",">=". Defaultwer = "==".
            whileName (string): Eindeutiger Name der Schleife, welche zum Schliessen benötigt wird.
            
        .. seealso:: :func:`~RTS.endWhileConnection`
        
        Example:
        
            .. code-block:: python
            
                # Folgender Code würde auf der Simulation insgesamt 10 mal durchlaufen.
                # Auf dem Roboter läuft dieser Code solange, bis der Eingang dSecuritySensor = 0 ist.
                
                i = 0
                # While-Schleife für die Simulation.
                while i < 11:     
                    # Setzt die Schranken der While-Schleife auf dem Roboter.  
                    # Muss an erster Stelle mit eindeutigem Namen stehen.                 
                    RTS.whileConnection("secWhile", "dSecuritySensor", 0)  
                                                     
                    robot.MoveJ(target1)             # Bewegt den Roboter zu target1.
                    robot.MoveJ(target2)             # Bewegt den Roboter zu target2.
                    i=i+1                            # Zählt die Simulationsinterne Variable hoch.
                    
                # Muss ausserhalb und direkt nach der Simulations-Schleife 
                # mit dem gleichen Namen wie innherhalb der Simulations-Schleife stehen.
                RTS.endWhileConnection("secWhile")   
                                                     
                                                            
                # Es gibt auch die Möglichkeit, Schleifen zu verschachteln.
                # Folgende Schleife wird 50 mal in der Simulation ausgeführt
                # Innerhalb der Schleife wird jedesmal eine andere Schleife mit
                # 3 Durchgängen ausgeführt.
                
                i = 1
                # Äussere While-Schleife der Simulation: 50 Durchgänge.
                while i < 51:                                               
                    # Schranken für das Roboterprogramm der äusserem Schleife
                    # Läuft solange, wie der Eingang dGripper < 5 ist.
                    AROB.whileConnection('dGripper', '<', 5, 'whileTest') 
                                                                            
                    r_tx240.MoveJ(target1)
                    r_tx240.MoveJ(target2)
                    
                    j = 1
                    # Innere While-Schleife: 3 Durchgänge.
                    while j < 4:
                        # Schranken für das Roboterprogramm der inneren Schleife. Läuft solange, 
                        # wie dSecurity < 5 ist.                                    
                        AROB.whileConnection('dSecurity', '<', 5, 'whileTestInner')   
                        r_tx240.MoveJ(target3)
                        r_tx240.MoveJ(target4)
                        j += 1
                        
                    # Ende der inneren While-Schleife.
                    # Muss ausserhalb und direkt nach der Schleife platziert werden.
                    AROB.endWhileConnection('whileTestInner')                          
                                                                                      
                    r_tx240.MoveJ(target4)
                    i += 1
                    
                # Ende der äusseren While-Schleife.
                # Muss ausserhalb und direkt nach der Schleife platziert werden.
                AROB.endWhileConnection('whileTest')                                  
                                                             
                # ACHTUNG: FOLGENDER CODE FUNKTIONIERT NICHT!                         
                # Simulationsschleifen, die abhängig von Variablen sind, welche sich in der
                # Schleife ändern, funktionieren NICHT.
                
                i = 1
                j = 10
                while i<5:
                    AROB.whileConnection('dGripper', '<', 5, 'whileTest')
                    # Bewegung (MoveJ(target[i])) ist abhängig von der Variable i, welche während
                    # der Ausführung hochgezählt wird.
                    robot.MoveJ(target[i])                                   
                    i=i+1
                    # Bewegung (MoveJ(target[j])) ist abhängig von der Variable j, welche während
                    # jedem Durchgang geändert wird.
                    robot.MoveJ(target[j])                                   
                    j=i
                AROB.endWhileConnection('whileTest')
                
        """

        if whileName not in self.whileLoops:
            if self.checkConnectionName(connectionName):
                if self.checkCondition(condition):
                    self.RDK.RunCode("whileConnection('%s', '%s', '%s', '%s')" % (connectionName, condition, value, whileName))
                    self.whileLoops.append(whileName)
        else:
            debug("Es wurde bereits eine While-Schleife mit dem Namen %s verwendet, wähle einen anderen Namen." % name)
    
    def endWhileConnection(self, whileName):
        """
            Schliesst die geöffnete while-Schleife mit dem gegebenenen Namen im Roboterprogramm. Wurde die Schleife innerhalb
            einer Schleife des Simulationsprogrammes geöffnet, muss sie ausserhalb davon (direkt nach dem Beenden der Schleife)
            geschlossen werden. Wurde keine Schleife mit dem gegebenen Namen geöffnet, wird ein Fehler angezeigt.
            
            Hat keinen Einfluss auf die Simulation.
            
        Args:
            whileName (string): Eindeutiger Name der Schleife.
            
        .. seealso:: :func:`~RTS.whileConnection`
        """
        
        
        if whileName in self.whileLoops:
            self.RDK.RunCode("endWhileConnection('%s')" % whileName)
        else:
            debug("Es wurde keine While-Schleife mit dem Namen %s gefunden. Benutze zuerst den Befehl whileConnection(...)" % whileName)
            
    # ----------- Endless-loop ----------- # 
    
    def whileEndless(self, whileName):
        """
            Erzeugt eine Endlosschleife im Roboterprogramm. Gibt es bereits eine While-Schleife mit dem gewählten Namen,
            wird ein Fehler ausgegeben. Beachte: Im Simulationsprogramm sind keine Endlosschleifen möglich,
            da beim Erstellen des Roboterprogrammes die Simulation durchlaufen wird. Daher würde eine Endlosschleife in einem endlos
            langem durchlaufen resultieren, und nie fertig werden.
            
            Hat keinen Einfluss auf die Simulation.

        Args:
            whileName (string): Eindeutiger Name der Schleife, welche zum Schliessen benötigt wird.
            
        .. seealso:: :func:`~RTS.endWhileEndless`
        
        Example:
        
            .. code-block:: python
            
                # Startet eine Endlosschleife. Folgender Code wird unendlich viele Male ausgeführt.
                AROB.whileEndless("endlessWhile")       
                rRobot.MoveJ(target1)                   # Bewegt den Roboter zu target1.
                rRobot.MoveJ(target2)                   # Bewegt den Roboter zu target2.
                # Setzt die Endschranken der Schleife.
                # Da der Start nicht in einer while-Schleife des Simulationsprogrammes liegt,
                # liegt das Ende auf der gleichen Ebene wie der Start.
                AROB.endWhileEndless("endlessWhile")    
                
                # ACHTUNG: FOLGENDER CODE FUNKTIONIERT NICHT!
                # Würde man folgendes Roboterprogramm generieren, würde die Simulation diese Schleife
                # zuerst unendlich lange mal durchlaufen, bis daraus dann das Roboterprogramm
                # generiert werden kann. Dies ist nicht möglich.
                
                # Erzeugt in der Simulation eine Endlosschleife
                while True:                              
                    # Startet eine Endlosschleife. Folgender Code wird unendlich viele Male ausgeführt.
                    AROB.whileEndless("endlessWhile")     
                    rRobot.MoveJ(target1)                   # Bewegt den Roboter zu target1.
                    rRobot.MoveJ(target2)                   # Bewegt den Roboter zu target2.
                # Setzt die Endschranken der Schleife.
                # Muss ausserhalb und direkt nach der Schleife platziert werden.  
                AROB.endWhileEndless("endlessWhile")    
        """
        if whileName not in self.whileLoops:
            self.RDK.RunCode("whileEndless('%s')" % whileName)
            self.whileLoops.append(whileName)
        else:
            debug("Es wurde bereits eine While-Schleife mit dem Namen %s verwendet, wähle einen anderen Namen." % name)
    
    def endWhileEndless(self, whileName):
        """
            Schliesst die geöffnete Endlos-Schleife mit dem gegebenenen Namen im Roboterprogramm. 

            Hat keinen Einfluss auf die Simulation.
            
        Args:
            whileName (string): Eindeutiger Name der Schleife.
            
        .. seealso:: :func:`~RTS.whileEndless`
        """
        if whileName in self.whileLoops:
            self.RDK.RunCode("endWhileEndless('%s')" % whileName)
        else:
            debug("Es wurde keine While-Schleife mit dem Namen %s gefunden. Benutze zuerst den Befehl whileConnection(...)" % whileName)
        
    # ----------- Wait ----------- #

    def waitConnection(self, connectionName, value, timeout=-1, condition="=="):
        """
            Erzwingt im Roboterprogramm ein Warten auf den gegebenen Anschluss, solange bis dieser entweder der gegebenen
            Bedingung entspricht, oder das Timeout abgelaufen ist.
            
            Wird idealerweise mit einer If-Abfrage eines Anschlusses kombiniert. Siehe dazu das Beispiel 2.
        
            Hat keinen Einfluss auf die Simulation.

        Args:
            connectionName (string): Anschlussname, muss zwingend initialisiert sein.
            value (int): Wert, mit welchem der Wert des Anschlusses verglichen wird.
            timeout (int, optional): Wartezeit in Sekunden. -1 entspricht unendlich lange. Defaultwert = -1.
            condition (string, optional): Bedingung der Abfrage. Möglich sind "==","!=","<",">","<=",">=".  Defaultwert = '=='
            
        .. seealso:: :func:`~RTS.setVacuum`, :func:`~RTS.ifConnection`
        
        Example:
        
            .. code-block:: python
            
                # Beispiel 1:
            
                robot.MoveL(target1)                 # Bewegt den Roboter zu Punkt target1.

                RTS.setVacuum(1)                     # Aktiviert den Vakuumgreifer.
                RTS.waitConnection("dSensor", 1, 5)  # Wartet, bis der Vakuumsensor ein Vakuum erkannt
                                                     # hat. Wird kein Vakuum erkannt (kein Block
                                                     # wurde angesaugt), wird nach 5 Sekunden mit dem
                                                     # Programm weitergefahren.
                                                            
                robot.MoveL(target2)                 # Bewegt den Roboter zu Punkt target2.
                
                # Beispiel 2: Kombination mit ifConnection(...)
                robot.MoveL(target1)                 # Bewegt den Roboter zu Punkt target1.

                RTS.setVacuum(1)                     # Aktiviert den Vakuumgreifer.
                RTS.waitConnection("dSensor", 1, 5)  # Wartet solange, bis der Vakuumsensor ein Vakuum
                                                     # erkannt hat. Wird kein Vakuum erkannt
                                                     # (kein Block wurde angesaugt), wird nach
                                                     # 5 Sekunden mit dem Programm weitergefahren.
                                                     
                RTS.ifConnection("dSensor", 1)       # Es wird geprüft, ob der Vakuumsensor ein Vakuum
                                                     # erkannt hat. waitConnection(...) wartet nur auf 
                                                     # einen Eingang, knüpft diesen aber an keine 
                                                     # Bedingungen, daher kann mit einer nachfolgenden
                                                     # Abfrage diese Bedingung hergestellt werden.
                                                     
                robot.MoveL(target3)                 # Bewegt den Roboter zum Punkt target3.
                                                     # ! Nur wenn das Vakuum vorhanden ist.
                RTS.endIfConnection()                # Das Ende der If-Abfrage.                    
                
                
        """
        if self.checkConnectionName(connectionName):
            self.RDK.RunCode("waitConnection('%s', '%s', '%s', %d)" % (connectionName, str(value), condition, timeout))


    # ----- checkFunctions ------ #
    def checkConnectionName(self, connectionName):
        """
            Prüft, ob ein Anschluss bereits initialisiert wurde. Gibt eine Fehlermeldung aus, falls dies nicht der
            Fall ist. Wird nur Library-Intern verwendet.
        
            Hat keinen Einfluss auf die Simulation.
            
        Args:
            connectionName (string): Anschlussname

        Returns:
            bool: 1 falls initialisiert, 0 falls nicht initialisiert.
        """
        if connectionName not in self.connections:
            debug("Der Anschluss mit dem Namen %s wurde noch nicht initialisiert. Verwende dazu addConnection(...)." % connectionName)
            return 0
        else:
            return 1
        
    def checkCondition(self, condition):
        """
            Prüft ob eine gegebene Kondition für Abfragen (if, while, wait) in der Liste der möglichen Konditionen
            enthalten ist. Wird nur Library-Intern verwendet.

            Hat keinen Einfluss auf die Simulation.
            
        Args:
            condition (string): Die zu überprüfende Kondition.

        Returns:
            bool: 1 falls in der Liste, 0 falls nicht in der Liste.
        """
        if condition not in conditions:
            debug("Condition %s is no valid Condition. Use %s" % (condition, ', '.join(conditions)))
            return 0
        else:
            return 1

    # ---------------------- # 
    # Messages on controller # 
    
    def boxAlert(self, sMessage):
        """
            Zeigt einerseits in RoboDK einen Text an, und öffnet auf dem Robotercontroller
            einen Textbox mit dem gegebenen Text.

        Args:
            sMessage (string): Nachricht, welche angezeigt werden soll.
        """
        mbox(sMessage)
        self.RDK.RunCode("boxAlert('%s')" % sMessage)
           
    # --------------- #
    # RobotSettings #    
    
    def setAccelerationPercentageJoints(self, percent):
        """
            Setzt die Beschleunigung der Achsen des Roboters in % der Nennbeschleunigung. 

            Hat keinen Einfluss auf die Simulation.
            
        Args:
            percent (int): Prozent der Nennbeschleunigung.
            
        .. seealso:: :func:`~RTS.setMovementParameter`
        """
        if percent >= 0 and percent <= 100:
            self.RDK.RunCode("setAccelerationPercentageJoints('%s')" % percent)
        else: 
            debug("Der Wert von setAccelerationPercentageJoints muss zwischen 0 und 100 liegen.")
        
    def setDeccelerationPercentageJoints(self, percent):
        """Setzt die Verzögerung der Achsen des Roboters in % der Nennverzögerung. 

            Hat keinen Einfluss auf die Simulation.
            
        Args:
            percent (int): Prozent der Nennverzögerung.
            
        .. seealso:: :func:`~RTS.setMovementParameter`
        """
        if percent >= 0 and percent <= 100:
            self.RDK.RunCode("setDeccelerationPercentageJoints('%s')" % percent)
        else: 
            debug("Der Wert von setDeccelerationPercentageJoints muss zwischen 0 und 100 liegen.")
        
    def setSpeedPercentageJoints(self, percent):
        """
            Setzt die lineare Geschwindigkeit der Achsen des Roboters in % der Nenngeschwindigkeit. 

            Hat keinen Einfluss auf die Simulation.

        Args:
            percent (int): Prozent der Nenngeschwindigkeit.
            
        .. seealso:: :func:`~RTS.setMovementParameter`
        """
        if percent >= 0 and percent <= 100:
            self.RDK.RunCode("setSpeedPercentageJoints('%s')" % percent)
        else: 
            debug("Der Wert von setSpeedPercentageJoints muss zwischen 0 und 100 liegen.")
        
    def setTranslationalSpeedTool(self, speed):
        """
            Setzt die maximale lineare Geschwindigkeit des Tools in mm/s.

            Hat keinen Einfluss auf die Simulation.
            
        Args:
            percent (int): Maximale lineare Geschwindigkeit in mm/s.
            
        .. seealso:: :func:`~RTS.setMovementParameter`
        """
        self.RDK.RunCode("setTranslationalSpeedTool('%s')" % speed)
        
    def setRotationalSpeedTool(self, speed):
        """
            Setzt die maximale rotative Geschwindigkeit des Tools in deg/s.

            Hat keinen Einfluss auf die Simulation.
        
        Args:
            percent (int): Maximale rotative Geschwindigkeit in deg/s.
            
        .. seealso:: :func:`~RTS.setMovementParameter`
        """
        self.RDK.RunCode("setRotationalSpeedTool('%s')" % speed)
        
    def setMovementParameter(self, accel_joints = -1, deccel_joints = -1, speed_joints = -1, trans_tool = -1, rot_tool = -1):
        """
            Setzt die Beschleunigung der Achsen des Roboters in % der Nennbeschleunigung, die Verzögerung der
            Achsen des Roboters in % der Nennverzögerung, die lineare Geschwindigkeit der
            Achsen des Roboters in % der Nenngeschwindigkeit, die maximale lineare Geschwindigkeit des Tools in mm/s,
            die maximale rotative Geschwindigkeit des Tools in deg/s. Wird ein Wert nicht gesetzt, wird er nicht in das
            Roboterprogramm geschrieben.

            Hat keinen Einfluss auf die Simulation.

        Args:
            accel_joints (int, optional): Prozent der Nennbeschleunigung. Defaultwert = -1.
            deccel_joints (int, optional): Prozent der Nenngeschwindigkeit. Defaultwert = -1.
            speed_joints (int, optional): Prozent der Nenngeschwindigkeit. Defaultwert = -1.
            trans_tool (int, optional): Maximale lineare Geschwindigkeit in mm/s. Defaultwert = -1.
            rot_tool (int, optional): Maximale rotative Geschwindigkeit in deg/s. Defaultwert = -1.
            
        .. seealso:: :func:`~RTS.setAccelerationPercentageJoints`, :func:`~RTS.setDeccelerationPercentageJoints`, :func:`~RTS.setSpeedPercentageJoints`, :func:`~RTS.setTranslationalSpeedTool`, :func:`~RTS.setRotationalSpeedTool`
        """
        if accel_joints != -1:
            self.setAccelerationPercentageJoints(accel_joints)
        if deccel_joints != -1:
            self.setDeccelerationPercentageJoints(deccel_joints)
        if speed_joints != -1:
            self.setSpeedPercentageJoints(speed_joints)
        if trans_tool != -1:
            self.setTranslationalSpeedTool(trans_tool)
        if rot_tool != -1:
            self.setRotationalSpeedTool(rot_tool)
    
    # --------------- #
    # Other functions #    
    
    #implemented
    def Pause(self, time):
        """
            Stoppt die Simulation und den Roboter für die gebenene Anzahl Sekunden.

        Args:
            nSeconds (int): Wartezeit in Sekunden.
        """
        pause(2)
        self.robot.Pause(time*1000)

    # ------- #
    # Helpers #  
    
    def setGripper(self, gripper):
        """
            Setzt den Greifer nachträglich. Nur wichtig für die Simulation.

        Args:
            gripper (Item): Greifer des Roboters.
        """
        self.gripper = gripper

    def setGripperConnection(self, connectionName):
        """
            Setzt den Greifer des realen Roboters auf einen definierten Anschluss. 
            Wurde der Anschluss nicht initialisiert, wird ein Fehler ausgegeben.
            
            Hat keinen Einfluss auf die Simulation.

        Args:
            connectionName (string): Anschlussname, muss initialisiert sein.
            
        .. seealso:: :func:`~RTS.addConnection`
        
        Example:
        
            .. code-block:: python
                
                # Initialisiert den Vakuumgreifer mit dem gegebenen Link.
                RTS.addConnection('dVacuum', '98FE10BA-0446-4B8A-A8CF-35B98F42725A', 'dio')
                RTS.setGripperConnection('dVacuum')
        """
        if self.checkConnectionName(connectionName):
            self.gripperConnection = connectionName
            self.RDK.RunCode("setGripperConnection('%s')" % self.gripperConnection)

def debug(message):
    """
        Öffnet eine Textbox in der Simulation.

    Args:
        message (string): Auszugebende Nachricht.
    """
    caller = getframeinfo(stack()[-1][0])
    mbox("%s:%d - %s" % (caller.filename, caller.lineno, message)) # python3 syntax print


# Replace the mbox-function with a intern mbox-function. Has only an effect on Mac OS #
try:
    mbox
except NameError:
    def mbox(message):
        """
            Öffnet eine Textbox in der Simulation. Nur nötig für MacOS-Systeme.

        Args:
            message (string): Auszugebende Nachricht.
        """
        os.system("osascript -e 'Tell application \"System Events\" to display dialog \""+message+"\"'")
else:
    print("In scope!")
            