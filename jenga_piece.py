class JengaPiece:
    """Represents a single Jenga piece"""
    
    def __init__(self, rdk, number):
        self.number = number
        self.rdk = rdk
        self.piece = rdk.Item(f"Jengastuck {number}")
        
        if not self.piece.Valid():
            raise Exception(f"Jenga piece {number} not found in RoboDK")
    
    def attach_to_frame(self, frame):
        """Attach this piece to a specific frame (used for tower building)"""
        self.piece.setParentStatic(frame)