from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

class Magazine:
    """Verwaltet Magazin-Frame und Stein-Positionierung für Aufnahme"""
    
    def __init__(self, rdk, frame_name="MagazinFrame"):
        self.rdk = rdk
        self.frame = rdk.Item(frame_name)
        
        # Optimierte Offset-Parameter für präzise Stein-Aufnahme
        self.offset_x = 72.5
        self.offset_y_first_row = 97.5
        self.offset_y_second_row = 172.5
        self.z_offset = 15              
        self.z_pick = 15                
        
        # Magazin-Layout: 8 Steine in erster Reihe, 7 in zweiter Reihe
        self.count_first_row = 8
        self.count_second_row = 7
        
        if not self.frame.Valid():
            raise Exception(f"Magazine frame '{frame_name}' not found in RoboDK")
    
    def get_pick_positions(self):
        """Generiert alle Aufnahmepositionen für Steine im Magazin"""
        pick_above, pick = {}, {}
        
        # Erste Reihe: Steine 1-8 mit 25mm Abstand
        for i in range(self.count_first_row):
            piece_num = i + 1
            
            # Position oberhalb des Steins für sichere Anfahrt
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(
                    self.offset_x + i * 25,
                    self.offset_y_first_row, 
                    self.z_offset
                    ) * 
                rotx(pi)  # 180° Rotation für korrekte Greifer-Orientierung
            )
            
            # Direkte Aufnahmeposition des Steins
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(self.offset_x + i * 25, 
                       self.offset_y_first_row, 
                       self.z_pick
                       ) * 
                rotx(pi)
            )
        
        # Zweite Reihe: Steine 9-15 mit identischem Raster
        for i in range(self.count_second_row):
            piece_num = i + 9
            
            # Position oberhalb des Steins
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(self.offset_x + i * 25, 
                       self.offset_y_second_row, 
                       self.z_offset
                       ) * 
                rotx(pi)
            )
            
            # Aufnahmeposition
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(self.offset_x + i * 25, 
                       self.offset_y_second_row, 
                       self.z_pick
                       ) * 
                rotx(pi)
            )
        
        return pick_above, pick