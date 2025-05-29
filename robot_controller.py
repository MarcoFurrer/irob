# Robotersteuerung für Staubli TX2-40 mit RTS-System
# Verwaltet Bewegungsabläufe, Greifer-Funktionen und Koordinatentransformationen

from RTS import RTS

class RobotController:
    """Zentrale Robotersteuerung für Bewegungskoordination"""
    
    def __init__(self, rdk):
        self.rdk = rdk
        
        # Initialisierung der Hardware-Komponenten
        self.robot = rdk.Item('Staubli TX2-40')
        self.tool = rdk.Item('AROB_LWS_VakuumGreifer_14')
        self.world_frame = rdk.Item("World")
        
        # RTS-System für Vakuum-Greifer-Steuerung
        self.rts = RTS(rdk, self.robot, self.tool)
        self.rts.addConnection('dVacuum', '98FE10BA-0446-4B8A-A8CF-35B98F42725A', 'dio')
        self.rts.setGripperConnection('dVacuum')
        self.rts.addConnection('dVaccumSensor', '98FE10BA-0446-4B8A-A8CF-35B98F42725B', 'aio')
        
        # Standard-Gelenkpositionen für sichere Bewegungen
        self.t_home = [0, 50, 50, 0, 60, 0]    # Home-Position für sichere Übergänge
        self.t_start = [0, 0, 90, 0, 90, 0]    # Start-Position für Initialisierung
        
        # Validierung der RoboDK-Komponenten
        if not self.robot.Valid():
            raise Exception("Robot 'Staubli TX2-40' not found in RoboDK")
        if not self.tool.Valid():
            raise Exception("Tool 'AROB_LWS_VakuumGreifer_14' not found in RoboDK")
    
    def initialize(self):
        """Initialisiert Roboter in definierte Ausgangslage"""
        self.robot.setJoints(self.t_start)
        self.robot.setPoseFrame(self.world_frame)
        self.robot.setSpeed(50, 50, 50, 75)  # Standard-Geschwindigkeitsprofile
    
    def move_to_home(self):
        """Bewegt Roboter in sichere Home-Position"""
        self.robot.MoveJ(self.t_home)
    
    def pick_piece(self, piece, pick_above_poses, pick_poses, speed=10):
        """Aufnahme eines Jenga-Steins aus dem Magazin"""
        print(f"Picking up piece {piece.number}")
        
        # Sicherheitsbewegung über Home-Position
        self.move_to_home()
        
        # Positionierung oberhalb des Zielsteins
        self.robot.MoveJ(pick_above_poses[f"Jenga{piece.number}above"])
        
        # Präzisionsbewegung mit reduzierter Geschwindigkeit
        self.robot.setSpeed(speed)
        
        # Anfahren der Greifposition und Aktivierung des Vakuums
        self.robot.MoveL(pick_poses[f"Jenga{piece.number}"])
        self.rts.setVacuum(1, "dVacuum")
        
        # Zurückfahren in sichere Höhe
        self.robot.MoveL(pick_above_poses[f"Jenga{piece.number}above"])
        
        # Geschwindigkeit für nachfolgende Bewegungen zurücksetzen
        self.robot.setSpeed(50)
    
    def place_piece(self, piece, place_above_pose, place_pose, tower_frame, speed=10):
        """Platzierung eines Jenga-Steins auf dem Turm"""
        print(f"Placing piece {piece.number}")
        
        # Sicherheitsbewegung über Home-Position
        self.move_to_home()
        
        # Anfahren der Position oberhalb des Zielplatzes
        self.robot.MoveJ(place_above_pose)
        
        # Präzisionsplatzierung mit reduzierter Geschwindigkeit
        self.robot.setSpeed(speed)
        
        # Absetzen des Steins und Deaktivierung des Vakuums
        self.robot.MoveL(place_pose)
        self.rts.setVacuum(0, "dVacuum")
        
        # Statische Befestigung des Steins am Tower-Frame
        piece.attach_to_frame(tower_frame)
        
        # Zurückfahren und Rückkehr zur Home-Position
        self.robot.MoveL(place_above_pose)
        self.robot.setSpeed(50)
        self.move_to_home()
    
    def move_piece(self, piece, magazine, tower, pick_above_poses, pick_poses, speed=10):
        """Vollständiger Bewegungsablauf: Aufnahme aus Magazin und Platzierung im Turm"""
        print(f"Moving piece {piece.number} from magazine to tower")
        
        # Phase 1: Aufnahme aus dem Magazin
        self.pick_piece(piece, pick_above_poses, pick_poses, speed)
        
        # Phase 2: Berechnung der Zielposition im Turm
        place_above, place = tower.get_placement_pose(piece)
        
        # Phase 3: Platzierung im Turm
        self.place_piece(piece, place_above, place, tower.frame, speed)