from robodk import *
from robolink import *
from src.position import Position


class Jenga:
    def __init__(self, 
                 speed=100,
                 block_rows=2,
                 blocks:list = [],
                 ground_height = 0,
                 jenga_start_pos:Position= Position(0, 0, 100, 0, 0, 0),
                 pickup_start_pos:Position = Position(50, 150, 100, 0, 0, 0),
                 robot:str = "Staubli TX2-90L",
                 ):
        self.RDK = robolink.Robolink()
        self.robot = self.RDK.Item(robot)
        self.speed = speed
        self.block_rows = block_rows
        self.blocks = blocks
        self.ground_height = ground_height
        self.jenga_start_pos = jenga_start_pos
        self.pickup_start_pos = pickup_start_pos
        self.block_width = 3
        self.block_height = 1
        self.safety_distance = 2
        self.home_pos = self.robot.JointsHome()
        
        self._initialize_blocks()
        
    def _initialize_blocks(self):
        for i, block in enumerate(self.blocks):
            # Calculate start position for this block
            start_pos = self.get_block_start_pos(i)
            # Convert position to pose matrix
            pose_matrix = transl(start_pos.x, start_pos.y, start_pos.z) * rotz(math.radians(start_pos.rz))
            # Reset block position in RoboDK
            block.setPose(pose_matrix)
        

    def get_jenga_pos(self, block_num):
        """
        Get the position of a block in a Jenga tower.

        Args:
            block_num (int): The block number (1-indexed).

        Returns:
            tuple: A tuple containing the x, y, z coordinates and rotation of the block.
        """
        # Calculate the layer and position within the layer
        layer = (block_num) // 3
        position = (block_num) % 3
        
        # Determine rotation based on layer (alternating)
        # True for even layers (0, 2, 4...), False for odd layers (1, 3, 5...)
        rotation = layer % 2 == 0
        
        # Calculate x, y coordinates based on rotation
        if rotation:
            # Blocks along x-axis
            x = position * self.block_width
            y = 0
        else:
            # Blocks along y-axis
            x = 0
            y = position * self.block_width
        
        # Calculate z coordinate (height)
        z = layer * self.block_height
        
        return Position(x, y, z, 0,0,rotation*90) + self.jenga_start_pos

    def get_block_start_pos(self, block_num):
        """
        Get the starting position of a block in a Jenga tower.

        Args:
            block_num (int): The block number (1-indexed).

        Returns:
            tuple: A tuple containing the x, y coordinates of the block.
        """
        # Calculate the row and column of the block
        row = (block_num) // self.block_rows
        col = (block_num) % (self.amout_of_blocks // self.block_rows)

        # Calculate the x, y coordinates of the block
        x = col * self.block_width
        y = row * self.block_height

        return Position(x, y, self.ground_height, 0, 0, 0)
    
    def move_to_start(self):
        """Move robot to home/safe position"""
        self.robot.MoveJ(self.home_pos)
    
    def move_to_start_block_pos(self, position:Position):
        """
        Move to the starting position of a block in a Jenga tower.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.
            z (int): The z coordinate.
        """
        # Move to the starting position
        print(f"Moving to starting position: ({position.x}, {position.y}, {position.z})")
        self.robot.MoveJ(position.position())
        
    def move_to_jenga(self, position:Position):
        """
        Move to the specified position in a Jenga tower.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.
            z (int): The z coordinate.
        """
        # Move to the specified position
        print(f"Moving to position: ({position.x}, {position.y}, {position.z})")
        self.robot.MoveJ(position.position())
    
    def pick_block(self, block):
        """Pick up a block from its current position
        
        Args:
            block: The RoboDK Item object representing the block
        """
        # Get block position
        block_pos = block.PoseAbs()
        
        # Calculate approach position (e.g., 50mm above the block)
        approach_pos = block_pos * transl(0, 0, 50)
        
        # Move to approach position
        self.robot.MoveJ(approach_pos)
        
        # Move to pick position
        self.robot.MoveL(block_pos)
        
        # Activate vacuum
        self.rts.setVacuum(1)
        
        # Small delay to ensure grip
        robodk.pause(0.2)
        
        # Move back to approach position with the block
        self.robot.MoveL(approach_pos)
    
    def place_block_in_tower(self, block, block_index):
        """Place a block in the tower
        
        Args:
            block: The RoboDK Item object representing the block
            block_index: The index of the block to determine its position in the tower
        """
        # Calculate tower position based on block index
        # For example, we can build a 3x3x5 Jenga tower
        level = block_index // 3
        position_in_level = block_index % 3
        rotation = 0 if (level % 2 == 0) else pi/2  # Alternate orientation by level
        
        # Base position of the tower
        tower_frame = robolink.Robolink().Item('Tower')
        tower_pos = tower_frame.PoseAbs()
        
        # Calculate position within tower
        if level % 2 == 0:  # Even level
            block_tower_pos = tower_pos * transl(position_in_level * 25 - 25, 0, level * 15)
        else:  # Odd level
            block_tower_pos = tower_pos * transl(0, position_in_level * 25 - 25, level * 15)
        
        # Add proper orientation
        block_tower_pos = block_tower_pos * rotz(rotation)
        
        # Calculate approach position
        approach_pos = block_tower_pos * transl(0, 0, 50)
        
        # Move to approach position
        self.robot.MoveJ(approach_pos)
        
        # Move to placement position
        self.robot.MoveL(block_tower_pos)
        
        # Release block
        self.rts.setVacuum(0)
        
        # Small delay
        robodk.pause(0.2)
        
        # Move back to approach position
        self.robot.MoveL(approach_pos)