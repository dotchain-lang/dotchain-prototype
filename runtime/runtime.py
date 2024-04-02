from ast import Expression

from attr import dataclass

class Runtime():
    
    def __init__(self, context=None, parent=None, exteral_fun=None, name=None) -> None:
        self.name = name
        self.parent = parent
        self.context = context if context is not None else dict()
        self.exteral_fun = exteral_fun if exteral_fun is not None else dict()

    def has_value(self, identifier: str) -> bool:
        return identifier in self.context
    
    def get_value(self, identifier: str):
        return self.context.get(identifier)
    
    def deep_get_value(self, id: str):
        if self.has_value(id):
            return self.get_value(id)
        if self.parent is not None:
            return self.parent.deep_get_value(id)
        return None
    
    def set_value(self, identifier: str, value):
        self.context[identifier] = value
    
    def declare(self, identifier: str, value):
        if self.has_value(identifier):
            raise Exception(f"Variable {identifier} is already declared")
        self.set_value(identifier, value)
    
    def assign(self, identifier: str, value):
        if self.has_value(identifier):
            self.set_value(identifier, value)
        elif self.parent is not None:
            self.parent.assign(identifier, value)
        else:
            raise Exception(f"Variable {identifier} is not declared")
        
    def show_values(self):
        print(self.context)

