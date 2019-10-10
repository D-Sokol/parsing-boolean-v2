class Node:
    """
    Base class for representing formula in a binary tree.

    This class supports some standard operations in the infix form,
    so one can write "F1 & F2" instead of BinaryConjunction(F1, F2).
    """
    def subs(self, term, value):
        """
        Returns new formula that is equivalent given self, if replace all occurrences of
        variable term in self by boolean constant value.
        """
        raise NotImplementedError

    def __invert__(self):
        return NegationOperator(self)

    def __and__(self, other):
        return BinaryConjunction(self, other)

    def __or__(self, other):
        return BinaryDisjunction(self, other)

    def __rshift__(self, other):
        return BinaryImplication(self, other)


class CustomBool(Node, int):
    """
    Custom Boolean type, overloading negation and convertion to string
    Normal bool type does not provide correct '~' operator, since bool(~True) == True.
    """
    def __repr__(self):
        return '1' if self else '0'

    def subs(self, term, value):
        return self


class Variable(Node):
    """
    Represents one boolean variable.
    """
    def __init__(self, letter):
        self.letter = letter

    def subs(self, term, value):
        if self == term:
            return CustomBool(value)
        else:
            return self

    def __repr__(self):
        return self.letter

    def __eq__(self, value):
        if not isinstance(value, Variable):
            return False
        return self.letter == value.letter

    def __hash__(self):
        return hash(self.letter)


class NegationOperator(Node):
    truth_table = []

    def __new__(cls, value):
        if isinstance(value, CustomBool):
            return CustomBool(not value)
        elif isinstance(value, NegationOperator):
            return value.value
        else:
            self = super().__new__(cls)
            self.value = value
            return self

    def subs(self, term, value):
        return NegationOperator(self.value.subs(term, value))

    def __eq__(self, other):
        if not isinstance(other, NegationOperator):
            return False
        return self.value == other.value

    def __repr__(self):
        return '~{}'.format(self.value)

    def __hash__(self):
        return hash((False, self.value))


class BinaryOperator(Node):
    # cls(False, False), cls(False, True), cls(True, False), cls(True, True)
    truth_table = []
    # string form of this binary operator. Used when one prints the BinaryOperator instance.
    operator = ''

    def __new__(cls, left, right):
        """
        In general case returns BinaryOperator object that stores given left and right formulas.
        However, if at least one of arguments are constant or arguments are the same,
        returns equivalent simplified Node instance.
        """
        left_bool, right_bool = isinstance(left, CustomBool), isinstance(right, CustomBool)
        if left_bool and right_bool:
            return CustomBool(cls.truth_table[2 * left + right])
        elif left_bool:
            options = [cls.truth_table[2 * left], cls.truth_table[2 * left + 1]]
            if options[0] == options[1]:
                return CustomBool(options[0])
            elif options[0]:
                return NegationOperator(right)
            else:
                return right
        elif right_bool:
            options = [cls.truth_table[right], cls.truth_table[2 + right]]
            if options[0] == options[1]:
                return CustomBool(options[0])
            elif options[0]:
                return NegationOperator(left)
            else:
                return left
        elif left == right:
            options = [cls.truth_table[0], cls.truth_table[3]]
            if options[0] == options[1]:
                return CustomBool(options[0])
            elif options[0]:
                return NegationOperator(left)
            else:
                return left
        elif left == ~right:
            options = [cls.truth_table[1], cls.truth_table[2]]
            if options[0] == options[1]:
                return CustomBool(options[0])
            elif options[0]:
                return NegationOperator(left)
            else:
                return left
        else:
            self = super().__new__(cls)
            self.left = left
            self.right = right
            return self

    def subs(self, term, value):
        return type(self)(self.left.subs(term, value), self.right.subs(term, value))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.left == other.left and self.right == other.right
        return NotImplemented

    def __repr__(self):
        return '({left} {op} {right})'.format(left=self.left, op=self.operator, right=self.right)

    def __hash__(self):
        return hash((self.left, self.right))


class BinaryConjunction(BinaryOperator):
    truth_table = [False, False, False, True]
    operator = '/\\'


class BinaryDisjunction(BinaryOperator):
    truth_table = [False, True, True, True]
    operator = '\\/'


class BinaryImplication(BinaryOperator):
    truth_table = [True, True, False, True]
    operator = '->'
