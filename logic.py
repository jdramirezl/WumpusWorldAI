from typing import Any, List, Generator, Union, Optional
import re


class KnowledgeBase:
    """A base class for Knowledge Base (KB) systems."""

    def tell(self, sentence: Any) -> None:
        raise NotImplementedError("Must be implemented in a subclass")

    def ask(self, query: Any) -> Union[dict, bool]:
        """Returns a substitution that makes the query true, or False if not found."""
        for result in self.ask_generator(query):
            return result
        return False

    def ask_generator(self, query: Any) -> Generator[dict, None, None]:
        """Generates all substitutions that make the query true."""
        raise NotImplementedError("Must be implemented in a subclass")

    def retract(self, sentence: Any) -> None:
        """Removes a sentence from the KB."""
        raise NotImplementedError("Must be implemented in a subclass")


class PropKB(KnowledgeBase):
    """A Knowledge Base (KB) for propositional logic."""

    def __init__(self):
        self.clauses: List[Expr] = []

    def tell(self, sentence: "Expr") -> None:
        """Adds clauses of a sentence to the KB."""
        self.clauses.extend(Expr.conjuncts(Expr.to_cnf(sentence)))

    def ask_generator(self, query: "Expr") -> Generator[dict, None, None]:
        """Yields an empty substitution if the KB implies the query."""
        if Expr.tt_entails(Expr("&", *self.clauses), query):
            yield {}

    def retract(self, sentence: "Expr") -> None:
        """Removes clauses of a sentence from the KB."""
        for clause in Expr.conjuncts(Expr.to_cnf(sentence)):
            if clause in self.clauses:
                self.clauses.remove(clause)


class Expr:
    """Represents logical expressions using operators and arguments."""

    def __init__(self, op: Union[str, int], *args: Any) -> None:
        self.op = op
        self.args = list(map(Expr, args))  # Convert args to Expr

    @staticmethod
    def create_expression(s: Union[str, int]) -> "Expr":
        if isinstance(s, Expr):
            return s
        if isinstance(s, int):
            return Expr(s)
        s = s.replace("==>", ">>").replace("<==", "<<")
        s = s.replace("<=>", "%").replace("=/=", "^")
        s = re.sub(r"([a-zA-Z0-9_.]+)", r'Expr("\1")', s)
        return eval(s, {"Expr": Expr})

    def __repr__(self) -> str:
        if not self.args:  # Nullary operators (like variables, constants)
            return str(self.op)
        elif isinstance(self.op, str):
            return f"{self.op}({', '.join(map(repr, self.args))})"
        else:  # Binary or n-ary operators
            return f"({self.op.join(map(repr, self.args))})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Expr) and self.op == other.op and self.args == other.args
        )

    def __hash__(self) -> int:
        return hash((self.op, tuple(self.args)))

    # Operator overloading
    def __invert__(self) -> "Expr":  # For ~ (NOT)
        return Expr("~", self)

    def __and__(self, other: "Expr") -> "Expr":  # For & (AND)
        return Expr("&", self, other)

    def __or__(self, other: "Expr") -> "Expr":  # For | (OR)
        return Expr("|", self, other)

    def __rshift__(self, other: "Expr") -> "Expr":  # For >> (IMPLICATION)
        return Expr(">>", self, other)

    def __lshift__(self, other: "Expr") -> "Expr":  # For << (REVERSE IMPLICATION)
        return Expr("<<", self, other)


