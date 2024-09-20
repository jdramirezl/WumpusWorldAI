from agent import WumpusAgent
from environment import Environment

class Utils:
    def get_position_string(self, action):
        actions = action.split("|")
        position_string = actions[1].strip() # (x, y)
        positions = position_string.split(",") # ['(x', 'y)']
        positions = list(map(lambda x: x.strip(), positions)) # ['(x', 'y)']
        x, y = int(positions[0][1:]), int(positions[1][:-1])
        return x, y

    def get_last_action(self, action):
        actions = action.split("|")
        actions = actions[0].split("(")
        return actions[1].strip()

    def define_starting_clauses(self, world):
        def or_clause(position, first_symbol, consecuence_symbol, positions):
            clause = f"{first_symbol}{position[0]}_{position[1]} <=> ("
            for position in positions:
                clause += f" {consecuence_symbol}{position[0]}_{position[1]} |"
            clause = clause[:-1] + ")"
            return clause
        
        def and_clause(position, first_symbol, consecuence_symbol, positions):
            clause = f"{first_symbol}{position[0]}_{position[1]} <=> ("
            for position in positions:
                clause += f" {consecuence_symbol}{position[0]}_{position[1]} &"
            clause = clause[:-1] + ")"
            return clause
        
        initial_clauses = []
        for i in range(world.grid_size):
            for j in range(world.grid_size):
                B = or_clause((i, j), "B", "P", world.get_nearby_cells((i, j)))
                nB = and_clause((i, j), "~B", "~P", world.get_nearby_cells((i, j)))
                S = or_clause((i, j), "S", "W", world.get_nearby_cells((i, j)))
                nS = and_clause((i, j), "~S", "~W", world.get_nearby_cells((i, j)))
                
                initial_clauses = initial_clauses + [B, nB, S, nS]
        
        return initial_clauses


def main():
    # CONSTANTS
    MAP_SIZE = 4
    start_player_position = (MAP_SIZE - 1, 0)
    utils = Utils()
    
    # Create the world and the agent
    world = Environment(grid_size=MAP_SIZE, player_position=start_player_position)
    agent = WumpusAgent(start_player_position)
    
    # Define the initial clauses
    start_clauses = utils.define_starting_clauses(world)
    for clause in start_clauses:
        agent.KB.tell(clause)
        
    print(start_clauses)

    # Perceive
    percept = world.get_percept(agent.position)
    print(percept)
    # print(agent.KB.clauses)
    world.print_map(agent.position)

    # Lets play
    for _ in range(50):
        # Act
        action = agent.act(percept)
        print(action)
        
        # If there is a "position" in the action, we can extract it as its going to be "... position (x, y)..."
        x, y = utils.get_position_string(action)
        last_action = utils.get_last_action(action)
        print(last_action)
        
        # Perceive
        percept = world.get_percept(agent.position)
        print(percept)
        # print(agent.KB.clauses)
        world.print_map(agent.position)
        
        if last_action == "Climb":
            print("Game Over, you have climbed out of the cave")
            break
        elif last_action == "Grab":
            print("Gold has been grabbed")
            world.remove_gold()
        
        # Check if player is located at a pit or wumpus
        if world.is_valid_position((x, y)) and (world.is_pit((x, y)) or world.is_wumpus((x, y))):
            if world.is_pit((x, y)):
                print("Fell into a pit")
            else:
                print("Wumpus killed you")
            agent.is_alive = False
            print("Game over")
            break
        
        print("-----------------")
        # self.map = 
        

if __name__ == "__main__":
    main() # Call the main function