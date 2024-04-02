import re
from enum import Enum

from attr import dataclass

class TokenType(Enum):
    NEW_LINE = 1
    SPACE = 2
    COMMENTS = 3
    LEFT_PAREN = 4
    RIGHT_PAREN = 5
    COMMA = 6
    LEFT_BRACE = 7
    RIGHT_BRACE = 8
    SEMICOLON = 9
    LET = 10
    RETURN = 11
    IF = 12
    ELSE = 13
    WHILE = 14
    FOR = 15
    FLOAT = 18
    INT = 19
    IDENTIFIER = 20
    LOGICAL_OPERATOR = 21
    NOT = 22
    ASSIGNMENT = 23
    MULTIPLICATIVE_OPERATOR = 24
    ADDITIVE_OPERATOR = 25
    STRING = 26
    ARROW = 27
    BOOL = 28
    BREAK = 29
    TYPE_DEFINITION = 30
    COLON = 31

specs = (
    (re.compile(r"^\n"),TokenType.NEW_LINE),
    # Space:
    (re.compile(r"^\s"),TokenType.SPACE),
    # Comments:
    (re.compile(r"^//.*"), TokenType.COMMENTS),

    # Symbols:
    (re.compile(r"^\("), TokenType.LEFT_PAREN),
    (re.compile(r"^\)"), TokenType.RIGHT_PAREN),
    (re.compile(r"^\,"), TokenType.COMMA),
    (re.compile(r"^\{"), TokenType.LEFT_BRACE),
    (re.compile(r"^\}"), TokenType.RIGHT_BRACE),
    (re.compile(r"^;"), TokenType.SEMICOLON),
    (re.compile(r"^:"), TokenType.COLON),
    (re.compile(r"^=>"), TokenType.ARROW),

    # Keywords:
    (re.compile(r"^\blet\b"), TokenType.LET),
    (re.compile(r"^\breturn\b"), TokenType.RETURN),
    (re.compile(r"^\bif\b"), TokenType.IF),
    (re.compile(r"^\belse\b"), TokenType.ELSE),
    (re.compile(r"^\bwhile\b"), TokenType.WHILE),
    (re.compile(r"^\bfor\b"), TokenType.FOR),
    (re.compile(r"^\bbreak\b"), TokenType.BREAK),

    (re.compile(r"^\btrue\b"), TokenType.BOOL),
    (re.compile(r"^\bfalse\b"), TokenType.BOOL),

    # Type definition:
    (re.compile(r"^\bstring\b"), TokenType.TYPE_DEFINITION),
    (re.compile(r"^\bint\b"), TokenType.TYPE_DEFINITION),
    (re.compile(r"^\bfloat\b"), TokenType.TYPE_DEFINITION),
    (re.compile(r"^\bbool\b"), TokenType.TYPE_DEFINITION),
    (re.compile(r"^\bany\b"), TokenType.TYPE_DEFINITION),

    # Floats:
    (re.compile(r"^[0-9]+\.[0-9]+"), TokenType.FLOAT),

    # Ints:
    (re.compile(r"^[0-9]+"), TokenType.INT),

    # Identifiers:
    (re.compile(r"^\w+"),  TokenType.IDENTIFIER),


    # Logical operators:
    (re.compile(r"^&&"),  TokenType.LOGICAL_OPERATOR),
    (re.compile(r"^\|\|"), TokenType.LOGICAL_OPERATOR),
    (re.compile(r"^=="), TokenType.LOGICAL_OPERATOR),
    (re.compile(r"^!="), TokenType.LOGICAL_OPERATOR),
    (re.compile(r"^<="), TokenType.LOGICAL_OPERATOR),
    (re.compile(r"^>="), TokenType.LOGICAL_OPERATOR),
    (re.compile(r"^<"), TokenType.LOGICAL_OPERATOR),
    (re.compile(r"^>"), TokenType.LOGICAL_OPERATOR),

    (re.compile(r"^!"), TokenType.NOT),

    # Assignment:
    (re.compile(r"^="), TokenType.ASSIGNMENT),

    # Math operators: +, -, *, /:
    (re.compile(r"^[*/%]"), TokenType.MULTIPLICATIVE_OPERATOR),
    (re.compile(r"^[+-]"), TokenType.ADDITIVE_OPERATOR),

    # Double-quoted strings
    # TODO: escape character \" and
    (re.compile(r"^\"[^\"]*\""), TokenType.STRING),
)

