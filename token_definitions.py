from bool_types import CustomBool, Variable
from exceptions import LexerException, ParserException

tokens = (
    'TERM',
    'TRUE', 'FALSE',
    'AND', 'OR', 'NOT', 'IMPLIES',
)

literals = '()'

precedence = (
    ('nonassoc', 'IMPLIES'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

t_AND = r'/\\'
t_OR = r'\\/'
t_NOT = r'~'
t_IMPLIES = r'->'
t_TRUE = r'1'
t_FALSE = r'0'

t_ignore = ' \t'


# definition of a variable
def t_TERM(t):
    r'[A-Za-z_]\w*'
    return t


def t_error(t):
    raise LexerException(t.value)


def p_expression_true(p):
    """
    expression : TRUE
    """
    p[0] = CustomBool(True)


def p_expression_false(p):
    """
    expression : FALSE
    """
    p[0] = CustomBool(False)


def p_expression_term(p):
    """
    expression : TERM
    """
    p[0] = Variable(p[1])


def p_expression_and(p):
    """
    expression : expression AND expression
    """
    p[0] = p[1] & p[3]


def p_expression_or(p):
    """
    expression : expression OR expression
    """
    p[0] = p[1] | p[3]


def p_expression_implies(p):
    """
    expression : expression IMPLIES expression
    """
    p[0] = p[1] >> p[3]


def p_expression_negate(p):
    """
    expression : NOT expression
    """
    p[0] = ~p[2]


def p_expression_group(p):
    """
    expression : "(" expression ")"
    """
    p[0] = p[2]


def p_error(p):
    raise ParserException(p.value if p else 'EOF')
