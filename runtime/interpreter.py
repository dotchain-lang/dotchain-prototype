from ast import Expression
import copy
from runtime.ast import Assignment, BinaryExpression, Block, BoolLiteral, BreakStatement, CallExpression, EmptyStatement, FloatLiteral, Fun, Identifier, IfStatement, IntLiteral, Program, ReturnStatement, Statement, StringLiteral, UnaryExpression, VariableDeclaration, WhileStatement
from .tokenizer import Token, TokenType, Tokenizer

unary_prev_statement = [
    TokenType.COMMENTS,
    TokenType.LEFT_PAREN,
    TokenType.COMMA,
    TokenType.LEFT_BRACE,
    TokenType.RIGHT_BRACE,
    TokenType.SEMICOLON,
    TokenType.LET,
    TokenType.RETURN,
    TokenType.IF,
    TokenType.ELSE,
    TokenType.WHILE,
    TokenType.FOR,
    TokenType.LOGICAL_OPERATOR,
    TokenType.NOT,
    TokenType.ASSIGNMENT,
    TokenType.MULTIPLICATIVE_OPERATOR,
    TokenType.ADDITIVE_OPERATOR,
    TokenType.ARROW,
]

unary_end_statement = [
    TokenType.MULTIPLICATIVE_OPERATOR,
    TokenType.ADDITIVE_OPERATOR,
    TokenType.LOGICAL_OPERATOR,
]

end_statement = [
    TokenType.SEMICOLON,
    TokenType.COMMA,
    TokenType.ARROW,
    TokenType.RETURN,
    TokenType.LET,
    TokenType.IF,
    TokenType.ELSE,
    TokenType.WHILE,
    TokenType.FOR,
    TokenType.ASSIGNMENT,
    TokenType.RIGHT_BRACE,
    TokenType.LEFT_BRACE,
]

def program_parser(tkr: Tokenizer):
    statements = list[Statement]()
    count = 0
    while True:
        if tkr.token() is None:
            break
        if tkr.token().type == TokenType.SEMICOLON:
            tkr.next()
            continue
        statement = statement_parser(tkr)
        statements.append(statement)
        count += 1
    return Program(statements)

def if_parser(tkr: Tokenizer):
    tkr.eat(TokenType.IF)
    condition = ExpressionParser(tkr).parse()
    block = block_statement(tkr)
    if tkr.type_is(TokenType.ELSE):
        tkr.eat(TokenType.ELSE)
        if tkr.type_is(TokenType.IF):
            print("else if")
            return IfStatement(condition, block, Block([if_parser(tkr)]))
        return IfStatement(condition, block, block_statement(tkr))
    return IfStatement(condition, block, Block([]))

def while_parser(tkr: Tokenizer):
    tkr.eat(TokenType.WHILE)
    condition = ExpressionParser(tkr).parse()
    block = block_statement(tkr)
    return WhileStatement(condition, block)


def identifier(tkr: Tokenizer):
    token = tkr.token()
    if token.type != TokenType.IDENTIFIER:
        raise Exception("Invalid identifier", token)
    tkr.next()
    return Identifier(token.value)

def block_statement(tkr: Tokenizer):
    tkr.eat(TokenType.LEFT_BRACE)
    statements = list[Statement]()
    while True:
        if tkr.token() is None:
            raise Exception("Invalid block expression", tkr.token())
        if tkr.tokenType() == TokenType.RIGHT_BRACE:
            tkr.eat(TokenType.RIGHT_BRACE)
            break
        if tkr.tokenType() == TokenType.SEMICOLON:
            tkr.next()
            continue
        statements.append(statement_parser(tkr))
    return Block(statements)


def return_parser(tkr: Tokenizer):
    tkr.eat(TokenType.RETURN)
    return ReturnStatement(ExpressionParser(tkr).parse())

def statement_parser(tkr: Tokenizer):
    token = tkr.token()
    if token is None:
        return EmptyStatement()
    if token.type == TokenType.SEMICOLON:
        tkr.next()
        return EmptyStatement()
    if token.type == TokenType.LET:
        return let_expression_parser(tkr)
    if _try_assignment_expression(tkr):
        return assignment_parser(tkr)
    if token.type == TokenType.IF:
        return if_parser(tkr)
    if token.type == TokenType.WHILE:
        return while_parser(tkr)
    if token.type == TokenType.RETURN:
        return return_parser(tkr)
    if token.type == TokenType.BREAK:
        tkr.eat(TokenType.BREAK)
        return BreakStatement()
    return ExpressionParser(tkr).parse()

