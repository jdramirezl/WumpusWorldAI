import random

class Environment:
    def __init__(self, grid_size: int = 4, player_position: tuple = (0, 0)):
        # the map is always a square
        self.grid_size = grid_size
        self.player_position = player_position
        self.generate_map()
        # self.map = [
        #     ['o', 'o', 'o', 'P'],
        #     ['W', 'G', 'P', 'o'],
        #     ['o', 'o', 'o', 'o'],
        #     ['o', 'o', 'P', 'o']
        # ] UN MAPA QUE PODEMOS USAR DE EJEMPLO
        
    
    def get_random_position(self, start: int = 0, end: int = None):
        return (random.randint(start, end - 1), random.randint(start, end - 1))
        
    def generate_map(self):
        self.map = [['o' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Place the wumpus
        wumpus_position = self.get_random_position(0, self.grid_size)
        while wumpus_position == self.player_position:
            wumpus_position = self.get_random_position(0, self.grid_size)
        self.map[wumpus_position[0]][wumpus_position[1]] = 'W'
        
        # Place the gold
        gold_position = self.get_random_position(0, self.grid_size)
        while gold_position == self.player_position or gold_position == wumpus_position:
            gold_position = self.get_random_position(0, self.grid_size)
        self.map[gold_position[0]][gold_position[1]] = 'G'
        
        # Place the pits
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if (x, y) == self.player_position or (x, y) == wumpus_position or (x, y) == gold_position:
                    continue
                if random.random() < 0.2:
                    self.map[y][x] = 'P'
    
    def get_map(self):
        return self.map
    
    def print_map(self, player_position: tuple = None):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if player_position is not None and (x, y) == player_position:
                    print('♥', end=' ')
                else:
                    print(self.map[x][y], end=' ')
            print()
    
    def get_nearby_cells(self, position):
        # Only return cells that are within the bounds of the map
        x, y = position
        nearby_cells = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < len(self.map) and 0 <= new_y < len(self.map[0]):
                nearby_cells.append((new_x, new_y))
        return nearby_cells
    
    def get_percept(self, position):
        percept = [None, None, None, None, None]
        nearby_cells = self.get_nearby_cells(position)
        
        # Check if the player perceives a bump
        if not self.is_valid_position(position):
            percept[3] = 'Bump'
        
        # Only check the rest of the percepts if the player did not perceive a bump
        if percept[3] is None:
            # Check for pits, wumpus, and gold in nearby cells
            for cell in nearby_cells:
                if self.is_pit(cell):
                    percept[1] = 'Breeze'
                if self.is_wumpus(cell):
                    percept[0] = 'Stench'
            
            # Check for gold in the current cell
            if self.is_gold(position):
                percept[2] = 'Glitter'
                
            
            # Check if the wumpus is alive
            if not self.is_wumpus_alive():
                percept[4] = 'Scream'

        return percept
    
    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < len(self.map) and 0 <= y < len(self.map[0])
    
    def is_pit(self, position):
        x, y = position
        return self.map[x][y] == 'P'
    
    def is_wumpus(self, position):
        x, y = position
        return self.map[x][y] == 'W'
    
    def is_gold(self, position):
        x, y = position
        return self.map[x][y] == 'G'
    
    def is_wumpus_alive(self):
        return any('W' in row for row in self.map)
    
    def remove_wumpus(self):
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                if self.map[x][y] == 'W':
                    self.map[x][y] = 'o'
                    return
                
    def remove_gold(self):
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                if self.map[x][y] == 'G':
                    self.map[x][y] = 'o'
                    return