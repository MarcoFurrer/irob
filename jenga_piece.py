class JengaPiece:
    def __init__(self,rdk, number, orientation=[0, 0, 0]):
        """
        position: [x, y, z]
        orientation: [rx, ry, rz] in degrees
        """
        self.orientation = orientation
        self.number = number
        self.width = 25
        self.length = 75
        self.height = 15
        self.piece = rdk.Item(f"jengastuck{number}")

    
if __name__ == "__main__":
    from robodk import robolink

    rdk = robolink.Robolink()
    jenga_piece = JengaPiece(rdk, 1)
    
    # Ausgabe der Eigenschaften des Jenga-Stücks
    print(f"Jenga-Stück {jenga_piece.number}:")
    print(f"Position: {jenga_piece.piece.Pose()}")
    print(f"Orientierung: {jenga_piece.orientation}")