def assignment_parser(tkr: Tokenizer):
    id = identifier(tkr)
    tkr.eat(TokenType.ASSIGNMENT)
    return Assignment(id, ExpressionParser(tkr).parse())

def let_expression_parser(tkr: Tokenizer):
    tkr.eat(TokenType.LET)
    token = tkr.token()
    if token.type != TokenType.IDENTIFIER:
        raise Exception("Invalid let statement", token)
    id = identifier(tkr)
    token = tkr.token()
    if token is None:
        raise Exception("Invalid let statement", token)
    if token.type != TokenType.ASSIGNMENT:
        raise Exception("Invalid let statement", token.type)
    tkr.next()
    ast = ExpressionParser(tkr).parse()
    return VariableDeclaration(id, ast)

class ExpressionParser:

    def __init__(self, tkr: Tokenizer):
        self.stack = list[Expression | Token]()
        self.operator_stack = list[Token]()
        self.tkr = tkr

    def parse(self, unary = False):
        while not self.is_end():
            token = self.tkr.token()
            if unary and not self.is_unary() and token.type in unary_end_statement:
                break
            if self.is_unary():
                self.push_stack(self.unary_expression_parser())
            elif self._try_fun_expression():
                return self.fun_expression()
            # -(hello x 123) // !(true and false)
            elif unary and token.type == TokenType.LEFT_PAREN:
                self.tkr.next()
                self.push_stack(ExpressionParser(self.tkr).parse())
            elif self._is_operator(token) or token.type in [TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN ]:
                self.push_operator_stack(token)
                self.tkr.next()
            else:
                self.push_stack(self.expression_parser())
        self.pop_all()
        return self.expression()
    
    def expression(self):
        if len(self.stack) == 0:
            return EmptyStatement()
        if len(self.stack) == 1:
            return self.stack[0]
        return expression_list_to_binary(self.stack)

    def expression_parser(self):
        token = self.tkr.token()
        if token is None:
            return EmptyStatement()
        expression = None
        if token.type == TokenType.INT:
            self.tkr.eat(TokenType.INT)
            expression = IntLiteral(int(token.value))
        elif token.type == TokenType.FLOAT:
            self.tkr.eat(TokenType.FLOAT)
            expression = FloatLiteral(float(token.value))
        elif token.type == TokenType.STRING:
            self.tkr.eat(TokenType.STRING)
            expression = StringLiteral(token.value[1:-1])
        elif token.type == TokenType.BOOL:
            self.tkr.eat(TokenType.BOOL)
            expression = BoolLiteral(token.value == "true")
        elif token.type == TokenType.IDENTIFIER:
            expression = self.identifier_or_fun_call_parser()
        return expression
    
    def _try_fun_expression(self):
        return _try_fun_expression(self.tkr)
    
    def fun_expression(self):
        tkr = self.tkr
        tkr.next()
        args = list[Identifier]()
        token_type = tkr.tokenType()
        while token_type != TokenType.RIGHT_PAREN:
            args.append(Identifier(tkr.token().value))
            tkr.next()
            token_type = tkr.tokenType()
            if token_type == TokenType.RIGHT_PAREN:
                break
            tkr.next()
            token_type = tkr.tokenType()
        token_type = tkr.next_token_type()
        if token_type != TokenType.ARROW:
            raise Exception("Invalid fun_expression", tkr.token())
        tkr.next()
        return Fun(args, block_statement(tkr))

    def push_stack(self, expression: Expression | Token):
        self.stack.append(expression)

    def _pop_by_right_paren(self):
        token = self.operator_stack.pop()
        if token.type != TokenType.LEFT_PAREN:
            self.push_stack(token)
            self._pop_by_right_paren()

    def pop(self):
        self.push_stack(self.operator_stack.pop())

    def pop_all(self):
        while len(self.operator_stack) > 0:
            self.pop()

    def push_operator_stack(self, token: Token):
        if len(self.operator_stack) == 0:
            self.operator_stack.append(token)
            return
        if token.type == TokenType.LEFT_PAREN:
            self.operator_stack.append(token)
            return
        if token.type == TokenType.RIGHT_PAREN:
            self._pop_by_right_paren()
            return
        top_operator = self.operator_stack[-1]
        if top_operator.type == TokenType.LEFT_PAREN:
            self.operator_stack.append(token)
            return
        # priority is in descending order
        if self._priority(token) >= self._priority(top_operator):
            self.pop()
            self.push_operator_stack(token)
            return
        self.operator_stack.append(token)

    def unary_expression_parser(self):
        token = self.tkr.token()
        self.tkr.next()
        return UnaryExpression(token.value, ExpressionParser(self.tkr).parse(True))

    def identifier_or_fun_call_parser(self):
        id = self.identifier()
        tokenType = self.tkr.tokenType()
        if tokenType == TokenType.LEFT_PAREN:
            return self.fun_call_parser(id)
        return id
    
    def fun_call_parser(self, id: Identifier):
        self.tkr.eat(TokenType.LEFT_PAREN)
        args = list[Expression]()
        while self.tkr.tokenType() != TokenType.RIGHT_PAREN:
            args.append(ExpressionParser(self.tkr).parse())
            if self.tkr.tokenType() == TokenType.COMMA:
                self.tkr.eat(TokenType.COMMA)
        self.tkr.eat(TokenType.RIGHT_PAREN)
        return CallExpression(id, args)

    def identifier(self):
        return identifier(self.tkr)

    def is_unary(self):
        token = self.tkr.token()
        if not self.unary_operator(token):
            return False
        if token.type == TokenType.NOT:
            return True
        prev_token = self.tkr.get_prev()
        if prev_token is None:
            return True
        if prev_token.type == TokenType.LEFT_PAREN:
            return True
        if prev_token.type in unary_prev_statement:
            return True
        return False
    
    def unary_operator(self, token: Token):
        if token is None:
            return False
        return token.value in ["+", "-", "!"]

    def _has_brackets(self):
        return TokenType.LEFT_PAREN in map(lambda x: x.type, self.operator_stack)

    def is_end(self):
        token = self.tkr.token()
        if token is None:
            return True
        if token.type == TokenType.SEMICOLON:
            return True
        if not self._has_brackets() and token.type == TokenType.RIGHT_PAREN:
            return True
        if token.type in end_statement:
            return True
        return False
    
    def _is_operator(self, token: Token):
        if token is None:
            return False
        return token.type in [TokenType.ADDITIVE_OPERATOR, TokenType.MULTIPLICATIVE_OPERATOR, TokenType.LOGICAL_OPERATOR, TokenType.NOT]
    
    def _debug_print_tokens(self):
        print("operator stack:----")
        for token in self.operator_stack:
            print(token)

    def _debug_print_stack(self):
        print("stack:----")
        for expression in self.stack:
            print(expression)
    
    def _priority(self, token: Token):
        return _priority(token.value)

