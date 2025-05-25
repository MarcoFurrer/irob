class JengaPiece:
    """Represents a single Jenga piece"""
    
    def __init__(self, rdk, number):
        self.number = number
        self.rdk = rdk
        self.piece = rdk.Item(f"Jengastuck {number}")
        
        if not self.piece.Valid():
            raise Exception(f"Jenga piece {number} not found in RoboDK")
    
    def attach_to_frame(self, frame):
        """Attach this piece to a specific frame (used for tower building)"""
        self.piece.setParentStatic(frame)
    
    def __str__(self):
        """String representation of the piece"""
        return f"JengaPiece({self.number})"
    
    def __repr__(self):
        """Developer representation of the piece"""
        return f"JengaPiece(number={self.number})"


class JengaPieceCollection:
    """Collection of Jenga pieces with convenient access methods"""
    
    def __init__(self, rdk, count=15):
        """Initialize collection with specified number of pieces"""
        self.rdk = rdk
        self.pieces = [JengaPiece(rdk, i) for i in range(1, count + 1)]
    
    def get_piece(self, number):
        """Get a specific piece by number"""
        return self.pieces[number]
    
    def get_pieces_by_numbers(self, numbers):
        """Get multiple pieces by their numbers"""
        return [self.get_piece(num) for num in numbers]
    
    def get_all_pieces(self):
        """Get all pieces as a list, ordered by number"""
        return [self.pieces[i] for i in sorted(self.pieces)]
    
    def get_piece_count(self):
        """Get total number of pieces in collection"""
        return len(self.pieces)
    
    def __len__(self):
        """Support len() function"""
        return len(self.pieces)
    
    def __iter__(self):
        """Support iteration over pieces in order"""
        for number in sorted(self.pieces):
            yield self.pieces[number]