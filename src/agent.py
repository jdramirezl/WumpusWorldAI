from knowledgebase import KnowledgeBase

class LogicAgent:
    def __init__(self):
        self.KB = KnowledgeBase()
        self.DELTAS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
    def safe_neighbors(self, position):
        neighbours = self.get_neighbors(position)        
        safe_neighbors = set()
        
        for neighbor in neighbours:
            x, y = neighbor
            
            if x < 0 or y < 0:
                continue
            
            # Current Neighbor
            loc = f"{x}_{y}"
            
            # Add current location spot to the safe_spots
            is_loc = self.KB.ask(f"L{loc}")
            if is_loc:
                safe_neighbors.add(neighbor)
            
            # print(f"Safe Neighbors: {safe_neighbors} after checking for location")
            # isnt_pit = self.KB.ask(Expr.create_expression(f"~P{loc}"))
            # isnt_wumpus = self.KB.ask(Expr.create_expression(f"~W{loc}"))
            isnt_pit = not self.KB.ask(f"P{loc}")
            isnt_wumpus = not self.KB.ask(f"W{loc}")
            if isnt_pit and isnt_wumpus:
                safe_neighbors.add(neighbor)
            
            # print("Current KB: ", self.KB.clauses)
            # print(f"Current neighbor: {neighbor} - {loc} - isnt_pit: {isnt_pit} - isnt_wumpus: {isnt_wumpus} is_loc: {is_loc}")
        return safe_neighbors                
        
    def not_unsafe_neighbors(self, position: tuple):
        neighbours = self.get_neighbors(position)
        not_unsafe_neighbors = set()
        
        for neighbor in neighbours:
            x, y = neighbor
            
            if x < 0 or y < 0:
                continue
            
            # Current Neighbor
            loc = f"{x}_{y}"
            
            # is_loc = self.KB.ask(Expr.create_expression(f"L{loc}"))
            is_loc = self.KB.ask(f"L{loc}")
            if not is_loc:
                not_unsafe_neighbors.add(neighbor)
                
            
            # Not a pit or not a wumpus at current location
            # print("is_wumpus: ", f"W{loc}")
            # is_wumpus = self.KB.ask(Expr.create_expression(f"W{loc}"))
            # is_pit = self.KB.ask(Expr.create_expression(f"P{loc}"))
            is_wumpus = self.KB.ask(f"W{loc}")
            is_pit = self.KB.ask(f"P{loc}")
            if not is_wumpus and not is_pit:
                not_unsafe_neighbors.add(neighbor)
            
            # print(f"Current neighbor: {neighbor} - {loc} - is_wumpus: {is_wumpus} - is_pit: {is_pit} is_loc: {is_loc}")


        return not_unsafe_neighbors
        
        
    def get_neighbors(self, position):
        return [(position[0] + dx, position[1] + dy) for dx, dy in self.DELTAS if 0 <= position[0] + dx and 0 <= position[1] + dy]
    
    def unvisited(self, position):
        neighbours = self.get_neighbors(position)
        unvisited = set()
        for neighbor in neighbours:
            # if we haven't added the neighbor to the unvisited set, add it
            
            if f"L{neighbor[0]}_{neighbor[1]}" not in [str(clause) for clause in self.KB.clauses]:
                unvisited.add(neighbor)
        
        return unvisited
    
    def get_next_cell(self, position):
        print(f"Current Position: {position}")  
        unvisited_cells = self.unvisited(position)
        print(f"Unvisited Cells: {unvisited_cells}")
        
        safe_cells = self.safe_neighbors(position)
        print(f"Safe Cells: {safe_cells}")
        
        safe_cells = safe_cells.intersection(unvisited_cells)
        
        print(f"Safe Unvisited Cells: {safe_cells}")
        
        if safe_cells:
            next_cell = min(safe_cells)
        else:
            print("No safe cells, checking for not unsafe cells")
            not_unsafe_cells = self.not_unsafe_neighbors(position)
            print(f"Not unsafe Cells: {not_unsafe_cells}")
            not_unsafe_cells = not_unsafe_cells.intersection(unvisited_cells)
            if not_unsafe_cells:
                next_cell = min(not_unsafe_cells)
            else:
                raise Exception("Nowhere left to go")

        return next_cell

