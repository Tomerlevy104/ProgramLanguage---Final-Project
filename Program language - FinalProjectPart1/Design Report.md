# Custom Language Interpreter Project

## 1. Introduction

This program was written by Adir Davidov, Omer Meler, and Tomer Levy. We created the "@" language, a custom programming language with a unique syntax using "@" symbols to wrap operators and keywords. Implemented in Python, and it features arithmetic operations, boolean logic, conditionals, loops, and functions including lambdas. The project includes a lexer, parser, and interpreter, demonstrating fundamental concepts of language design and interpretation. Our @ language supports both interactive mode and file execution, providing a practical tool for learning and application development. 

## 2. Design Decisions

Several key design decisions were made in the development of this language:

1. **Operator and Keyword Syntax**: All operators and keywords are wrapped in `@` symbols (e.g., `@+@`, `@IF@`). This unique syntax clearly distinguishes language constructs from user-defined identifiers and makes parsing more straightforward.

2. **Function Definition**: Functions are defined using the `@DEF@` keyword, with the body enclosed between `@IS@` and `@END@`. This structure provides clear demarcation of function blocks.

3. **Lambda Expressions**: The language supports lambda expressions using the `@LAMBDA@` keyword, with the body following `@:@`. This allows for concise, anonymous function definitions.

4. **Recursion**: The language supports recursive function calls, enabling the implementation of recursive algorithms.

5. **Looping Construct**: A `@FOR@` loop is implemented with a built-in `@RANGE@` function, similar to Python's range function, providing a familiar and versatile looping mechanism.

6. **Error Handling**: Comprehensive error handling is implemented, providing detailed error messages with line numbers to assist in debugging.

7. **Interactive Mode**: The interpreter supports both file execution and an interactive mode, enhancing usability for testing and learning.

## 3. Challenges Faced and Solutions Implemented

1. **Lexical Analysis Complexity**: 
   - Challenge: Implementing a lexer that could handle the unique `@`-wrapped operators and keywords.
   - Solution: A custom lexer was developed with specific methods to identify and tokenize these special constructs.

2. **Parsing Nested Structures**: 
   - Challenge: Parsing nested structures like conditional statements and function definitions.
   - Solution: The parser uses a combination of methods for different language constructs. For example, it uses separate methods like if_expr(), for_expr(), and func_def() to handle different types of nested structures. These methods work together to parse complex, nested language elements.

3. **Function Implementation**: 
   - Challenge: Implementing function definitions and function calls in the language.
   - Solution: Created FunctionDefNode for function definitions and FunctionCallNode for function calls in the parser. In the interpreter, a Function class was implemented to handle the execution of defined functions.

4. **Lambda Functions**: 
   - Challenge: Adding support for anonymous functions (lambda expressions) in the language.
   - Solution: Developed a LambdaNode in the parser to handle the syntax of lambda expressions. The interpreter's Function class was designed to work with both named functions and lambda functions, allowing for their execution in a similar manner.

5. **Error Handling and Reporting**: 
   - Challenge: Providing meaningful error messages with accurate position information.
   - Solution: A robust error handling system was implemented, tracking token positions throughout the lexing and parsing process.

## 4. Conclusion

Our custom language interpreter project is now complete and working well. It covers a range of programming features, from simple to complex. We overcame challenges in showing errors clearly and dealing with tricky parts like nested functions. Users can type commands directly or run whole programs from files. The interpreter understands complex language elements and points out mistakes helpfully. After lots of testing with different examples, we're confident it performs as intended. This project has given us a strong base to build on in the future.