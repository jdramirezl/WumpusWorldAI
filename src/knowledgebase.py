from typing import Any, Generator, List, Union
from expression import Expr
from logic import Logic

class KnowledgeBase:
    """A base class for Knowledge Base (KB) systems."""
    def __init__(self):
        self.clauses: List[Expr] = []
        self.logic = Logic()

    def ask(self, query: Any) -> Union[dict, bool]:
        """Returns a substitution that makes the query true, or False if not found."""
        
        if isinstance(query, str):
            query = Expr.create_expression(query)
        
        for _ in self.ask_generator(query):
            return True
        return False

    def tell(self, sentence: "Expr") -> None:
        """Adds clauses of a sentence to the KB."""
        cnf_sentence = Logic().to_cnf(sentence)
        conjuncts = Logic().conjuncts(cnf_sentence)
        self.clauses.extend(conjuncts)


    def ask_generator(self, query: "Expr") -> Generator[dict, None, None]:
        """Yields an empty substitution if the KB implies the query."""
        if self.logic.tt_entails(Expr("&", *self.clauses), query):
            yield {}

    def retract(self, sentence: "Expr") -> None:
        """Removes clauses of a sentence from the KB."""
        
        for clause in self.logic.conjuncts(self.logic.to_cnf(sentence)):
            if clause in self.clauses:
                self.clauses.remove(clause)

