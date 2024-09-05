##############################################
# TOKENS
##############################################

T_INT = 'T_INT'
T_BOOLEAN = 'T_BOOLEAN'
T_IDENTIFIER = 'T_IDENTIFIER'
T_PLUS = 'T_PLUS'
T_SUB = 'T_SUB'
T_MUL = 'T_MUL'
T_DIV = 'T_DIV'
T_MODULO = 'T_MODULO'
T_AND = 'T_AND'
T_OR = 'T_OR'
T_NOT = 'T_NOT'
T_EQEQ = 'T_EQEQ'
T_NEQ = 'T_NEQ'
T_GREATERTHAN = 'T_GREATERTHAN'
T_LESSTHAN = 'T_LESSTHAN'
T_EQGREATERTHAN = 'T_EQGREATERTHAN'
T_EQLESSTHAN = 'T_EQLESSTHAN'
T_LPAREN = 'T_LPAREN'
T_RPAREN = 'T_RPAREN'
T_IF = 'T_IF'
T_IS = 'T_IS'
T_THEN = 'T_THEN'
T_ELSE = 'T_ELSE'
T_ELSEIF = 'T_ELSEIF'
T_FOR = 'T_FOR'
T_IN = 'T_IN'
T_RANGE = 'T_RANGE'
T_END = 'T_END'
T_STEP = 'T_STEP'
T_DO = 'T_DO'
T_DEF = 'T_DEF'
T_COLON = 'T_COLON'
T_COMMA = 'T_COMMA'
T_LAMBDA = 'T_LAMBDA'


##############################################
# MY TOKEN
##############################################
class my_Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
        else:
            self.pos_start = None

        if pos_end:
            self.pos_end = pos_end.copy()
        else:
            self.pos_end = None

        if pos_start:
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

    def matches(self, type_, value=None):
        return self.type == type_ and (self.value == value or value is None)

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


