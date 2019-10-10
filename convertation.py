from bool_types import *

def to_CNF(tree):
    pass


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
