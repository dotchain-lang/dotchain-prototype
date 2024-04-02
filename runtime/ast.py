from abc import ABC, abstractmethod

from attr import dataclass

from runtime.runtime import Runtime

@dataclass
class ReturnValue():
    value: any

class Node(ABC):
    def type(self):
        return self.__class__.__name__

@dataclass
class Statement(Node, ABC):
    
    @abstractmethod
    def exec(self, runtime: Runtime):
        print(self)
        pass

    @abstractmethod
    def dict(self):
        pass

@dataclass
class Expression(Node):

    @abstractmethod
    def eval(self, runtime: Runtime):
        pass

    @abstractmethod
    def dict(self):
        pass

@dataclass
class Literal(Expression):
    value: str | int | float | bool
    def eval(self, runtime: Runtime):
        return self.value
    
    def dict(self) -> dict:
        return {
            "type": "Literal",
            "value": self.value
        }
    
@dataclass
class StringLiteral(Literal):
    value: str

    def dict(self) -> dict:
        return {
            "type": "StringLiteral",
            "value": self.value
        }
    
@dataclass
class IntLiteral(Literal):
    value: int
    
    def dict(self):
        return {
            "type": "IntLiteral",
            "value": self.value
        }
    
@dataclass
class FloatLiteral(Literal):
    value: float
    
    def dict(self):
        return {
            "type": "FloatLiteral",
            "value": self.value
        }
    
@dataclass
class BoolLiteral(Literal):
    value: bool
    
    def dict(self):
        return {
            "type": "FloatLiteral",
            "value": self.value
        }
    
@dataclass
class UnaryExpression(Expression):
    operator: str
    expression: Expression
    def eval(self, runtime: Runtime):
        if self.operator == "-":
            return -self.expression.eval(runtime)
        if self.operator == "!":
            return not self.expression.eval(runtime)
        return self.expression.eval(runtime)
    
    def dict(self):
        return {
            "type": "UnaryExpression",
            "operator": self.operator,
            "argument": self.expression.dict()
        }

@dataclass
class Program(Statement):
    body: list[Statement]

    def exec(self, runtime: Runtime):
        index = 0 
        while index < len(self.body):
            statement = self.body[index]
            result = statement.exec(runtime)
            if isinstance(result, ReturnValue):
                return result
            index += 1
            
    def dict(self):
        return {
            "type": self.type(),
            "body": [statement.dict() for statement in self.body]
        }
    
@dataclass
class Identifier(Expression):
    name: str
    def eval(self,runtime: Runtime):
        return runtime.deep_get_value(self.name)
    
    def dict(self):
        return {
            "type": self.type(),
            "name": self.name
        }
    
@dataclass
class Block(Statement):
    body: list[Statement]
    def exec(self, runtime: Runtime):
        index = 0
        while index < len(self.body):
            statement = self.body[index]
            result = statement.exec(runtime)
            if isinstance(result, ReturnValue):
                return result
            if isinstance(result, BreakStatement):
                return result
            index += 1
            
    def dict(self):
        return {
            "type": "Block",
            "body": [statement.dict() for statement in self.body]
        }
    
@dataclass
class WhileStatement(Statement):
    test: Expression
    body: Block

    def exec(self, runtime: Runtime):
        while self.test.eval(runtime):
            while_runtime = Runtime(parent=runtime,name="while")
            result = self.body.exec(while_runtime)
            if isinstance(result, ReturnValue):
                return result
            if isinstance(result, BreakStatement):
                return result

    def dict(self):
        return {
            "type": "WhileStatement",
            "test": self.test.dict(),
            "body": self.body.dict()
        }
    
@dataclass
class BreakStatement(Statement):

    def exec(self, _: Runtime):
        return self

    def dict(self):
        return {
            "type": "BreakStatement"
        }

@dataclass
class ReturnStatement(Statement):
    value: Expression

    def exec(self, runtime: Runtime):
        return ReturnValue(self.value.eval(runtime))

    def dict(self):
        return {
            "type": "ReturnStatement",
            "value": self.value.dict()
        }

