#!/usr/bin/env python3
import functools
import itertools
import operator
import unittest

from bool_types import *
from convertation import *
from parser import yacc
from exceptions import LexerException, ParserException


p, q, r = Variable('p'), Variable('q'), Variable('r')
t, f = CustomBool(True), CustomBool(False)


class TestCustomBoolean(unittest.TestCase):
    def test_inversion(self):
        self.assertTrue(t)
        self.assertFalse(f)
        self.assertFalse(~t)
        self.assertTrue(~f)

    def test_equals(self):
        self.assertEqual(t, t)
        self.assertEqual(f, f)
        self.assertEqual(t, ~f)
        self.assertEqual(~t, f)
        self.assertNotEqual(t, f)
        self.assertNotEqual(t, ~t)
        self.assertNotEqual(~f, f)
        self.assertEqual(~~~~~~~~t, t)

    def test_operations(self):
        self.assertEqual(t | t, t)
        self.assertEqual(t | f, t)
        self.assertEqual(f | t, t)
        self.assertEqual(f | f, f)
        self.assertEqual(t & t, t)
        self.assertEqual(t & f, f)
        self.assertEqual(f & t, f)
        self.assertEqual(f & f, f)
        self.assertEqual(t >> t, t)
        self.assertEqual(t >> f, f)
        self.assertEqual(f >> t, t)
        self.assertEqual(f >> f, t)

    def test_str(self):
        self.assertEqual(str(t), '1')
        self.assertEqual(str(f), '0')


class TestVariable(unittest.TestCase):
    def test_creation(self):
        lam = Variable('lambda')
        self.assertEqual(lam.letter, 'lambda')

    def test_str(self):
        long_name = 'ewriuwoieuroiu'
        l = Variable(long_name)
        self.assertEqual(str(p), 'p')
        self.assertEqual(str(q), 'q')
        self.assertEqual(str(l), long_name)

    def test_equal(self):
        self.assertEqual(p, p)
        self.assertEqual(~~p, p)
        self.assertNotEqual(p, q)
        self.assertNotEqual(p, ~p)

    def test_trivial_operations(self):
        for p_ in (p, ~p):
            with self.subTest(negated=(p_ == p)):
                self.assertEqual(p_ | t, t)
                self.assertEqual(p_ | f, p_)
                self.assertEqual(t | p_, t)
                self.assertEqual(f | p_, p_)
                self.assertEqual(p_ & t, p_)
                self.assertEqual(p_ & f, f)
                self.assertEqual(t & p_, p_)
                self.assertEqual(f & p_, f)
                self.assertEqual(p_ >> t, t)
                self.assertEqual(p_ >> f, ~p_)
                self.assertEqual(t >> p_, p_)
                self.assertEqual(f >> p_, t)
                self.assertEqual(p_ | p_, p_)
                self.assertEqual(p_ & p_, p_)
                self.assertEqual(p_ | ~p_, t)
                self.assertEqual(p_ & ~p_, f)
                self.assertEqual(p_ >> p_, t)
                self.assertEqual(p_ >> ~p_, ~p_)

    def test_substitutions(self):
        self.assertEqual(p.subs(p, True), t)
        self.assertEqual(p.subs(p, False), f)
        self.assertEqual(p.subs(q, True), p)
        self.assertEqual(p.subs(q, False), p)

    def test_operations(self):
        self.assertEqual(p & q, BinaryConjunction(p, q))
        self.assertEqual(p & ~q, BinaryConjunction(p, ~q))
        self.assertEqual(p | q, BinaryDisjunction(p, q))
        self.assertEqual(p | ~q, BinaryDisjunction(p, ~q))
        self.assertEqual(p >> q, BinaryImplication(p, q))
        self.assertEqual(p >> ~q, BinaryImplication(p, ~q))


