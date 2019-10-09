class Node:
    pass


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
