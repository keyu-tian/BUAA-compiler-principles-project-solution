# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

from enum import unique, Enum, auto

from lexical.tokentype import TokenType


@unique
class TypeDeduction(Enum):
    INT = TokenType.INT_TYPE_SPECIFIER
    DOUBLE = TokenType.DBL_TYPE_SPECIFIER
    VOID = TokenType.VOID_TYPE_SPECIFIER
    STRING_OFFSET = TokenType.STR_LITERAL
    BOOL = auto()
    
    def __str__(self):
        return self.name.lower()
    
    @staticmethod
    def from_is_int(is_int: bool):
        return TypeDeduction.INT if is_int else TypeDeduction.DOUBLE
    
    @staticmethod
    def from_token_type(tt: TokenType):
        return {
            TokenType.INT_TYPE_SPECIFIER: TypeDeduction.INT,
            TokenType.DBL_TYPE_SPECIFIER: TypeDeduction.DOUBLE,
            TokenType.VOID_TYPE_SPECIFIER: TypeDeduction.VOID,
            
            TokenType.UINT_LITERAL: TypeDeduction.INT,
            TokenType.DBL_LITERAL: TypeDeduction.DOUBLE,
            TokenType.STR_LITERAL: TypeDeduction.STRING_OFFSET,
        }[tt]
    
    def to_token_type(self):
        return self.value
    
    def evaluable(self):
        return self in {TypeDeduction.INT, TypeDeduction.DOUBLE, TypeDeduction.BOOL}
