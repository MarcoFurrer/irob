class JengaConstants:
    """Constants for the Jenga robot system"""
    # Magazine layout
    OFFSET_X = 72.5
    OFFSET_Y_FIRST_ROW = 97.5
    OFFSET_Y_SECOND_ROW = 172.5
    Z_PICK = 15
    Z_OFFSET = 15
    COUNT_FIRST_ROW = 8
    COUNT_SECOND_ROW = 7
    
    # Jenga piece dimensions
    LENGTH = 75
    WIDTH = 25.5
    HEIGHT = 15
    
    # Tower placement
    OFFSET_TOOL = 0
    X_TOWER = 70
    Y_TOWER = 70
    
    # Robot positions
    T_HOME = [0, 50, 50, 0, 60, 0]
    T_START = [0, 0, 90, 0, 90, 0]