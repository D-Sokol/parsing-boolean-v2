#!/usr/bin/env python3
from ply.lex import lex
from ply import yacc

from exceptions import CustomException
from convertation import to_CNF, to_DNF
from token_definitions import *

lex()
yacc.yacc()

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
            if not s:
                continue
            parsed = yacc.parse(s)
            print('DNF: ', to_DNF(parsed))
            print('CNF: ', to_CNF(parsed))
        except EOFError:
            # add new line in output
            print()
            break
        except CustomException as ex:
            print(ex)
