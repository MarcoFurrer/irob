from jenga_constants import JengaConstants

from robodk.robolink import *
from robodk.robomath import *
from robodk.robodialogs import *

class Magazine:
    """Handles magazine frame and piece positioning"""
    
    def __init__(self, rdk, frame_name="MagazinFrame"):
        self.rdk = rdk
        self.frame = rdk.Item(frame_name)
        
        if not self.frame.Valid():
            raise Exception(f"Magazine frame '{frame_name}' not found in RoboDK")
    
    def get_pick_positions(self):
        """Generate all pickup positions for pieces in magazine"""
        pick_above, pick = {}, {}
        
        # First row (pieces 1-8)
        for i in range(JengaConstants.COUNT_FIRST_ROW):
            piece_num = i + 1
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_FIRST_ROW, JengaConstants.Z_OFFSET) * 
                rotx(pi)
            )
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_FIRST_ROW, JengaConstants.Z_PICK) * 
                rotx(pi)
            )
        
        # Second row (pieces 9-15)
        for i in range(JengaConstants.COUNT_SECOND_ROW):
            piece_num = i + 9
            pick_above[f"Jenga{piece_num}above"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_SECOND_ROW, JengaConstants.Z_OFFSET) * 
                rotx(pi)
            )
            pick[f"Jenga{piece_num}"] = (
                self.frame.Pose() * 
                transl(JengaConstants.OFFSET_X + i * 25, JengaConstants.OFFSET_Y_SECOND_ROW, JengaConstants.Z_PICK) * 
                rotx(pi)
            )
        
        return pick_above, pick