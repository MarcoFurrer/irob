# tower.py

import numpy as np
from jenga_piece import JengaPiece

class Tower:
    def __init__(self, frame_origin):
        """
        frame_origin: [x, y, z] Position des Turm-Referenzpunkts
        """
        self.frame_origin = np.array(frame_origin)

        self.jenga_width = 25
        self.jenga_length = 75
        self.jenga_height = 15
        self.middle_offset = 20

        # Versatz relativ zum Referenzpunkt
        self.offset_x = 70.711 - self.jenga_length / 2
        self.offset_y = 70.711 - self.jenga_length / 2

        self.counter = 0
        self.max_pieces = 15

    def get_next_target(self):
        """Gibt die nächste Zielposition auf dem Turm zurück"""

        if self.counter >= self.max_pieces:
            raise StopIteration("Turm ist voll.")

        layer = self.counter // 3 + 1  # 3 Steine pro Schicht

        # Unterscheidung zwischen geraden/ungeraden Schichten
        if layer % 2 == 0:
            # Gerade Schicht – Steine quer
            x = self.frame_origin[0] + self.offset_x + self.jenga_width * (self.counter % 3)
            y = self.frame_origin[1] + self.offset_y - self.middle_offset
            z = self.frame_origin[2] + self.jenga_height * (layer - 1)
            orientation = [0, 180, -90]
        else:
            # Ungerade Schicht – Steine längs
            x = self.frame_origin[0] + self.offset_x - self.middle_offset
            y = self.frame_origin[1] + self.offset_y + self.jenga_width * (self.counter % 3)
            z = self.frame_origin[2] + self.jenga_height * (layer - 1)
            orientation = [0, 180, 180]

        self.counter += 1
        return JengaPiece([x, y, z], orientation, number=self.counter)
