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
    variable = pick_variable(tree)

    subclauses1 = to_CNF(tree.subs(variable, False))
    # Check some degenerate cases
    if subclauses1 is True:
        subclauses1 = set()
    elif subclauses1 is False:
        subclauses1 = {frozenset({variable})}
    else:
        subclauses1 = {clause | {variable} for clause in subclauses1}

    subclauses2 = to_CNF(tree.subs(variable, True))
    # Check some degenerate cases
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
    """
    Builds DNF for the given formula and returns it as the set of sets.
    Computing DNF uses the following equality:
    A(x, y) = (x /\ A(1, y)) \/ (~x /\ A(0, y))
    where y may be boolean vector (y_1, ..., y_k)
    """
    if isinstance(tree, (bool, CustomBool)):
        return bool(tree)

    # Formula that is not bool constant, always has at least one variable
    variable = pick_variable(tree)

    subclauses1 = to_DNF(tree.subs(variable, True))
    # Check some degenerate cases
    if subclauses1 is False:
        subclauses1 = set()
    elif subclauses1 is True:
        subclauses1 = {frozenset({variable})}
    else:
        subclauses1 = {clause | {variable} for clause in subclauses1}

    subclauses2 = to_DNF(tree.subs(variable, False))
    # Check some degenerate cases
    if subclauses2 is False:
        subclauses2 = set()
    elif subclauses2 is True:
        subclauses2 = {frozenset({~variable})}
    else:
        subclauses2 = {clause | {~variable} for clause in subclauses2}

    result = subclauses1 | subclauses2
    if result == set():
        return False
    elif result == {frozenset({variable}), frozenset({~variable})}:
        return True
    else:
        return result


def pick_variable(tree):
    """
    Returns first variable that are presented in the given formula.
    """
    if not isinstance(tree, Node):
        raise TypeError
    if isinstance(tree, CustomBool):
        return None
    while True:
        # tree cannot be CustomBool unless the very argument of function is CustomBool, what is checked.
        # Therefore, one of the next conditions always satisfied.
        if isinstance(tree, Variable):
            return tree
        elif isinstance(tree, NegationOperator):
            tree = tree.value
        elif isinstance(tree, BinaryOperator):
            tree = tree.left


def cnf_to_string(clauses):
    """
    Converts return value of to_CNF function to string.
    """
    if isinstance(clauses, (bool, CustomBool)):
        return '1' if clauses else '0'
    return r' /\ '.join(
                '({})'.format(r' \/ '.join(
                    str(var) for var in clause
                )) for clause in clauses
            )


def dnf_to_string(clauses):
    """
    Converts return value of to_DNF function to string.
    """
    if isinstance(clauses, (bool, CustomBool)):
        return '1' if clauses else '0'
    return r' \/ '.join(
                '({})'.format(r' /\ '.join(
                    str(var) for var in clause
                )) for clause in clauses
            )


def optimize_clauses(clauses, default_value=None, recursive=True):
    """
    Optimizes given set of clauses using clauses which are single variables.
    Returns equivalent set of clauses of default_value if the given set is
    degenerate (equivalent to constant 0 or 1 depending on outer context).
    """
    if isinstance(clauses, bool):
        return clauses

    result = {clause for clause in clauses if len(clause) == 1}
    if not result:
        return clauses or default_value
    variables = frozenset.union(*result)
    negated_variables = frozenset({~p for p in variables})
    if not variables.isdisjoint(negated_variables):
        return default_value

    for clause in clauses:
        if clause.isdisjoint(variables):
            new_clause = clause - negated_variables
            if new_clause:
                result.add(new_clause)
            else:
                return default_value
    if not result:
        return default_value
    elif not recursive or result == clauses:
        return result
    else:
        return optimize_clauses(result, default_value, recursive)