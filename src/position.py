class Position:
    def __init__(self, x = 0, y = 0, z = 0, roll = 0, pitch = 0, yaw = 0):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        
    def coordinates(self):
        """
        Get the position of the block in a Jenga tower.
        
        Returns:
            tuple: A tuple containing the x, y, z coordinates of the block.
        """
        return (self.x, self.y, self.z)
    def rotation(self):
        """
        Get the rotation of the block in a Jenga tower.
        Returns:
            tuple: A tuple containing the roll, pitch, yaw coordinates of the block.
        """
        return (self.roll, self.pitch, self.yaw)
    def position(self):
        """
        Get the position and rotation of the block in a Jenga tower.
        
        Returns:
            tuple: A tuple containing the x, y, z coordinates and roll, pitch, yaw coordinates of the block.
        """
        return [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]
    
    def __add__(self, other):
        """
        Add two positions together.
        
        Args:
            other (Position): The other position to add.
        
        Returns:
            Position: A new position that is the sum of the two positions.
        """
        return Position(self.x + other.x, self.y + other.y, self.z + other.z, self.roll + other.roll, self.pitch + other.pitch, self.yaw + other.yaw)