#!/bin/bash
. venv/bin/activate

for pyshell in ipython3 python3; do
    if command -v $pyshell >/dev/null; then
        break
    fi
done

$pyshell -i -c\
"
from ply import lex, yacc
from token_definitions import *
__file__ = 'ipython.py'
lex.lex()
yacc.yacc()
from bool_types import *
p, q = Variable('p'), Variable('q')
t, f = CustomBool(True), CustomBool(False)
"
