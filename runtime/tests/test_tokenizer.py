
import unittest
from runtime.tokenizer import TokenType, Tokenizer,Token

class TestTokenizer(unittest.TestCase):

    def test_init(self):
        t = Tokenizer()
        self.assertEqual(t.script, "")
        self.assertEqual(t.cursor, 0)
        self.assertEqual(t.col, 0)
        self.assertEqual(t.row, 0)
        
    def test_tokenizer(self):
        t = Tokenizer()
        t.init("a")
        self.assertEqual(t.token().value, "a")
        self.assertEqual(t.token().type, TokenType.IDENTIFIER)

        t.init("12341")
        self.assertEqual(t.token().value, "12341")
        self.assertEqual(t.token().type, TokenType.INT)

        t.init("12341.1234124")
        self.assertEqual(t.token().value, "12341.1234124")
        self.assertEqual(t.token().type, TokenType.FLOAT)

        t.init("false")
        self.assertEqual(t.token().value, "false")
        self.assertEqual(t.token().type, TokenType.BOOL)

        t.init("\"false\"")
        self.assertEqual(t.token().value, "\"false\"")
        self.assertEqual(t.token().type, TokenType.STRING)
        
        t.init("helloworld")
        self.assertEqual(t.token().value, "helloworld")
        self.assertEqual(t.token().type, TokenType.IDENTIFIER)

        t.init("!")
        self.assertEqual(t.token().value, "!")
        self.assertEqual(t.token().type, TokenType.NOT)

        t.init("==")
        self.assertEqual(t.token().value, "==")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init("!=")
        self.assertEqual(t.token().value, "!=")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init("<=")
        self.assertEqual(t.token().value, "<=")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init(">=")
        self.assertEqual(t.token().value, ">=")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init("<")
        self.assertEqual(t.token().value, "<")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init(">")
        self.assertEqual(t.token().value, ">")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init("&&")
        self.assertEqual(t.token().value, "&&")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init("||")
        self.assertEqual(t.token().value, "||")
        self.assertEqual(t.token().type, TokenType.LOGICAL_OPERATOR)

        t.init("=")
        self.assertEqual(t.token().value, "=")
        self.assertEqual(t.token().type, TokenType.ASSIGNMENT)

        t.init("+")
        self.assertEqual(t.token().value, "+")
        self.assertEqual(t.token().type, TokenType.ADDITIVE_OPERATOR)

        t.init("-")
        self.assertEqual(t.token().value, "-")
        self.assertEqual(t.token().type, TokenType.ADDITIVE_OPERATOR)

        t.init("*")
        self.assertEqual(t.token().value, "*")
        self.assertEqual(t.token().type, TokenType.MULTIPLICATIVE_OPERATOR)

        t.init("/")
        self.assertEqual(t.token().value, "/")
        self.assertEqual(t.token().type, TokenType.MULTIPLICATIVE_OPERATOR)

        t.init("%")
        self.assertEqual(t.token().value, "%")
        self.assertEqual(t.token().type, TokenType.MULTIPLICATIVE_OPERATOR)

        t.init("(")
        self.assertEqual(t.token().value, "(")
        self.assertEqual(t.token().type, TokenType.LEFT_PAREN)

        t.init(")")
        self.assertEqual(t.token().value, ")")
        self.assertEqual(t.token().type, TokenType.RIGHT_PAREN)  

        t.init("{")
        self.assertEqual(t.token().value, "{")
        self.assertEqual(t.token().type, TokenType.LEFT_BRACE)

        t.init("}")
        self.assertEqual(t.token().value, "}")
        self.assertEqual(t.token().type, TokenType.RIGHT_BRACE)

    def test_init(self):
        t = Tokenizer()
        script = "a + 9 * ( 3 - 1 ) * 3 + 10 / 2;"
        t.init(script)
        self.assertEqual(t.script, script)
        self.assertEqual(len(t.tokens), 16)
        self.assertEqual(t.get_prev(), None)
        self.assertEqual(t.token().value, "a")
        self.assertEqual(t.get_next().value, "+")
        self.assertEqual(t.next().value, "+")
        self.assertEqual(t.next().value, "9")
        self.assertEqual(t.next().value, "*")
        t.prev()
        self.assertEqual(t.token().value, "9")
        t.prev()
        self.assertEqual(t.token().value, "+")

        script = "a + 9"
        t.init(script)
        self.assertEqual(t.token().type, TokenType.IDENTIFIER)
        self.assertEqual(t.next().type, TokenType.ADDITIVE_OPERATOR)
        self.assertEqual(t.next().type, TokenType.INT)
        self.assertEqual(t.next(), None)
        self.assertEqual(t._current_token_index, 3)
        self.assertEqual(t.next(), None)
        self.assertEqual(t.next(), None)
        self.assertEqual(t._current_token_index, 3)
        self.assertEqual(t.next(), None)
        t.prev()
        self.assertEqual(t.token().value, "9")
        t.prev()
        self.assertEqual(t.token().value, "+")
        t.prev()
        self.assertEqual(t.token().value, "a")
        t.prev()
        self.assertEqual(t.token().value, "a")