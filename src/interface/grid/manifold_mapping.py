from enum import Enum

class Tile(Enum):
    VOID = 0x00
    FLOOR = 0x01
    WALL = 0x02

class ManifoldMap:
    def __init__(self, size=32):
        self.size = size
        self.grid = [[Tile.VOID for _ in range(size)] for _ in range(size)]
    def validate_coordinate(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size
