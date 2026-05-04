from src.interface.grid.manifold_mapping import Tile

class ObserverController:
    def __init__(self, start_x=16, start_y=16):
        self.x = start_x
        self.y = start_y

    def move(self, dx, dy, manifold_map):
        target_x = self.x + dx
        target_y = self.y + dy
        if not manifold_map.validate_coordinate(target_x, target_y):
            return False
        target_tile = manifold_map.grid[target_y][target_x]
        if target_tile == Tile.WALL:
            return False
        self.x, self.y = target_x, target_y
        return True
