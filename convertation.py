from bool_types import *


def to_CNF(tree):
    """
    Builds CNF for the given formula and returns it as the set of sets.
    Computing CNF uses the following equality:
    A(x, y) = (x \/ A(0, y)) /\ (~x \/ A(1, y))
    where y may be boolean vector (y_1, ..., y_k)
    """
    if isinstance(tree, (bool, CustomBool)):
        return bool(tree)

    # Formula that is not bool constant, always has at least one variable
    variable = extract_variables(tree).pop()

    subclauses1 = to_CNF(tree.subs(variable, False))
    if subclauses1 is True:
        subclauses1 = set()
    elif subclauses1 is False:
        subclauses1 = {frozenset({variable})}
    else:
        subclauses1 = {clause | {variable} for clause in subclauses1}

    subclauses2 = to_CNF(tree.subs(variable, True))
    if subclauses2 is True:
        subclauses2 = set()
    elif subclauses2 is False:
        subclauses2 = {frozenset({~variable})}
    else:
        subclauses2 = {clause | {~variable} for clause in subclauses2}

    result = subclauses1 | subclauses2
    if result == set():
        return True
    elif result == {frozenset({variable}), frozenset({~variable})}:
        return False
    else:
        return result


def to_DNF(tree):
    pass


def extract_variables(tree):
    """
    Returns set with all variables that are presented in the given formula.
    """
    if isinstance(tree, CustomBool):
        return set()
    elif isinstance(tree, Variable):
        return {tree}
    elif isinstance(tree, NegationOperator):
        return extract_variables(tree.value)
    elif isinstance(tree, BinaryOperator):
        return extract_variables(tree.left) | extract_variables(tree.right)
