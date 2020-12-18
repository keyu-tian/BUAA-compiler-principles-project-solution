from collections import namedtuple, OrderedDict
from enum import Enum, auto

from lexical.chr import is_alpha


class TokenType(Enum):
    EOF_TOKEN = auto()
    
    FN_KW = auto()
    LET_KW = auto()
    CONST_KW = auto()
    AS_KW = auto()
    WHILE_KW = auto()
    IF_KW = auto()
    ELSE_KW = auto()
    RETURN_KW = auto()
    BREAK_KW = auto()
    CONTINUE_KW = auto()
    
    UINT_LITERAL = auto()
    DBL_LITERAL = auto()
    STR_LITERAL = auto()
    
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    L_PAREN = auto()
    R_PAREN = auto()
    L_BRACE = auto()
    R_BRACE = auto()
    ARROW = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    
    GETINT = auto()
    GETDBL = auto()
    GETCHR = auto()
    PUTINT = auto()
    PUTDBL = auto()
    PUTCHR = auto()
    PUTSTR = auto()
    PUTLN = auto()
    
    VOID_TYPE_SPECIFIER = auto()
    INT_TYPE_SPECIFIER = auto()
    DBL_TYPE_SPECIFIER = auto()
    IDENTIFIER = auto()


Token = namedtuple('Token', ['token_type', 'val'])

__s_to_tk = [
    ('fn', TokenType.FN_KW), ('let', TokenType.LET_KW),
    ('const', TokenType.CONST_KW), ('as', TokenType.AS_KW),
    ('while', TokenType.WHILE_KW), ('if', TokenType.IF_KW),
    ('else', TokenType.ELSE_KW), ('return', TokenType.RETURN_KW),
    ('break', TokenType.BREAK_KW), ('continue', TokenType.CONTINUE_KW),
    
    ('+', TokenType.PLUS),
    ('-', TokenType.MINUS),
    ('*', TokenType.MUL),
    ('/', TokenType.DIV),
    ('=', TokenType.ASSIGN),
    ('==', TokenType.EQ),
    ('!=', TokenType.NEQ),
    ('<', TokenType.LT),
    ('>', TokenType.GT),
    ('<=', TokenType.LE),
    ('>=', TokenType.GE),
    ('(', TokenType.L_PAREN),
    (')', TokenType.R_PAREN),
    ('{', TokenType.L_BRACE),
    ('}', TokenType.R_BRACE),
    ('->', TokenType.ARROW),
    (',', TokenType.COMMA),
    (':', TokenType.COLON),
    (';', TokenType.SEMICOLON),
    
    ('getint', TokenType.GETINT),
    ('getdouble', TokenType.GETDBL),
    ('getchar', TokenType.GETCHR),
    ('putint', TokenType.PUTINT),
    ('putdouble', TokenType.PUTDBL),
    ('putchar', TokenType.PUTCHR),
    ('putstr', TokenType.PUTSTR),
    ('putln', TokenType.PUTLN),
    
    ('void', TokenType.VOID_TYPE_SPECIFIER),
    ('int', TokenType.INT_TYPE_SPECIFIER),
    ('double', TokenType.DBL_TYPE_SPECIFIER),
]

STR_TO_TOKEN_TYPE = OrderedDict(sorted(__s_to_tk, key=lambda tup: len(tup[0])))

SHRINKING_OPERANDS = {(' ' * sum(c in STR_TO_TOKEN_TYPE for c in k)).join(k): k for k in STR_TO_TOKEN_TYPE if not is_alpha(k) and len(k) > 1}

__spreads = [*filter(lambda k: len(k) == 1, STR_TO_TOKEN_TYPE), *SHRINKING_OPERANDS]
SPREADING_OPERANDS = OrderedDict((k, f' {k} ') for k in __spreads)

STR_LITERAL_REFERENCE = chr(352)
DBL_LITERAL_REFERENCE = chr(270)
