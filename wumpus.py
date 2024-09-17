

class WumpusAgent:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.position = (1, 1)
        self.orientation = 'EAST'
        self.has_gold = False
        self.has_arrow = True
        self.t = 0  # Inicializar el contador de tiempo
        self.orientations = ['NORTH', 'EAST', 'SOUTH', 'WEST']
        self.movements = {'NORTH': (0, 1), 'EAST': (1, 0), 'SOUTH': (0, -1), 'WEST': (-1, 0)}
        self.is_alive = True
        self.score = 0

    def make_percept_sentence(self, percept, t):
        return f"Percept({percept}, {t}, {self.position}, {self.orientation})"

    def make_action_query(self, t):
        return f"Action, {t}"

    def make_action_sentence(self, action, t):
        return f"Executed({action}, {t})"

    def act(self, percept):
        # Actualización de la percepción
        percept_sentence = self.make_percept_sentence(percept, self.t)
        self.kb.tell(percept_sentence)

        # Consulta qué acción tomar basada en el percept
        action_query = self.make_action_query(self.t)
        inferred_action = self.kb.ask(action_query)

        if inferred_action:
            action = inferred_action.split[0]
        else:
            action = self.decide_action(percept)

        action_sentence = self.make_action_sentence(action, self.t)
        self.kb.tell(action_sentence)
        self.execute_action(action)

        # Actualiza el tiempo t
        self.t += 1

        return action

    def decide_action(self, percept):
        if 'Glitter' in percept:
            return 'Grab'
        elif 'Stench' in percept and self.has_arrow:
            return 'Shoot'
        elif 'Breeze' in percept:
            return 'TurnLeft'  # Ejemplo simple
        else:
            return 'Forward'

    def execute_action(self, action):
        if action == 'Forward':
            self.move_forward()
        elif action == 'TurnLeft':
            self.turn_left()
        elif action == 'TurnRight':
            self.turn_right()
        elif action == 'Grab':
            self.has_gold = True
        elif action == 'Shoot':
            self.has_arrow = False

    def move_forward(self):
        x, y = self.position
        dx, dy = self.movements[self.orientation]
        new_position = (x + dx, y + dy)
        
        


    def turn_left(self):
        current_orientation_index = self.orientations.index(self.orientation)  
        self.orientation = self.orientations[(current_orientation_index - 1) % 4]

    def turn_right(self):
        current_orientation_index = self.orientations.index(self.orientation)
        self.orientation = self.orientations[(current_orientation_index + 1) % 4]

    def grab(self):
        if not self.has_gold:
            self.has_gold = True
            print("El agente ha recogido el oro")
        else:
            print("El agente ya tiene el oro")


    def shoot(self):
        if self.has_arrow:
            self.has_arrow = False
            print("El agente ha disparado la flecha")
        else:
            print("El agente no tiene flechas")