class TestNegation(unittest.TestCase):
    def test_creation(self):
        with self.subTest('from Boolean'):
            self.assertEqual(NegationOperator(f), t)
            self.assertEqual(NegationOperator(t), f)
        with self.subTest('from Variable'):
            not_q = NegationOperator(q)
            self.assertIsInstance(not_q, NegationOperator)
            self.assertEqual(not_q.value, q)
            self.assertEqual(not_q, ~q)
            not_not_p = NegationOperator(~p)
            self.assertIsInstance(not_not_p, Variable)
            self.assertEqual(not_not_p, p)
        with self.subTest('from Formula'):
            not_c = NegationOperator(p & q)
            self.assertIsInstance(not_c, NegationOperator)
            self.assertEqual(not_c.value, p & q)
            not_d = NegationOperator(q | ~p)
            self.assertIsInstance(not_d, NegationOperator)
            self.assertEqual(not_d.value, q | ~p)

    def test_substitutions(self):
        not_q = NegationOperator(q)
        self.assertEqual(not_q.subs(q, False), True)
        self.assertEqual(not_q.subs(q, True), False)
        self.assertEqual(not_q.subs(p, False), not_q)
        not_c = NegationOperator(p & q)
        self.assertEqual(not_c.subs(p, False), True)
        self.assertEqual(not_c.subs(p, True), not_q)
        self.assertEqual(not_c.subs(r, False), not_c)

    def test_str(self):
        not_q = NegationOperator(q)
        not_c = NegationOperator(p & q)
        self.assertEqual(str(not_q), '~q')
        self.assertEqual(str(not_c), r'~(p /\ q)')


class TestConjunction(unittest.TestCase):
    def test_creation(self):
        c1 = BinaryConjunction(p, q)
        self.assertIsInstance(c1, BinaryConjunction)
        self.assertEqual(c1.left, p)
        self.assertEqual(c1.right, q)
        self.assertEqual(c1 & c1, c1)
        c2 = BinaryConjunction(p & q, ~r)
        self.assertIsInstance(c2, BinaryConjunction)
        self.assertEqual(c2.left, c1)
        self.assertEqual(c2.right, ~r)

    def test_substitutions(self):
        c2 = BinaryConjunction(p & q, ~r)
        self.assertEqual(c2.subs(r, False), p & q)
        self.assertEqual(c2.subs(r, True), f)
        self.assertEqual(c2.subs(p, True), q & ~r)

    def test_str(self):
        self.assertEqual(str(p & q), r'(p /\ q)')
        self.assertEqual(str((p & q) & ~r), r'((p /\ q) /\ ~r)')


class TestDisjunction(unittest.TestCase):
    def test_creation(self):
        d1 = BinaryDisjunction(p, q)
        self.assertIsInstance(d1, BinaryDisjunction)
        self.assertEqual(d1.left, p)
        self.assertEqual(d1.right, q)
        self.assertEqual(d1 | d1, d1)
        d2 = BinaryDisjunction(p & q, ~r)
        self.assertIsInstance(d2, BinaryDisjunction)
        self.assertEqual(d2.left, p & q)
        self.assertEqual(d2.right, ~r)

    def test_substitutions(self):
        d2 = BinaryDisjunction(p & q, ~r)
        self.assertEqual(d2.subs(r, False), t)
        self.assertEqual(d2.subs(r, True), p & q)
        self.assertEqual(d2.subs(p, True), q | ~r)
        self.assertEqual(d2.subs(Variable('t'), False), d2)

    def test_str(self):
        self.assertEqual(str(p | q), r'(p \/ q)')
        self.assertEqual(str((p & q) | ~r), r'((p /\ q) \/ ~r)')