class Logic:
    """A class for logical operations and conversions."""

    TRUE, FALSE, ZERO, ONE, TWO = map(Expr, ["TRUE", "FALSE", 0, 1, 2])
    A, B, C, D, E, F, G, P, Q, x, y, z = map(Expr, "ABCDEFGPQxyz")
    _op_identity = {"&": TRUE, "|": FALSE, "+": ZERO, "*": ONE}

    def is_symbol(self, s: str) -> bool:
        """Returns True if the string is a symbol."""
        return isinstance(s, str) and s[:1].isalpha()

    def is_var_symbol(self, s: str) -> bool:
        """Returns True if the string is a variable symbol."""
        return self.is_symbol(s) and s[0].islower()

    def is_prop_symbol(self, s: str) -> bool:
        """Returns True if the string is a proposition symbol."""
        return self.is_symbol(s) and s[0].isupper() and s != "TRUE" and s != "FALSE"

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
        assert not self.variables(alpha)
        return self.tt_check_all(kb, alpha, self.prop_symbols(kb & alpha), {})

    def tt_check_all(
        self, kb: "Expr", alpha: "Expr", symbols: list, model: dict
    ) -> bool:
        """Auxiliary routine to implement tt_entails."""
        if not symbols:
            if self.pl_true(kb, model):
                result = self.pl_true(alpha, model)
                assert result in (True, False)
                return result
            else:
                return True
        else:
            P, rest = symbols.pop(), symbols
            
            return self.tt_check_all(
                kb, alpha, rest, self.extend(model, P, True)
            ) and self.tt_check_all(kb, alpha, rest, self.extend(model, P, False))

    def extend(self, model: dict, var: "Expr", val: bool) -> dict:
        """Copy the model and extend it by setting var to val; return copy."""
        extended_model = model.copy()
        extended_model[var] = val
        return extended_model

    def prop_symbols(self, x: "Expr") -> set:
        """Return a set of all propositional symbols in x."""
        if not isinstance(x, Expr):
            return list()
        elif self.is_prop_symbol(x.op):
            return {x}
        else:
            return list(set(symbol for arg in x.args for symbol in self.prop_symbols(arg)))

    def tt_true(self, alpha: "Expr") -> bool:
        """Is the propositional sentence alpha a tautology?"""
        return self.tt_entails(self.TRUE, alpha)

    def pl_true(self, exp: "Expr", model: dict = {}) -> Optional[bool]:
        """Return True if the propositional logic expression is true in the model,
        and False if it is false. If the model does not specify the value for
        every proposition, this may return None to indicate 'not obvious';
        this may happen even when the expression is tautological."""
        op, args = exp.op, exp.args
        if exp == self.TRUE:
            return True
        elif exp == self.FALSE:
            return False
        elif self.is_prop_symbol(op):
            return model.get(exp)
        elif op == "~":
            p = self.pl_true(args[0], model)
            if p is None:
                return None
            else:
                return not p
        elif op == "|":
            result = False
            for arg in args:
                p = self.pl_true(arg, model)
                if p is True:
                    return True
                if p is None:
                    result = None
            return result
        elif op == "&":
            result = True
            for arg in args:
                p = self.pl_true(arg, model)
                if p is False:
                    return False
                if p is None:
                    result = None
            return result
        p, q = args
        if op == ">>":
            return self.pl_true(~p | q, model)
        elif op == "<<":
            return self.pl_true(p | ~q, model)
        pt = self.pl_true(p, model)
        if pt is None:
            return None
        qt = self.pl_true(q, model)
        if qt is None:
            return None
        if op == "<=>":
            return pt == qt
        elif op == "^":
            return pt != qt
        else:
            raise ValueError("illegal operator in logic expression" + str(exp))

    def to_cnf(s: "Expr") -> "Expr":
        """Converts a propositional logical sentence s to conjunctive normal form."""
        if not isinstance(s, Expr):
            return s
        s = Logic.eliminate_implications(s)
        s = Logic.move_not_inwards(s)
        return Logic.distribute_and_over_or(s)

    def eliminate_implications(s: "Expr") -> "Expr":
        """Change >>, <<, and <=> into &, |, and ~."""
        if not s.args or Logic.is_symbol(s.op):
            return s
        args = map(Logic.eliminate_implications, s.args)
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

    def move_not_inwards(s: "Expr") -> "Expr":
        """Rewrite sentence s by moving negation sign inward."""
        if s.op == "~":
            NOT = lambda b: Logic.move_not_inwards(~b)
            a = s.args[0]
            if a.op == "~":
                return Logic.move_not_inwards(a.args[0])
            if a.op == "&":
                return Logic.associate("|", map(NOT, a.args))
            if a.op == "|":
                return Logic.associate("&", map(NOT, a.args))
            return s
        elif Logic.is_symbol(s.op) or not s.args:
            return s
        else:
            return Expr(s.op, *map(Logic.move_not_inwards, s.args))

    def distribute_and_over_or(s: "Expr") -> "Expr":
        """Given a sentence s consisting of conjunctions and disjunctions of literals,
        return an equivalent sentence in CNF."""
        if s.op == "|":
            s = Logic.associate("|", s.args)
            if s.op != "|":
                return Logic.distribute_and_over_or(s)
            if len(s.args) == 0:
                return Logic.FALSE
            if len(s.args) == 1:
                return Logic.distribute_and_over_or(s.args[0])
            conj = next((d for d in s.args if d.op == "&"), None)
            if not conj:
                return s
            others = [a for a in s.args if a is not conj]
            rest = Logic.associate("|", others)
            return Logic.associate(
                "&", [Logic.distribute_and_over_or(c | rest) for c in conj.args]
            )
        elif s.op == "&":
            return Logic.associate("&", map(Logic.distribute_and_over_or, s.args))
        else:
            return s

    def associate(op: str, args: List["Expr"]) -> "Expr":
        """Given an associative op, return an expression with the same meaning as
        Expr(op, *args), but flattened."""
        args = Logic.dissociate(op, args)
        if len(args) == 0:
            return Logic._op_identity[op]
        elif len(args) == 1:
            return args[0]
        else:
            return Expr(op, *args)

    def dissociate(op: str, args: List["Expr"]) -> List["Expr"]:
        """Given an associative op, return a flattened list result such that
        Expr(op, *result) means the same as Expr(op, *args)."""
        result = []

        def collect(subargs):
            for arg in subargs:
                if arg.op == op:
                    collect(arg.args)
                else:
                    result.append(arg)

        collect(args)
        return result

    def conjuncts(s: "Expr") -> List["Expr"]:
        """Return a list of the conjuncts in the sentence s."""
        return Logic.dissociate("&", [s])

    def disjuncts(s: "Expr") -> List["Expr"]:
        """Return a list of the disjuncts in the sentence s."""
        return Logic.dissociate("|", [s])