@dataclass
class Token:
    type: TokenType
    value: str
    row: int
    col: int
    col_end: int
    cursor: int
    
    def __str__(self) -> str:
        return f"Token({self.type}, {self.value}, row={self.row}, col={self.col}, col_end={self.col_end}, cursor={self.cursor})"


class Tokenizer:

    def __init__(self):
        self._current_token = None
        self.script = ""
        self.cursor = 0
        self.col = 0
        self.row = 0
        self._current_token_index = 0
        self.tokens = list[Token]()
        self.checkpoint = list[int]()
    
    def init(self, script: str):
        self.checkpoint = list[int]()
        self.tokens = list[Token]()
        self._current_token_index = 0
        self._current_token = None
        self.script = script
        self.cursor = 0
        self.col = 0
        self.row = 0
        self._get_next_token()
        while self._current_token is not None:
            self.tokens.append(self._current_token)
            self._get_next_token()

    def checkpoint_push(self):
        self.checkpoint.append(self._current_token_index)
    
    def checkpoint_pop(self):
        self._current_token_index = self.checkpoint.pop()
    
    def next(self):
        if self._current_token_index < len(self.tokens):
            self._current_token_index += 1
        return self.token()
    
    def next_token_type(self):
        if self._current_token_index < len(self.tokens):
            self._current_token_index += 1
        return self.tokenType()

    def prev(self):
        if self._current_token_index > 0:
            self._current_token_index -= 1
        return self.token()
    
    def get_prev(self):
        if self._current_token_index == 0:
            return None
        return self.tokens[self._current_token_index - 1]
    
    def get_next(self):
        if self._current_token_index >= len(self.tokens):
            return None
        return self.tokens[self._current_token_index + 1]

    def token(self):
        if self._current_token_index >= len(self.tokens):
            return None
        return self.tokens[self._current_token_index]

    def tokenType(self):
        if self._current_token_index >= len(self.tokens):
            return None
        return self.tokens[self._current_token_index].type


    def _get_next_token(self):
        if self._is_eof():
            self._current_token = None
            return None
        _string = self.script[self.cursor:]
        for spec in specs:
            tokenValue, offset = self.match(spec[0], _string)
            if tokenValue == None:
                continue
            if spec[1] == TokenType.NEW_LINE:
                self.row += 1
                self.col = 0
                return self._get_next_token()
            if  spec[1] == TokenType.COMMENTS:
                return self._get_next_token()
            if spec[1] == TokenType.SPACE:
                self.col += offset
                return self._get_next_token()
            if spec[1] == None:
                return self._get_next_token()
            self._current_token = Token(spec[1],tokenValue, self.cursor, self.row, self.col, self.col + offset)
            self.col += offset
            return self.get_current_token()
        raise Exception("Unknown token: " + _string[0])
    
    def _is_eof(self):
        return self.cursor == len(self.script)
    
    def has_more_tokens(self):
        return self.cursor < len(self.script)

    def get_current_token(self):
        return self._current_token
    
    def match(self, reg: re, _script):
        matched = reg.search(_script)
        if matched == None:
            return None,0
        self.cursor = self.cursor + matched.span(0)[1]
        return matched[0], matched.span(0)[1]
    
    def eat(self, value: str | TokenType):
        if isinstance(value, str):
            return self.eat_value(value)
        if isinstance(value, TokenType):
            return self.eat_token_type(value)
    
    def eat_value(self, value: str):
        token = self.token()
        if token is None:
            raise Exception(f"Expected {value} but got None")
        if token.value != value:
            raise Exception(f"Expected {value} but got {token.value}")
        self.next()
        return token

    def eat_token_type(self,tokenType: TokenType):
        token = self.token()
        if token is None:
            raise Exception(f"Expected {tokenType} but got None")
        if token.type != tokenType:
            raise Exception(f"Expected {tokenType} but got {token.type}")
        self.next()
        return token
    
    def type_is(self, tokenType: TokenType):
        if self.token() is None:
            return False
        return self.token().type == tokenType
    
    def the_rest(self):
        return self.tokens[self._current_token_index:]