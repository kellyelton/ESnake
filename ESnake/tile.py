from .tiletype import TileType

class Tile(self): 
    def __init__(self, x: int, y: int, tileType: TileType):
        self.type = tileType
        self.x = x
        self.y = y