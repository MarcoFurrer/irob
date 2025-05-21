# jenga_piece.py

class JengaPiece:
    def __init__(self, position, orientation, number):
        """
        position: [x, y, z]
        orientation: [rx, ry, rz] in degrees
        """
        self.position = position
        self.orientation = orientation
        self.number = number

    def get_pose(self):
        """Returns the full pose as a 6-element list (xyz + rpy)"""
        return self.position + self.orientation
