# magazine.py

import numpy as np
from jenga_piece import JengaPiece

class Magazine:
    def __init__(self, name="MagazineFrame", rdk=None):
        """
        frame_origin: [x, y, z] Position des Magazin-Referenzpunktes
        offset_x, offset_y: Abstand der ersten Steinposition vom Rahmen
        """

        self.middle_offset = 20

        self.counter = 0
        self.max_pieces = 15
        
        self.frame = rdk.Item(name)

if __name__ == "__main__":
    from robodk import robolink
    rdk = robolink.Robolink()
    magazine = Magazine(rdk=rdk)
    print(f"Magazine frame: {magazine.frame.Name()} at {magazine.frame.Pose()}")
        
        