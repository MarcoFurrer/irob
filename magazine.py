# magazine.py

import numpy as np
from jenga_piece import JengaPiece

class Magazine:
    def __init__(self, frame_origin, offset_x=40, offset_y=60):
        """
        frame_origin: [x, y, z] Position des Magazin-Referenzpunktes
        offset_x, offset_y: Abstand der ersten Steinposition vom Rahmen
        """
        self.frame_origin = np.array(frame_origin)
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.jenga_width = 25
        self.jenga_length = 75
        self.jenga_height = 15
        self.middle_offset = 20

        self.counter = 0
        self.max_pieces = 15

    def get_next_piece(self):
        """Gibt die nächste Position für einen Jenga-Stein im Magazin zurück"""

        if self.counter >= self.max_pieces:
            raise StopIteration("Keine weiteren Steine im Magazin.")

        # Basisposition berechnen
        base_x = self.frame_origin[0] - (60 - self.middle_offset) - self.jenga_length / 2
        base_y = self.frame_origin[1] + self.offset_y + self.jenga_width / 2
        base_z = self.frame_origin[2] + self.jenga_height

        if self.counter == 0:
            pos = [base_x, base_y, base_z]
        elif (self.counter+1) % 2 == 0:
            pos = [base_x, base_y + (self.counter // 2) * self.jenga_width, base_z]
        else:
            pos = [base_x - self.jenga_length, base_y + (self.counter // 2) * self.jenga_width, base_z]

        self.counter += 1
        orientation = [0, 180, 0]
        return JengaPiece(pos, orientation, self.counter)