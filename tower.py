from jenga_piece import JengaPiece
import numpy as np

class Tower:
    def __init__(self, name="TowerFrame", rdk=None)->list:
        """
        frame_origin: [x, y, z] Position des Turm-Referenzpunkts
        """
        self.frame = rdk.Item(name)
        # Name() Pose()

        # Versatz relativ zum Referenzpunkt
        self.offset_x = 70.711 
        self.offset_y = 70.711
        self.offset_z = 0

        self.max_pieces = 15
        
        self.frame = rdk.Item(name)

    def get_next_target(self, piece: JengaPiece):
        """Gibt die nächste Zielposition auf dem Turm zurück, basierend auf der Schicht- und Blocklogik."""

        if piece.number >= self.max_pieces:
            raise StopIteration("Turm ist voll.")

        layer = piece.number // 3  # Ebene (0-basiert)
        index_in_layer = piece.number % 3
        is_even_layer = (layer % 2 == 0)


        return [
            index_in_layer * piece.width + self.offset_x if is_even_layer else self.offset_x,
            self.offset_y if is_even_layer else self.offset_y + index_in_layer * piece.width, 
            self.offset_z + layer * piece.height, 
            0, 
            0, 
            np.pi / 2 if is_even_layer else 0
        ]