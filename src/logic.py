from collections import deque
from typing import List, Optional
from expression import Expr

class Logic:
    """A class for logical operations and conversions."""

    TRUE, FALSE, ZERO, ONE, TWO = map(Expr, ["TRUE", "FALSE", 0, 1, 2])
    A, B, C, D, E, F, G, P, Q, x, y, z = map(Expr, "ABCDEFGPQxyz")
    _op_identity = {"&": TRUE, "|": FALSE, "+": ZERO, "*": ONE}

    def is_var_symbol(self, s: str) -> bool:
        """Returns True if the string is a variable symbol."""
        return Expr.is_symbol(s) and s[0].islower()

    def is_prop_symbol(self, s: str) -> bool:
        """Returns True if the string is a proposition symbol."""
        return Expr.is_symbol(s) and s[0].isupper() and s != "TRUE" and s != "FALSE"

    def variables(self, s: "Expr") -> set:
        """Returns a set of variables in the expression."""
        result = set([])

        def walk(s):
            if self.is_var_symbol(s):
                result.add(s)
            else:
                for arg in s.args:
                    walk(arg)

        walk(s)
        return result

    def tt_entails(self, kb: "Expr", alpha: "Expr") -> bool:
        """Does kb entail the sentence alpha? Use truth tables. For propositional
        kb's and sentences."""
        # print("TT_ENTAILS", kb, alpha)
        assert not self.variables(alpha)
        return self.tt_check_all(kb, alpha, self.prop_symbols(kb & alpha), {})

    def tt_check_all(
        self, kb: "Expr", alpha: "Expr", symbols: deque, model: dict
    ) -> bool:
        """Auxiliary routine to implement tt_entails."""
        # print("TT_CHECK_ALL", kb, alpha, symbols, model)
        if not symbols:
            if self.evaluate(kb, model):
                result = self.evaluate(alpha, model)
                assert result in (True, False)
                return result
            else:
                return True
        else:
            # P, rest = symbols[0], symbols[1:]
            P = symbols.popleft()
            rest = symbols
            # print the entire kb clauses but only for stirngs that start with L
            # print("TT_CHECK_ALL", [str(clause) for clause in kb.args if str(clause).startswith("L")])
            
            model[P] = True
            result_true = self.tt_check_all(kb, alpha, rest, model)
            model[P] = False
            result_false = self.tt_check_all(kb, alpha, rest, model)
            del model[P]
            return result_true and result_false

    def prop_symbols(self, x: "Expr") -> deque:
        """Return a set of all propositional symbols in x."""
        if not isinstance(x, Expr):
            return deque([])
        elif self.is_prop_symbol(x.op):
            return deque([x])
        else:
            return deque(set(symbol for arg in x.args for symbol in self.prop_symbols(arg)))

    def evaluate(self, exp: "Expr", model: dict = {}) -> Optional[bool]:
        """Return True if the propositional logic expression is true in the model,
        and False if it is false. If the model does not specify the value for
        every proposition, this may return None to indicate 'not obvious';
        this may happen even when the expression is tautological."""
        op, args = exp.op, exp.args
        
        # If the expression is a constant, return its value
        if exp in (self.TRUE, self.FALSE):
            return exp == self.TRUE

        # If the expression is a proposition symbol, return its value
        if self.is_prop_symbol(op):
            return model.get(exp)
        
        # Evaluate complex expressions
        if op == "~": # negation
            p = self.evaluate(args[0], model)
            return not p if p is not None else None
        elif op == "|": # disjunction
            result = False
            for arg in args:
                p = self.evaluate(arg, model)
                if p is True:
                    return True
                if p is None:
                    result = None
            return result
        elif op == "&": # conjunction
            result = True
            for arg in args:
                p = self.evaluate(arg, model)
                if p is False:
                    return False
                if p is None:
                    result = None
            return result
        
        # At this point, the operator represents a binary operation
        # Split the expression into a list of clauses
        p, q = args
        
        if op == ">>": # implication
            return self.evaluate(~p | q, model)
        elif op == "<<": # reverse implication
            return self.evaluate(p | ~q, model)
        
        # If the operator is not an implication, evaluate the expression
        # Get the truth values of the two propositions
        pt = self.evaluate(p, model)
        qt = self.evaluate(q, model) 
        
        # If the truth values are not known, return None
        if not pt or not qt:
            return None
        
        # Evaluate the expression
        if op == "<=>": # biconditional
            return pt == qt
        elif op == "^": # exclusive or
            return pt != qt
        else:
            raise ValueError("illegal operator in logic expression" + str(exp))

    def to_cnf(self, s: "Expr") -> "Expr":
        """Converts a propositional logical sentence s to conjunctive normal form."""
        if isinstance(s, str):
            s = Expr.create_expression(s)
        s = self.eliminate_implications(s)
        s = self.demorgans_law(s)
        return self.distribute_and_over_or(s)

    def eliminate_implications(self, s: "Expr") -> "Expr":
        """Change >>, <<, and <=> into &, |, and ~."""
        if not s.args or Expr.is_symbol(s.op):
            return s
        args = list(map(self.eliminate_implications, s.args))
        a, b = args[0], args[-1]
        if s.op == ">>":
            return b | ~a
        elif s.op == "<<":
            return a | ~b
        elif s.op == "<=>":
            return (a | ~b) & (b | ~a)
        elif s.op == "^":
            assert len(args) == 2
            return (a & ~b) | (~a & b)
        else:
            assert s.op in ("&", "|", "~")
            return Expr(s.op, *args)
    
    def demorgans_law(self, s: "Expr") -> "Expr":
        """Rewrite sentence s by moving negation sign inward."""
        if s.op == "~":
            NOT = lambda b: self.demorgans_law(~b)
            a = s.args[0]
            if a.op == "~":
                return self.demorgans_law(a.args[0])
            if a.op == "&":
                return self.associate("|", map(NOT, a.args))
            if a.op == "|":
                return self.associate("&", map(NOT, a.args))
            return s
        elif Expr.is_symbol(s.op) or not s.args:
            return s
        else:
            return Expr(s.op, *map(self.demorgans_law, s.args))

    def distribute_and_over_or(self, s: "Expr") -> "Expr":
        """Given a sentence s consisting of conjunctions and disjunctions of literals,
        return an equivalent sentence in CNF."""
        if s.op == "|":
            s = self.associate("|", s.args)
            if s.op != "|":
                return self.distribute_and_over_or(s)
            if len(s.args) == 0:
                return self.FALSE
            if len(s.args) == 1:
                return self.distribute_and_over_or(s.args[0])
            conj = next((d for d in s.args if d.op == "&"), None)
            if not conj:
                return s
            others = [a for a in s.args if a is not conj]
            rest = self.associate("|", others)
            return self.associate(
                "&", [self.distribute_and_over_or(c | rest) for c in conj.args]
            )
        elif s.op == "&":
            return self.associate("&", map(self.distribute_and_over_or, s.args))
        else:
            return s

    def associate(self, op: str, args: List["Expr"]) -> "Expr":
        """Given an associative op, return an expression with the same meaning as
        Expr(op, *args), but flattened."""
        args = self.split_by_op(op, args)
        if len(args) == 0:
            return self._op_identity[op]
        elif len(args) == 1:
            return args[0]
        else:
            return Expr(op, *args)
        
    
    def conjuncts(self, s: "Expr") -> List["Expr"]:
        """Return a list of the conjuncts in the sentence s."""
        return self.split_by_op("&", [s])
    
    def disjuncts(self, s: "Expr") -> List["Expr"]:
        """Return a list of the disjuncts in the sentence s."""
        return self.split_by_op("|", [s])

    def split_by_op(self, op: str, args: List["Expr"]) -> List["Expr"]:
        """Given an associative op, return a flattened list result such that
        Expr(op, *result) means the same as Expr(op, *args).
        
        EJ: for op = "&" and args = [A, B, Expr("|", C, D), Expr("&", E, F)]
        result = [A, B, Expr("|", C, D), E, F]
        
        """
        result = []

        def collect(subargs):
            for arg in subargs:
                if arg.op == op:
                    collect(arg.args)
                else:
                    result.append(arg)

        collect(args)
        return result


    
    