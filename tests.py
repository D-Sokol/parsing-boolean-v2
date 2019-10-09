#!/usr/bin/env python3

import unittest

from bool_types import *
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


if __name__ == '__main__':
    unittest.main()