@dataclass
class IfStatement(Statement):
    test: Expression
    consequent: Block
    alternate: Block

    def exec(self, runtime: Runtime):
        if_runtime = Runtime(parent=runtime)
        if self.test.eval(runtime):
            return self.consequent.exec(if_runtime)
        else:
            return self.alternate.exec(if_runtime)
        
    def dict(self):
        return {
            "type": "IfStatement",
            "test": self.test.dict(),
            "consequent": self.consequent.dict(),
            "alternate": self.alternate.dict()
        }

@dataclass
class VariableDeclaration(Statement):
    id: Identifier
    value: Expression
    value_type: str = "any"
    def exec(self, runtime: Runtime):
        runtime.declare(self.id.name, self.value.eval(runtime))

    def dict(self):
        return {
            "type": "VariableDeclaration",
            "id": self.id.dict(),
            "value": self.value.dict()
        }

@dataclass
class Assignment(Statement):
    id: Identifier
    value: Expression

    def exec(self, runtime: Runtime):
        runtime.assign(self.id.name, self.value.eval(runtime))

    def dict(self):
        return {
            "type": "Assignment",
            "id": self.id.dict(),
            "value": self.value.dict()
        }
    
@dataclass
class Argument(Expression):
    id: Identifier
    value: Expression

    def dict(self):
        return {
            "type": "Argument",
            "id": self.id.dict(),
            "value": self.value.dict()
        }

@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

    def eval(self, runtime: Runtime):
        left = self.left.eval(runtime)
        right = self.right.eval(runtime)
        if self.operator == "+":
            return left + right
        if self.operator == "-":
            return left - right
        if self.operator == "*":
            return left * right
        if self.operator == "/":
            return left / right
        if self.operator == "%":
            return left % right
        if self.operator == "<":
            return left < right
        if self.operator == ">":
            return left > right
        if self.operator == "<=":
            return left <= right
        if self.operator == ">=":
            return left >= right
        if self.operator == "==":
            return left == right
        if self.operator == "!=":
            return left != right
        if self.operator == "&&":
            return left and right
        if self.operator == "||":
            return left or right
        return None
    
    def dict(self):
        return {
            "type": "BinaryExpression",
            "left": self.left.dict(),
            "operator": self.operator,
            "right": self.right.dict()
        }
    
@dataclass
class CallExpression(Expression):
    callee: Identifier
    arguments: list[Expression]
    def exec(self, runtime: Runtime, args: list=None):
        if args == None:
            args = []
            for index, argument in enumerate(self.arguments):
                args.append(argument.eval(runtime))
        if runtime.has_value(self.callee.name):
            fun:FunEnv = runtime.get_value(self.callee.name)
            return fun.exec(args)
        if runtime.parent is not None:
            return self.exec(runtime.parent,args)
        if self.callee.name in runtime.exteral_fun:
            return runtime.exteral_fun[self.callee.name](*args)
        

    def eval(self, runtime):
        result = self.exec(runtime)
        if result is not None:
            return result.value
    
    def dict(self):
        return {
            "type": "CallExpression",
            "callee": self.callee.dict(),
            "arguments": [argument.dict() for argument in self.arguments]
        }

@dataclass
class Fun(Statement):
    params: list[Identifier]
    body: Block

    def exec(self, runtime: Runtime):
        return self.body.exec(runtime)

    def eval(self, runtime: Runtime):
        return FunEnv(runtime, self)

    def dict(self):
        return {
            "type": "Fun",
            "params": [param.dict() for param in self.params],
            "body": self.body.dict()
        }
    
class EmptyStatement(Statement):

    def exec(self, _: Runtime):
        return None
    
    def eval(self, _: Runtime):
        return None

    def dict(self):
        return {
            "type": "EmptyStatement"
        }
    

class FunEnv():

    def __init__(self, parent: Runtime, body: Fun):
        self.parent = parent
        self.body = body
    
    def exec(self, args: list):
        fun_runtime = Runtime(parent=self.parent)
        for index, param in enumerate(self.body.params):
            fun_runtime.declare(param.name, args[index])
        return self.body.exec(fun_runtime)