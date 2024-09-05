from tokens import *
from general import *


##############################################
# NODES
##############################################


class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class BooleanNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node} {self.op_tok} {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}{self.node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases  # (condition, expr)
        self.else_case = else_case
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1][1]).pos_end

    def __repr__(self):
        result = f'@IF@ {self.cases[0][0]} @THEN@ {self.cases[0][1]}'
        for condition, expr in self.cases[1:]:
            result += f' @ELSEIF@ {condition} @THEN@ {expr}'
        if self.else_case:
            result += f' @ELSE@ {self.else_case}'
        result += ' @END@'
        return result


class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        range_repr = f'@RANGE@({self.start_value_node}, {self.end_value_node}'
        if self.step_value_node:
            range_repr += f', {self.step_value_node}'
        range_repr += ')'
        return f'@FOR@ {self.var_name_tok} @IN@ {range_repr} @DO@ {self.body_node} @END@'


class FunctionDefNode:
    def __init__(self, name_tok, arg_name_toks, body_node):
        self.name_tok = name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.pos_start = self.name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'@DEF@ {self.name_tok}({", ".join(str(arg) for arg in self.arg_name_toks)}) @IS@ {self.body_node} @END@'


class FunctionCallNode:
    def __init__(self, name_tok, arg_nodes):
        self.name_tok = name_tok
        self.arg_nodes = arg_nodes
        self.pos_start = self.name_tok.pos_start
        self.pos_end = (self.arg_nodes[-1].pos_end if self.arg_nodes else self.name_tok.pos_end)

    def __repr__(self):
        return f'{self.name_tok}({", ".join(str(arg) for arg in self.arg_nodes)})'


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'[{", ".join(str(element) for element in self.element_nodes)}]'


class IdentifierNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class LambdaNode:
    def __init__(self, arg_name_toks, body_node):
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.pos_start = self.arg_name_toks[0].pos_start if self.arg_name_toks else self.body_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f'@LAMBDA@({", ".join(str(arg) for arg in self.arg_name_toks)}) @:@ {self.body_node}'

    def apply(self, args, interpreter):
        if len(args) != len(self.arg_name_toks):
            raise ValueError(f"Expected {len(self.arg_name_toks)} arguments, got {len(args)}")

        # Create a new symbol table for the lambda execution
        new_symbol_table = interpreter.global_symbol_table.copy()

        # Bind arguments to parameter names
        for i, arg_name in enumerate(self.arg_name_toks):
            new_symbol_table[arg_name.value] = args[i]

        # Execute the body with the new symbol table
        old_symbol_table = interpreter.global_symbol_table
        interpreter.global_symbol_table = new_symbol_table
        result = interpreter.visit(self.body_node)
        interpreter.global_symbol_table = old_symbol_table
        return result


##############################################
# PARSE RESULT
##############################################

# The ParseResult class is used to track the progress and results of parsing operations.
# It handles the management of parsed nodes, error tracking, and token advancement counting.
# This class helps in error recovery and backtracking during the parsing process.
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


##############################################
# PARSER
##############################################

