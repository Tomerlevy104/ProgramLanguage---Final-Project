# User Guide for Running the Custom Language Interpreter

## 1. Prerequisites

- Ensure you have Python installed on your system
- All provided Python files (`interpreter.py`, `lexer.py`, `parser.py`, `tokens.py`, and `general.py`) in the same directory

## 2. Running the Interpreter

### Option 1: Running Text Files

1. Create a text file with your code (e.g., `my_program.txt`)
2. Open a terminal or command prompt
3. Navigate to the directory containing the interpreter files
4. Run the following command:
   ```
   python interpreter.py my_program.txt
   ```
5. The interpreter will execute your code and display the results

### Option 2: Interactive Mode

1. Open a terminal or command prompt
2. Navigate to the directory containing the interpreter files
3. Run the following command:
   ```
   python interpreter.py
   ```
4. You will see a prompt: `basic >`
5. Enter your code one line at a time and press Enter
6. To exit the interactive mode, use the appropriate keyboard shortcut (e.g., Ctrl+C on most systems)

## 3. Language Features

- Arithmetic operations: `@+@`, `@-@`, `@*@`, `@/@`, `@%@`
- Comparison operations: `@==@`, `@!=@`, `@<@`, `@<=@`, `@>@`, `@>=@`
- Logical operations: `@&@` (AND), `@|@` (OR), `@NOT@`
- Conditional statements: `@IF@`, `@THEN@`, `@ELSEIF@`, `@ELSE@`, `@END@`
- Loops: `@FOR@`, `@IN@`, `@RANGE@`, `@DO@`, `@END@`
- Function definitions: `@DEF@`, `@IS@`, `@END@`
- Lambda expressions: `@LAMBDA@`, `@:@`
- Boolean values: `@TRUE@`, `@FALSE@`

## 4. Error Handling

The interpreter provides detailed error messages for various types of errors:

- Illegal Character: When an unexpected character is encountered
- Expected Character: When a required character is missing
- Invalid Syntax: When the code structure is incorrect
- Division by Zero: When attempting to divide by zero
- Runtime Error: For errors that occur during code execution

Error messages include the error type, description, and the location (line number) where the error occurred.

## 5. Tips

- Remember to end conditional statements and loops with `@END@`
- Remember to wrap all operators and keywords with @ symbols. For example, use @+@ for addition, @IF@ for conditional statements, and @DEF@ for function definitions. This is a unique feature of the language and is required for the interpreter to recognize these elements correctly. Forgetting to include the @ symbols will result in syntax errors.
- If you encounter an error, carefully read the error message and check the indicated line number to identify and fix the issue
- If you want to see examples of code running in this custom programming language, please visit the `tests` folder in the project directory. There, you'll find various sample programs that demonstrate the language's features and syntax in action. These examples are a great way to understand how different language constructs work in practice.

By following this guide, you should be able to run the interpreter and start writing programs in this custom language.
Enjoy!