class WumpusAgent(LogicAgent):
    def __init__(self, initial_position=(0, 0)):
        # Initialize the agent
        super().__init__()
        
        # Constants
        self.ORIENTATIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
        self.MOVEMENTS = {'NORTH': (0, 1), 'EAST': (1, 0), 'SOUTH': (0, -1), 'WEST': (-1, 0)}
        
        # Initialize agent state
        self.initial_position = initial_position
        self.position = initial_position
        self.orientation = 'EAST'
        self.has_gold = False
        self.has_arrow = True
        self.t = 0 # Time step
        self.is_alive = True
        self.score = 0
        self.wumpus_alive = True


    def make_action_sentence(self, action):
        return f"Executed({action}| {self.position}| {self.orientation}| {self.t})"
    
    def make_clause(self, position, symbol):
        return f"{symbol}{position[0]}_{position[1]}"
    
    def make_neighbor_clause(self, position, symbol, consecuence_symbol, negation=False):
        conjunction = "&" if negation else "|"
        x, y = position
        
        clause = f"{symbol}{x}_{y} <=> ("
        neighbors = self.get_neighbors(position)
        for n in neighbors:
            clause += f" {consecuence_symbol}{n[0]}_{n[1]} {conjunction}"
        clause = clause[:-1] + ")"
        return clause
 
    def make_percept_knowledge(self, percept, t):
        # Create sentences based on the percept
        percept_sentences = []
        
        
        # Scream
        if 'Scream' in percept:
            self.wumpus_alive = False
            
        # New perceptions
        # The obvious ones
        # 1. Current location
        percept_sentences.append(self.make_clause(self.position, 'L'))
        
        # 2. No pit at current location
        percept_sentences.append(self.make_clause(self.position, '~P'))
        
        # 3. No wumpus at current location
        percept_sentences.append(self.make_clause(self.position, '~W'))
        
        # Breeze
        if 'Breeze' in percept:
            breeze = self.make_clause(self.position, 'B')
            # neighbor_clause = self.make_neighbor_clause(self.position, 'B', 'P')
        else:
            breeze = self.make_clause(self.position, '~B')
            # neighbor_clause = self.make_neighbor_clause(self.position, '~B', '~P', negation=True)
        percept_sentences.append(breeze)
        # percept_sentences.append(neighbor_clause)
        
        # Stench
        if 'Stench' in percept:
            stench = self.make_clause(self.position, 'S')
            # neighbor_clause = self.make_neighbor_clause(self.position, 'S', 'W')
        else:
            stench = self.make_clause(self.position, '~S')
            # neighbor_clause = self.make_neighbor_clause(self.position, '~S', '~W', negation=True)
        percept_sentences.append(stench)
        # percept_sentences.append(neighbor_clause)
        
        # Glitter
        if 'Glitter' in percept:
            percept_sentences.append(self.make_clause(self.position, 'G'))
        
        return percept_sentences
    
    def go_to(self, goal):
        self.position = goal
    
    def act(self, percept):
        # Update time step
        self.t += 1
        
        # If we feel a bump, return to the previous position
        if 'Bump' in percept:
            self.KB.tell(f"L{self.position[0]}_{self.position[1]}")
            self.KB.tell(f"N{self.position[0]}_{self.position[1]}")
            self.position = (self.position[0] - self.MOVEMENTS[self.orientation][0], self.position[1] - self.MOVEMENTS[self.orientation][1])
            return self.make_action_sentence('Return')
        
        # Check if there is a Glitter 
        if 'Glitter' in percept and not self.has_gold:
            self.has_gold = True
            # self.KB.tell(Expr.create_expression(f"G{self.position[0]}_{self.position[1]}"))
            self.KB.tell(f"G{self.position[0]}_{self.position[1]}")
            return self.make_action_sentence('Grab')
        
        # If we have gold we need to go back to the start
        if self.has_gold and self.position == self.initial_position:
            return self.make_action_sentence('Climb')
        elif self.has_gold:
            self.go_to(self.initial_position)
            return self.make_action_sentence('Forward')
        
        # Get the next action
        knowledge = self.make_percept_knowledge(percept, self.t)
        
        # Update knowledge base
        for sentence in knowledge:
            self.KB.tell(sentence)
        
        # Ask the knowledge base for the next action
        next_cell = self.get_next_cell(self.position)
        
        # Change the orientation and move to the next cell
        dx, dy = next_cell[0] - self.position[0], next_cell[1] - self.position[1]
        
        # Locate the orientation
        new_orientation = [k for k, v in self.MOVEMENTS.items() if v == (dx, dy)][0]
        self.orientation = new_orientation
        
        # Move to the next cell
        self.position = next_cell
        
        # Return the action
        return self.make_action_sentence('Forward')


