from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

class Magazine:
    """Handles magazine frame and piece positioning"""
    
    def __init__(self, rdk, frame_name="MagazinFrame"):
        self.rdk = rdk
        self.frame = rdk.Item(frame_name)
        self.offset_x = 72.5  # Reduced from 40
        self.offset_y_first_row = 97.5  # Reduced from 60
        self.offset_y_second_row = 172.5  # Reduced from 120
        self.z_offset = 15
        self.z_pick = 15
        self.count_first_row = 8
        self.count_second_row = 7
        
        
        if not self.frame.Valid():
            raise Exception(f"Magazine frame '{frame_name}' not found in RoboDK")
    
    def get_pick_positions(self):
        """Generate all pickup positions for pieces in magazine"""
        pick_above, pick = {}, {}
        
        # First row (pieces 1-8)
        for i in range(self.count_first_row):
            piece_num = i + 1
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(
                    self.offset_x + i * 25,
                    self.offset_y_first_row, 
                    self.z_offset
                    ) * 
                rotx(pi)
            )
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(self.offset_x + i * 25, 
                       self.offset_y_first_row, 
                       self.z_pick
                       ) * 
                rotx(pi)
            )
        
        # Second row (pieces 9-15)
        for i in range(self.count_second_row):
            piece_num = i + 9
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(self.offset_x + i * 25, 
                       self.offset_y_second_row, 
                       self.z_offset
                       ) * 
                rotx(pi)
            )
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(self.offset_x + i * 25, 
                       self.offset_y_second_row, 
                       self.z_pick
                       ) * 
                rotx(pi)
            )
        
        return pick_above, pick