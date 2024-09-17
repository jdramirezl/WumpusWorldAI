import random

class Environment:
    def __init__(self, grid_size: int = 4, player_position: tuple = (0, 0)):
        # the map is always a square
        self.grid_size = grid_size
        self.player_position = player_position
        
    
    def get_random_position(self, start: int = 0, end: int = None):
        return (random.randint(start, end - 1), random.randint(start, end - 1))
        
    def generate_map(self):
        self.map = [['o' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Place the wumpus
        wumpus_position = self.get_random_position(0, self.grid_size)
        while wumpus_position == self.player_position:
            wumpus_position = self.get_random_position(0, self.grid_size)
        self.map[wumpus_position[1]][wumpus_position[0]] = 'W'
        
        # Place the gold
        gold_position = self.get_random_position(0, self.grid_size)
        while gold_position == self.player_position or gold_position == wumpus_position:
            gold_position = self.get_random_position(0, self.grid_size)
        self.map[gold_position[1]][gold_position[0]] = 'G'
        
        # Place the pits
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if (x, y) == self.player_position or (x, y) == wumpus_position or (x, y) == gold_position:
                    continue
                if random.random() < 0.2:
                    self.map[y][x] = 'P'
        
    
    def get_map(self):
        return self.map
    
    def print_map(self):
        for row in self.map:
            print(' '.join(row))
            
    
    def get_nearby_cells(self, position):
        # Only return cells that are within the bounds of the map
        x, y = position
        nearby_cells = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < len(self.map[0]) and 0 <= new_y < len(self.map):
                nearby_cells.append((new_x, new_y))
        return nearby_cells
    
    def get_percept(self, position):
        percept = [None, None, None, None, None]
        nearby_cells = self.get_nearby_cells(position)
        
        # Check for pits, wumpus, and gold in nearby cells
        for cell in nearby_cells:
            if self.is_pit(cell):
                percept[1] = 'Breeze'
            if self.is_wumpus(cell):
                percept[0] = 'Stench'
        
        # Check for gold in the current cell
        if self.is_gold(position):
            percept[2] = 'Glitter'
            
        
        # Check if the player perceives a bump
        if not self.is_valid_position(position):
            percept[3] = 'Bump'
        
        # Check if the wumpus is alive
        if not self.is_wumpus_alive():
            percept[4] = 'Scream'

        return percept
    
    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < len(self.map) and 0 <= y < len(self.map[0])
    
    def is_pit(self, position):
        x, y = position
        return self.map[y][x] == 'P'
    
    def is_wumpus(self, position):
        x, y = position
        return self.map[y][x] == 'W'
    
    def is_gold(self, position):
        x, y = position
        return self.map[y][x] == 'G'
    
    def is_wumpus_alive(self):
        return any('W' in row for row in self.map)
    
    def remove_wumpus(self):
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell == 'W':
                    self.map[y][x] = 'o'
                    return
                
    def remove_gold(self):
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell == 'G':
                    self.map[y][x] = 'o'
                    return