
import unittest
from runtime.ast import BoolLiteral, CallExpression, FloatLiteral, Identifier, IntLiteral, UnaryExpression
from runtime.interpreter import ExpressionParser, _priority, _try_fun_expression
from runtime.tokenizer import TokenType, Tokenizer,Token



class TestExpressionParser(unittest.TestCase):

    def test__try_fun_expression(self):
        t = Tokenizer()
        t.init("()")
        self.assertFalse(_try_fun_expression(t))

        t.init("() =>")
        self.assertTrue(_try_fun_expression(t))

        t.init("(a) =>")
        self.assertTrue(_try_fun_expression(t))

        t.init("(a,) =>")
        self.assertFalse(_try_fun_expression(t))

        t.init("(a,b,c,d) =>;")
        self.assertTrue(_try_fun_expression(t))

        t.init("(a,b,c,true) =>;")
        self.assertFalse(_try_fun_expression(t))

        t.init("(a,b,c,1.23) =>;")
        self.assertFalse(_try_fun_expression(t))

    def test_is_unary(self):
        t = Tokenizer()
        t.init("!")
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertTrue(pred)

        t.init("+")
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertTrue(pred)

        t.init("--123")
        t.next()
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertTrue(pred)

        t.init("+-123")
        t.next()
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertTrue(pred)

        t.init(")-123")
        t.next()
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertFalse(pred)

        t.init("=> - 123")
        t.next()
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertTrue(pred)

        t.init(", - 123")
        t.next()
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertTrue(pred)

        t.init("* - 123")
        t.next()
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertTrue(pred)

        t.init("* - 123")
        parser = ExpressionParser(t)
        pred = parser.is_unary()
        self.assertFalse(pred)

    def test_expression_parser(self):
        t = Tokenizer()
        t.init("a")
        parser = ExpressionParser(t)
        expression = parser.expression_parser()
        self.assertIsInstance(expression, Identifier)

        t.init("true")
        parser = ExpressionParser(t)
        expression = parser.expression_parser()
        self.assertIsInstance(expression, BoolLiteral)
        self.assertEqual(expression.value, True)

        t.init("false")
        parser = ExpressionParser(t)
        expression = parser.expression_parser()
        self.assertIsInstance(expression, BoolLiteral)
        self.assertEqual(expression.value, False)

        t.init("12341")
        parser = ExpressionParser(t)
        expression = parser.expression_parser()
        self.assertEqual(expression.value, 12341)
        self.assertIsInstance(expression, IntLiteral)

        t.init("12341.42")
        parser = ExpressionParser(t)
        expression = parser.expression_parser()
        self.assertEqual(expression.value, 12341.42)
        self.assertIsInstance(expression, FloatLiteral)

        t.init("hello")
        parser = ExpressionParser(t)
        expression: Identifier = parser.expression_parser()
        self.assertIsInstance(expression, Identifier)
        self.assertEqual(expression.name, "hello")
        
        t.init("print()")
        parser = ExpressionParser(t)
        expression: CallExpression = parser.expression_parser()
        self.assertIsInstance(expression, CallExpression)
        self.assertEqual(expression.callee.name, "print")

        t.init("print(1,2,3,hello)")
        parser = ExpressionParser(t)
        expression: CallExpression = parser.expression_parser()
        self.assertIsInstance(expression, CallExpression)
        self.assertEqual(expression.callee.name, "print")
        self.assertEqual(len(expression.arguments), 4)

    def test_binary_expression(self):
        t = Tokenizer()

    def test__priority(self):
        self.assertEqual(_priority("*"), 0)
        self.assertEqual(_priority("/"), 0)
        self.assertEqual(_priority("%"), 0)
        self.assertEqual(_priority("+"), 1)
        self.assertEqual(_priority("-"), 1)
        self.assertEqual(_priority(">"), 2)
        self.assertEqual(_priority("<"), 2)
        self.assertEqual(_priority(">="), 2)
        self.assertEqual(_priority("<="), 2)
        self.assertEqual(_priority("=="), 3)
        self.assertEqual(_priority("!="), 3)
        self.assertEqual(_priority("&&"), 4)
        self.assertEqual(_priority("||"), 5)