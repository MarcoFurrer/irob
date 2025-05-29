class JengaPiece:
    """Repräsentiert einen einzelnen Jenga-Stein mit seinen Eigenschaften"""
    
    def __init__(self, rdk, number):
        self.number = number
        self.rdk = rdk
        self.piece = rdk.Item(f"Jengastuck {number}")
        
        # Geometrische Eigenschaften des Jenga-Steins
        self.length = 75
        self.width = 25.5
        self.height = 15
        
        if not self.piece.Valid():
            raise Exception(f"Jenga piece {number} not found in RoboDK")
    
    def attach_to_frame(self, frame):
        """Befestigt den Stein statisch an einem Frame (für Turmbau)"""
        self.piece.setParentStatic(frame)
    
    def __str__(self):
        """String-Darstellung für Debugging und Logging"""
        return f"JengaPiece({self.number})"
    
    def __repr__(self):
        """Entwickler-Darstellung des Objekts"""
        return f"JengaPiece(number={self.number})"


class JengaPieceCollection:
    """Sammlung aller Jenga-Steine mit komfortablen Zugriffsmethoden"""
    
    def __init__(self, rdk, count=15):
        """Initialisiert Sammlung mit spezifizierter Anzahl Steine"""
        self.rdk = rdk
        # Erstellt Liste aller Jenga-Steine
        self.pieces = [JengaPiece(rdk, i) for i in range(1, count + 1)]
    
    def __len__(self):
        """Unterstützt len()-Funktion für Anzahl Steine"""
        return len(self.pieces)
    
    def __iter__(self):
        """Ermöglicht Iteration über alle Steine in numerischer Reihenfolge"""
        return iter(self.pieces)