# The Parser class is responsible for analyzing the sequence of tokens produced by the lexer
# and constructing an Abstract Syntax Tree (AST) that represents the structure of the program.
# It implements various parsing methods for different language constructs such as expressions,
# statements, function definitions, and control structures (if, for, etc.).
# The parser uses recursive descent parsing techniques and handles error detection and reporting.

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_idx = -1
        self.current_token = None
        self.advance()

    def advance(self):
        self.token_idx += 1
        self.update_current_token()
        return self.current_token

    def update_current_token(self):
        if self.token_idx >= 0 and self.token_idx < len(self.tokens):
            self.current_token = self.tokens[self.token_idx]
        else:
            self.current_token = None

    def parse(self):
        res = ParseResult()
        if not self.tokens:
            return res.failure(InvalidSyntaxError(
                Position(0, 0, 0, '<unknown>', ''),
                Position(0, 0, 0, '<unknown>', ''),
                "No tokens to parse"
            ))

        if self.current_token.matches(T_DEF):
            return self.func_def()

        expr = res.register(self.expr())
        if res.error: return res
        if self.current_token is not None:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', 'AND' or 'OR'"
            ))
        return res.success(expr)

    def expr(self):
        res = ParseResult()

        if self.current_token.type == T_LAMBDA:
            lambda_node = res.register(self.lambda_expr())
            if res.error: return res
            return res.success(lambda_node)

        return self.expression()

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token != None:
            statement = res.register(self.statement())
            if res.error: return res
            statements.append(statement)

        return res.success(ListNode(
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type == T_DEF:
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        expr = res.register(self.expr())
        if res.error:
            return res.failure(IllegalCharError(
                pos_start, self.current_token.pos_end,
                "Expected 'DEF', 'IF', 'FOR', 'INT', 'IDENTIFIER', '+', '-', '('"
            ))
        return res.success(expr)

    def expression(self):
        res = ParseResult()
        if self.current_token.type == T_IF:
            return self.if_expr()
        elif self.current_token.type == T_FOR:
            return self.for_expr()

        left = res.register(self.comparison())
        if res.error: return res

        while self.current_token != None and self.current_token.type in (T_AND, T_OR):
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            right = res.register(self.comparison())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def comparison(self):
        res = ParseResult()

        left = res.register(self.term())
        if res.error: return res

        while self.current_token != None and self.current_token.type in (
                T_EQEQ, T_NEQ, T_GREATERTHAN, T_LESSTHAN, T_EQGREATERTHAN, T_EQLESSTHAN):
            op_tok = self.current_token
            self.advance()
            right = res.register(self.term())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def term(self):
        res = ParseResult()

        left = res.register(self.factor())
        if res.error: return res

        while self.current_token != None and self.current_token.type in (T_MUL, T_DIV, T_MODULO, T_PLUS, T_SUB):
            op_tok = self.current_token
            res.register_advancement()
            self.advance()

            if self.current_token is None:
                return res.failure(InvalidSyntaxError(
                    op_tok.pos_start, op_tok.pos_end,
                    "Expected expression after operator"
                ))

            right = res.register(self.factor())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def factor(self):
        res = ParseResult()
        tok = self.current_token

        if tok is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end if self.tokens else Position(0, 0, 0, '<unknown>', ''),
                self.tokens[-1].pos_end if self.tokens else Position(0, 0, 0, '<unknown>', ''),
                "Unexpected end of input"
            ))

        if tok.type in (T_PLUS, T_SUB, T_NOT):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.primary()

    def primary(self):
        res = ParseResult()
        tok = self.current_token

        if tok is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end if self.tokens else Position(0, 0, 0, '<unknown>', ''),
                self.tokens[-1].pos_end if self.tokens else Position(0, 0, 0, '<unknown>', ''),
                "Unexpected end of input"
            ))

        if tok.type in (T_INT, T_BOOLEAN):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok) if tok.type == T_INT else BooleanNode(tok))

        elif tok.type == T_IDENTIFIER:
            res.register_advancement()
            self.advance()
            if self.current_token and self.current_token.type == T_LPAREN:
                return self.function_call(IdentifierNode(tok))
            return res.success(IdentifierNode(tok))

        elif tok.type == T_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_token is None or self.current_token.type != T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    tok.pos_start, self.current_token.pos_start if self.current_token else self.tokens[-1].pos_end,
                    "Expected ')'"
                ))
            res.register_advancement()
            self.advance()

            # Check if this is an immediate function call
            if self.current_token and self.current_token.type == T_LPAREN:
                return self.function_call(expr)

            return res.success(expr)

        elif tok.type == T_LAMBDA:
            lambda_expr = res.register(self.lambda_expr())
            if res.error:
                return res

            # Check if this is an immediate function call
            if self.current_token and self.current_token.type == T_LPAREN:
                return self.function_call(lambda_expr)

            return res.success(lambda_expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected INT, IDENTIFIER, '+', '-', '(', or 'LAMBDA'"
        ))

    def func_def(self):
        res = ParseResult()

        if not self.current_token.matches(T_DEF):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '@DEF@'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token is None or self.current_token.type != T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start if self.current_token else self.tokens[-1].pos_end,
                self.current_token.pos_end if self.current_token else self.tokens[-1].pos_end,
                f"Expected identifier"
            ))

        func_name = self.current_token
        res.register_advancement()
        self.advance()

        if self.current_token is None or self.current_token.type != T_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start if self.current_token else self.tokens[-1].pos_end,
                self.current_token.pos_end if self.current_token else self.tokens[-1].pos_end,
                f"Expected '('"
            ))

        res.register_advancement()
        self.advance()

        arg_name_toks = []

        # Check for unexpected end of input after opening parenthesis
        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected parameter list or ')'"
            ))

        if self.current_token.type == T_IDENTIFIER:
            arg_name_toks.append(self.current_token)
            res.register_advancement()
            self.advance()

            while self.current_token and self.current_token.type == T_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_token is None:
                    return res.failure(InvalidSyntaxError(
                        self.tokens[-1].pos_end,
                        self.tokens[-1].pos_end,
                        "Unexpected end of input. Expected identifier after ','"
                    ))

                if self.current_token.type != T_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected identifier"
                    ))

                arg_name_toks.append(self.current_token)
                res.register_advancement()
                self.advance()

        if self.current_token is None or self.current_token.type != T_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start if self.current_token else self.tokens[-1].pos_end,
                self.current_token.pos_end if self.current_token else self.tokens[-1].pos_end,
                f"Expected ')'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token is None or not self.current_token.matches(T_IS):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start if self.current_token else self.tokens[-1].pos_end,
                self.current_token.pos_end if self.current_token else self.tokens[-1].pos_end,
                f"Expected '@IS@'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected function body"
            ))

        body = res.register(self.expr())
        if res.error: return res

        if self.current_token is None or not self.current_token.matches(T_END):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start if self.current_token else self.tokens[-1].pos_end,
                self.current_token.pos_end if self.current_token else self.tokens[-1].pos_end,
                f"Expected '@END@'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(FunctionDefNode(func_name, arg_name_toks, body))

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(T_IF):
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'if'"))

        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input after '@IF@'. Expected a condition."
            ))

        condition = res.register(self.expression())
        if res.error: return res

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected '@THEN@' and an expression after the condition."
            ))

        if self.current_token.matches(T_THEN):
            res.register_advancement()
            self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected an expression after '@THEN@'."
            ))

        body = res.register(self.expression())
        if res.error: return res

        cases.append((condition, body))

        while self.current_token != None and self.current_token.matches(T_ELSEIF):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expression())
            if res.error: return res

            if self.current_token.matches(T_THEN):
                res.register_advancement()
                self.advance()

            body = res.register(self.expression())
            if res.error: return res

            cases.append((condition, body))

        if self.current_token != None and self.current_token.matches(T_ELSE):
            res.register_advancement()
            self.advance()
            else_case = res.register(self.expression())
            if res.error: return res

        if self.current_token is None or not self.current_token.matches(T_END):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start if self.current_token else self.tokens[-1].pos_end,
                self.current_token.pos_end if self.current_token else self.tokens[-1].pos_end,
                "Expected '@END@' at the end of IF expression"))

        res.register_advancement()
        self.advance()

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_token.matches(T_FOR):
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected '@FOR@'"))
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input after '@FOR@'. Expected identifier."
            ))

        if self.current_token.type != T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_token
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected '@IN@'."
            ))

        if not self.current_token.matches(T_IN):
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected '@IN@'"))
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected '@RANGE@'."
            ))

        if not self.current_token.matches(T_RANGE):
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected '@RANGE@'"))
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected '('."
            ))

        if not self.current_token.type == T_LPAREN:
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected '('"))
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected an expression."
            ))

        start = res.register(self.expr())
        if res.error: return res

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected ','."
            ))

        if not self.current_token.type == T_COMMA:
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected ','"))
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected an expression."
            ))

        end = res.register(self.expr())
        if res.error: return res

        step = None
        if self.current_token and self.current_token.type == T_COMMA:
            res.register_advancement()
            self.advance()
            if self.current_token is None:
                return res.failure(InvalidSyntaxError(
                    self.tokens[-1].pos_end,
                    self.tokens[-1].pos_end,
                    "Unexpected end of input. Expected an expression for step value."
                ))
            step = res.register(self.expr())
            if res.error: return res

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected ')'."
            ))

        if not self.current_token.type == T_RPAREN:
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected ')'"))
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected '@DO@'."
            ))

        if not self.current_token.matches(T_DO):
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected '@DO@'"))
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected an expression for the loop body."
            ))

        body = res.register(self.expr())
        if res.error: return res

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected '@END@'."
            ))

        if not self.current_token.matches(T_END):
            return res.failure(
                IllegalCharError(self.current_token.pos_start, self.current_token.pos_end, "Expected '@END@'"))
        res.register_advancement()
        self.advance()

        return res.success(ForNode(var_name, start, end, step, body))

    def lambda_expr(self):
        res = ParseResult()

        if not self.current_token.matches(T_LAMBDA):
            return res.failure(IllegalCharError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '@LAMBDA@'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input after '@LAMBDA@'. Expected '('."
            ))

        if self.current_token.type != T_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected '('"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected identifier."
            ))

        if self.current_token.type != T_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected identifier"
            ))

        arg_name_tok = self.current_token
        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected ')'."
            ))

        if self.current_token.type != T_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected ')'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected '@:@'."
            ))

        if not self.current_token.matches(T_COLON):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected '@:@'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token is None:
            return res.failure(InvalidSyntaxError(
                self.tokens[-1].pos_end,
                self.tokens[-1].pos_end,
                "Unexpected end of input. Expected an expression after '@:@'."
            ))

        body = res.register(self.expr())
        if res.error: return res

        return res.success(LambdaNode([arg_name_tok], body))

    def function_call(self, func_name_or_lambda):
        res = ParseResult()
        arg_nodes = []

        if not self.current_token.type == T_LPAREN:
            return res.failure(IllegalCharError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '('"
            ))

        res.register_advancement()
        self.advance()

        if self.current_token.type == T_RPAREN:
            res.register_advancement()
            self.advance()
        else:
            arg_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(IllegalCharError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')', 'IF', 'FOR', 'FUN', INT, IDENTIFIER, '+', '-', '(', or 'lambda'"
                ))

            while self.current_token.type == T_COMMA:
                res.register_advancement()
                self.advance()

                arg_nodes.append(res.register(self.expr()))
                if res.error: return res

            if self.current_token.type != T_RPAREN:
                return res.failure(IllegalCharError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ')'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(FunctionCallNode(func_name_or_lambda, arg_nodes))

    def atom(self):
        res = ParseResult()
        tok = self.current_token

        if tok.type == T_INT:
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == T_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(IdentifierNode(tok))

        elif tok.type == T_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_token.type == T_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == T_LAMBDA:
            lambda_expr = res.register(self.lambda_expr())
            if res.error: return res
            return res.success(lambda_expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, identifier, '+', '-', '(', 'LAMBDA'"
        ))

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_token.type == T_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_token.type == T_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ')', 'LAMBDA', int, identifier, '+', '-', '('"
                    ))

                while self.current_token.type == T_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_token.type != T_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()
            return res.success(FunctionCallNode(atom, arg_nodes))
        return res.success(atom)
