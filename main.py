
from runtime.interpreter import program_parser
from runtime.runtime import Runtime
from runtime.tokenizer import Tokenizer
import json

script = """
let rec = (c) => {
    print(c);
    if c == 0 {
        return "c + 1";
    }
    rec(c-1);
}

let main = () => {
    print("hello 嘉妮");
    print(rec(10));
}

main();
"""

if __name__ == "__main__":
    t = Tokenizer()
    t.init(script)
    runtime = Runtime(exteral_fun={"print": print})
    ast = program_parser(t)
    result = ast.exec(runtime)