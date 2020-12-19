# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

from collections import OrderedDict
from enum import Enum, unique, auto
from typing import NamedTuple, Union

from lexical.str_utils import is_alpha


@unique
class TokenType(Enum):
    EOF_TOKEN = auto()
    
    FN_KW = 'fn'
    LET_KW = 'let'
    CONST_KW = 'const'
    AS_KW = 'as'
    WHILE_KW = 'while'
    IF_KW = 'if'
    ELSE_KW = 'else'
    RETURN_KW = 'return'
    BREAK_KW = 'break'
    CONTINUE_KW = 'continue'
    
    UINT_LITERAL = auto()
    DBL_LITERAL = auto()
    STR_LITERAL = auto()
    
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    ASSIGN = '='
    EQ = '=='
    NEQ = '!='
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    L_PAREN = '('
    R_PAREN = ')'
    L_BRACE = '{'
    R_BRACE = '}'
    ARROW = '->'
    COMMA = ','
    COLON = ':'
    SEMICOLON = ';'
    
    GETINT = 'getint'
    GETDBL = 'getdouble'
    GETCHR = 'getchar'
    PUTINT = 'putint'
    PUTDBL = 'putdouble'
    PUTCHR = 'putchar'
    PUTSTR = 'putstr'
    PUTLN = 'putln'
    
    VOID_TYPE_SPECIFIER = 'void'
    INT_TYPE_SPECIFIER = 'int'
    DBL_TYPE_SPECIFIER = 'double'
    IDENTIFIER = auto()
    

class Token(NamedTuple):
    token_type: TokenType
    val: Union[str, int, float, None]

    # @property
    # def is_type(self):
    #     return self.val in {
    #         TokenType.VOID_TYPE_SPECIFIER,
    #         TokenType.INT_TYPE_SPECIFIER,
    #         TokenType.DBL_TYPE_SPECIFIER
    #     }
    
    # @property
    # def is_builtin_func(self):
    #     return self.val in {
    #         TokenType.GETCHR, TokenType.GETINT, TokenType.GETDBL,
    #         TokenType.PUTCHR, TokenType.PUTINT, TokenType.PUTDBL, TokenType.PUTSTR, TokenType.PUTLN
    #     }


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
    
    # ('getint', TokenType.GETINT),
    # ('getdouble', TokenType.GETDBL),
    # ('getchar', TokenType.GETCHR),
    # ('putint', TokenType.PUTINT),
    # ('putdouble', TokenType.PUTDBL),
    # ('putchar', TokenType.PUTCHR),
    # ('putstr', TokenType.PUTSTR),
    # ('putln', TokenType.PUTLN),
    
    ('void', TokenType.VOID_TYPE_SPECIFIER),
    ('int', TokenType.INT_TYPE_SPECIFIER),
    ('double', TokenType.DBL_TYPE_SPECIFIER),
]

STR_TO_TOKEN_TYPE = OrderedDict(sorted(__s_to_tk, key=lambda pair: len(pair[0])))

SHRINKING_OPERANDS = {(' ' * sum(c in STR_TO_TOKEN_TYPE for c in k)).join(k): k for k in STR_TO_TOKEN_TYPE if not is_alpha(k) and len(k) > 1}

__spreads = [*filter(lambda k: len(k) == 1, STR_TO_TOKEN_TYPE), *SHRINKING_OPERANDS]
SPREADING_OPERANDS = OrderedDict((k, f' {k} ') for k in __spreads)
