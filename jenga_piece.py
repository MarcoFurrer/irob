# jenga_piece.py


class JengaPiece:
    def __init__(self,rdk, number):
        """
        position: [x, y, z]
        orientation: [rx, ry, rz] in degrees
        """
        self.number = number
        self.width = 25
        self.length = 75
        self.height = 15
        self.piece = rdk.Item(f"AROB_Jengastuck{number}")
        # Pose() und Name()
    





