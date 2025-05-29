from robodk.robomath import *

class Tower:
    """Verwaltet Tower-Frame und Stein-Platzierung mit dynamischer Formel"""
    
    def __init__(self, rdk, frame_name="TowerFrame"):
        self.rdk = rdk
        self.frame = rdk.Item(frame_name)
        
        if not self.frame.Valid():
            raise Exception(f"Tower frame '{frame_name}' not found in RoboDK")
        
        # Turm-Basisposition relativ zum Frame-Ursprung
        self.base_x = 0      
        self.base_y = 70     
        self.base_z = 5     
    
    def calculate_piece_position(self, piece):
        """
        Berechnet Position für Jenga-Stein mit dynamischer Formel
        Rückgabe: (x_offset, y_offset, z, rotation_z)
        
        Jenga-Turm-Logik:
        - Gerade Layer (0,2,4...): Steine entlang X-Achse, Verteilung in Y-Richtung
        - Ungerade Layer (1,3,5...): Steine entlang Y-Achse, Verteilung in X-Richtung
        - Rotation bestimmt Ausrichtung und Abstandsberechnung zwischen Steinen
        """
        # Konvertierung zu 0-basiertem Index für Berechnungen
        piece_index = piece.number - 1
        
        # Berechnung Layer (0-basiert) und Position innerhalb des Layers
        layer = piece_index // 3
        index_in_layer = piece_index % 3
        
        # Bestimmung ob gerader oder ungerader Layer (alternierende Orientierungen)
        is_even_layer = (layer % 2 == 0)
        
        # Z-Position basierend auf Layer-Höhe und Stein-Eigenschaften
        z = (layer + 1) * piece.height + self.base_z
        
        if is_even_layer:
            # Gerade Layer: Steine horizontal entlang X-Achse ausgerichtet
            # 90° Rotation: Steine werden in Y-Richtung mit WIDTH-Abstand verteilt
            x_offset = 0
            y_offset = (index_in_layer - 1) * piece.width  # Muster: -WIDTH, 0, +WIDTH
            rotation_z = pi/2  # 90 Grad Rotation
        else:
            # Ungerade Layer: Steine vertikal entlang Y-Achse ausgerichtet  
            # 0° Rotation: Steine werden in X-Richtung mit WIDTH-Abstand verteilt
            x_offset = (index_in_layer - 1) * piece.width # Muster: -WIDTH, 0, +WIDTH
            y_offset = 0
            rotation_z = 0  # 0 Grad Rotation (natürliche Ausrichtung)
        
        return x_offset, y_offset, z, rotation_z
    
    def get_placement_pose(self, piece, hover_height=30):
        """Berechnet Platzierungs-Pose für Jenga-Stein mit dynamischer Formel"""
        # Positionsberechnung basierend auf Stein-Objekt
        piece_number = piece.number
        
        x_offset, y_offset, z, rotation_z = self.calculate_piece_position(piece)
        
        # Berechnung absoluter Positionen im Tower-Frame
        abs_x = self.base_x + x_offset
        abs_y = self.base_y + y_offset
        abs_z = z
        
        # Erstellung der Ziel-Posen mit Koordinatentransformation
        place_above = (
            self.frame.Pose() * 
            transl(abs_x, abs_y, abs_z + hover_height) * 
            rotz(rotation_z) * 
            rotx(pi)  # 180° Rotation für korrekte Greifer-Orientierung
        )
        
        place = (
            self.frame.Pose() * 
            transl(abs_x, abs_y, abs_z) * 
            rotz(rotation_z) * 
            rotx(pi)  # 180° Rotation für korrekte Greifer-Orientierung
        )
        
        return place_above, place
    
    def get_layer_for_piece(self, piece):
        """Bestimmt Layer-Nummer (0-basiert) für gegebenen Jenga-Stein"""
        return (piece.number - 1) // 3
    
