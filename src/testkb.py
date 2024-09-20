from knowledgebase import KnowledgeBase
import pytest

class TestKnowledgeBase:
    """Test the KnowledgeBase class."""
    def test_ask(self):
        """Test the ask method."""
        kb = KnowledgeBase()
        
        # This is the current map
        map = [
            ['P', 'W'],
            ['o', 'G']
        ]
        
        # Initial clauses for a 2x2 grid
        clauses = ['B0_0 <=> ( P0_1 | P1_0 )', '~B0_0 <=> ( ~P0_1 & ~P1_0 )', 'S0_0 <=> ( W0_1 | W1_0 )', '~S0_0 <=> ( ~W0_1 & ~W1_0 )', 'B0_1 <=> ( P1_1 | P0_0 )', '~B0_1 <=> ( ~P1_1 & ~P0_0 )', 'S0_1 <=> ( W1_1 | W0_0 )', '~S0_1 <=> ( ~W1_1 & ~W0_0 )', 'B1_0 <=> ( P1_1 | P0_0 )', '~B1_0 <=> ( ~P1_1 & ~P0_0 )', 'S1_0 <=> ( W1_1 | W0_0 )', '~S1_0 <=> ( ~W1_1 & ~W0_0 )', 'B1_1 <=> ( P1_0 | P0_1 )', '~B1_1 <=> ( ~P1_0 & ~P0_1 )', 'S1_1 <=> ( W1_0 | W0_1 )', '~S1_1 <=> ( ~W1_0 & ~W0_1 )']
        
        # Add current location to the KB
        kb.tell("L1_0")
        
        # Add the clauses to the KB
        for clause in clauses:
            kb.tell(clause)
            
        
        # Also this is the current perception of the agent
        percept = [None, 'Breeze', None, None, None]
        
        # Add the percepts to the KB
        breeze_percept = "B0_0"
        kb.tell(breeze_percept)
        
        # Ask if the KB implies that there is a pit at (0, 0)
        ans = kb.ask("P0_0")
        print(ans, ans == True)
        
        ans = kb.ask("~P0_0")
        print(ans, ans == False)
        
        # Ask if the KB implies that there is a pit at (0, 1)
        ans = kb.ask("P0_1")
        print(ans, ans == True)
        
        ans = kb.ask("~P0_1")
        print(ans, ans == False)
        
        
        # Check if teh cells are visited
        ans = kb.ask("L0_0")
        print(ans, ans == False)
        
        ans = kb.ask("~L0_0")
        print(ans, ans == False)
        
        ans = kb.ask("L0_1")
        
        ans = kb.ask("~L0_1")
        print(ans, ans == False)
        
        ans = kb.ask("L1_0")
        print(ans, ans == True)
        

if __name__ == "__main__":
    test = TestKnowledgeBase()
    test.test_ask()
        