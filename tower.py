# tower.py

import numpy as np
from jenga_piece import JengaPiece

class Tower:
    def __init__(self, frame_origin, name="TowerFrame", rdk=None)->list:
        """
        frame_origin: [x, y, z] Position des Turm-Referenzpunkts
        """
        self.frame_origin = np.array(frame_origin)
        self.frame = rdk.Item(name)
        # Name() Pose()

        # Versatz relativ zum Referenzpunkt
        self.offset_x = 70.711 
        self.offset_y = 70.711
        self.offset_z = 

        self.max_pieces = 15
        
        self.frame = rdk.Item(name)

def get_next_target(self, piece: JengaPiece):
    """Gibt die nächste Zielposition auf dem Turm zurück, basierend auf der Schicht- und Blocklogik."""

    if piece.number >= self.max_pieces:
        raise StopIteration("Turm ist voll.")

    layer = piece.number // 3  # Ebene (0-basiert)
    index_in_layer = piece.number % 3

    # Z-Höhe (Blockmitte)
    z = self.frame_origin[2] + (layer + 1) * piece.height - piece.height / 2

    return [
        index_in_layer * piece.width + self.offset_x, 
        self.offset_y, 
        self.offset_z + layer * piece.height, 
        0, 
        0, 
        0
    ]
    if layer % 2 != 0:
        # Ungerade Layer im ursprünglichen Code: Y-orientiert, rotiert um pi/2
        x = self.frame_origin[0]
        y = self.frame_origin[1] + piece.width * (1 - index_in_layer)
        rz = np.pi / 2
    else:
        # Gerade Layer: X-orientiert, rotiert um pi
        x = self.frame_origin[0] + piece.width * (1 - index_in_layer)
        y = self.frame_origin[1]
        rz = np.pi

    # self.counter += 1

    position = [x, y, z]
    orientation = [0, 0, rz]
    return JengaPiece(position, orientation, number=self.counter)


    # def get_next_target(self, piece: JengaPiece):
        # """Gibt die nächste Zielposition auf dem Turm zurück"""

        # if self.counter >= self.max_pieces:
            # raise StopIteration("Turm ist voll.")

        # layer = self.counter // 3 + 1  # 3 Steine pro Schicht

        # Unterscheidung zwischen geraden/ungeraden Schichten
        # if layer % 2 == 0:
            # Gerade Schicht – Steine quer
            # x = self.frame_origin[0] + self.offset_x + piece.width * (self.counter % 3)
            # y = self.frame_origin[1] + self.offset_y - self.middle_offset
            # z = self.frame_origin[2] + piece.height * (layer - 1)
            # orientation = [0, 180, -90]
        # else:
            # Ungerade Schicht – Steine längs
            # x = self.frame_origin[0] + self.offset_x - self.middle_offset
            # y = self.frame_origin[1] + self.offset_y + piece.width * (self.counter % 3)
            # z = self.frame_origin[2] + piece.height * (layer - 1)
            # orientation = [0, 180, 180]

        # self.counter += 1
        # return JengaPiece([x, y, z], orientation, number=self.counter)