class TestParser(unittest.TestCase):
    def test_trivial(self):
        self.assertEqual(yacc.parse('p'), p)
        self.assertEqual(yacc.parse('~q'), ~q)
        self.assertEqual(yacc.parse('1'), t)
        self.assertEqual(yacc.parse('0'), f)
        self.assertEqual(yacc.parse(r'p \/ q'), BinaryDisjunction(p, q))
        self.assertEqual(yacc.parse(r'p /\ q'), BinaryConjunction(p, q))
        self.assertEqual(yacc.parse(r'p -> q'), BinaryImplication(p, q))

    def test_simplify(self):
        self.assertEqual(yacc.parse(r'p /\ p'), p)
        self.assertEqual(yacc.parse(r'p /\ ~p'), f)
        self.assertEqual(yacc.parse(r'p \/ p'), p)
        self.assertEqual(yacc.parse(r'p \/ 1'), t)
        self.assertEqual(yacc.parse(r'p /\ 0'), f)
        self.assertEqual(yacc.parse('(p) -> ~(p)'), ~p)
        self.assertEqual(yacc.parse('~~((~p)) -> 0'), p)

    def test_lexer_errors(self):
        inputs = ['p + 1', r'q > q', '2', '1 -p', '0 >- 1', r'r / \ 1']
        for line in inputs:
            with self.subTest(line):
                self.assertRaises(LexerException, yacc.parse, line)

    def test_parse_errors(self):
        inputs = [r'p \/', '1 1 1', 'p q', 'p -> ((q)', '(~)p', r'p \/ /\ q']
        for line in inputs:
            with self.subTest(line):
                self.assertRaises(ParserException, yacc.parse, line)

    def test_priority(self):
        self.assertEqual(yacc.parse(r'~x \/ y'), yacc.parse(r'(~x) \/ y'))
        self.assertEqual(yacc.parse(r'~x /\ y'), yacc.parse(r'(~x) /\ y'))
        self.assertEqual(yacc.parse(r'x /\ y \/ z'), yacc.parse(r'(x /\ y) \/ z'))

        # There are no general agreement how to interpret this line, so one have to use brackets here.
        self.assertRaises(ParserException, yacc.parse, r'x -> y -> z')

    def test_readability(self):
        formula = r'(p->q) /\ (q->s) /\ (s->r) /\ (r->~p) /\ p'
        parsed = yacc.parse(formula)
        self.assertEqual(parsed,
            BinaryConjunction(
                BinaryConjunction(
                    BinaryConjunction(
                        BinaryConjunction(
                            BinaryImplication(Variable('p'), Variable('q')),
                            BinaryImplication(Variable('q'), Variable('s'))
                        ),
                        BinaryImplication(Variable('s'), Variable('r'))
                    ),
                    BinaryImplication(Variable('r'), NegationOperator(Variable('p')))
                ),
                Variable('p')
            )
        )


class TestConvertation(unittest.TestCase):
    def test_extraction(self):
        self.assertSetEqual(extract_variables(t), set())
        self.assertSetEqual(extract_variables(p), {p})
        self.assertSetEqual(extract_variables(~p), {p})
        self.assertSetEqual(extract_variables(p & q), {p, q})
        self.assertSetEqual(extract_variables(p >> (r | ~q)), {p, q, r})

    def test_DNF(self):
        self.assertSetEqual(to_DNF(p), {frozenset({p})})
        self.assertSetEqual(to_DNF(~p), {frozenset({~p})})
        self.assertSetEqual(to_DNF(p & ~q), {frozenset({p, ~q})})

        formula = (p & q) >> (r | (~q & p))
        dnf = functools.reduce(operator.or_,
                               [functools.reduce(operator.and_, clause) for clause in to_DNF(formula)])
        # Verify that both formulas are equivalent for all assignments.
        for p_, q_, r_ in itertools.product([True, False], repeat=3):
            expected = formula.subs(p, p_).subs(q, q_).subs(r, r_)
            observed = dnf.subs(p, p_).subs(q, q_).subs(r, r_)
            self.assertEqual(expected, observed)

    def test_CNF(self):
        self.assertSetEqual(to_CNF(p), {frozenset({p})})
        self.assertSetEqual(to_CNF(~p), {frozenset({~p})})
        self.assertSetEqual(to_CNF(p | ~q), {frozenset({p, ~q})})

        formula = (p & q) >> (r | (~q & p))
        cnf = functools.reduce(operator.and_,
                               [functools.reduce(operator.or_, clause) for clause in to_CNF(formula)])
        # Verify that both formulas are equivalent for all assignments.
        for p_, q_, r_ in itertools.product([True, False], repeat=3):
            expected = formula.subs(p, p_).subs(q, q_).subs(r, r_)
            observed = cnf.subs(p, p_).subs(q, q_).subs(r, r_)
            self.assertEqual(expected, observed)


if __name__ == '__main__':
    unittest.main()