def expression_list_to_binary(expression_list: list[Expression | Token], stack: list = None):
    if stack is None:
        stack = list()
    if len(expression_list) == 0:
        return stack[0]
    top = expression_list[0]
    if isinstance(top, Token):
        right = stack.pop()
        left = stack.pop()
        return expression_list_to_binary(expression_list[1:], stack + [BinaryExpression(left, top.value, right)])
    else:
        stack.append(top)
        return expression_list_to_binary(expression_list[1:], stack)

def _priority(operator: str):
    priority = 0
    if operator in ["*", "/", "%"]:
        return priority
    priority += 1
    if operator in ["+", "-"]:
        return priority
    priority += 1
    if operator in ["<", ">", "<=", ">="]:
        return priority
    priority += 1
    if operator in ["==", "!="]:
        return priority
    priority += 1
    if operator in ["&&"]:
        return priority
    priority += 1
    if operator in ["||"]:
        return priority
    priority += 1
    return priority

def _try_assignment_expression(tkr: Tokenizer):
    tkr = copy.deepcopy(tkr)
    token = tkr.token()
    if token is None:
        return False
    if token.type != TokenType.IDENTIFIER:
        return False
    tkr.next()
    token = tkr.token()
    if token is None:
        return False
    if token.type != TokenType.ASSIGNMENT:
        return False
    return True

def _try_fun_expression(_tkr: Tokenizer):
    tkr = copy.deepcopy(_tkr)
    token = tkr.token()
    if token is None:
        return False
    if token.type != TokenType.LEFT_PAREN:
        return False
    tkr.next()
    token_type = tkr.tokenType()
    while token_type != TokenType.RIGHT_PAREN:
        if token_type == TokenType.IDENTIFIER:
            tkr.next()
            token_type = tkr.tokenType()
            if token_type == TokenType.RIGHT_PAREN:
                break
            if token_type != TokenType.COMMA:
                return False
            tkr.next()
            token_type = tkr.tokenType()
            if token_type == TokenType.RIGHT_PAREN:
                return False
        else:
            return False
    token_type = tkr.next_token_type()
    if token_type != TokenType.ARROW:
        return False
    return True