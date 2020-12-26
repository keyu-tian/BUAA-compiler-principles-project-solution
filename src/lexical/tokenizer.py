# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import logging
from pprint import pformat
from typing import List, Optional, Tuple

from lexical.lex_err import UnknownTokenErr
from lexical.str_utils import is_identifier, is_decimal, remove_inline_comment, extract_str_dbl_chr_literals, STR_LITERAL_REFERENCE, DBL_LITERAL_REFERENCE
from lexical.tokentype import Token, TokenType, STR_TO_TOKEN_TYPE, SPREADING_OPERANDS, SHRINKING_OPERANDS


class LexicalTokenizer(object):
    r"""
    Performs lexical analysis for a given text.
    
    Methods:
    
        parse_tokens_from_raw_input:
            Parses all tokens from the separated words
        
        _pre_process:
            Performs pre-processing for the later lexical analysis, including:
        
            * Comments removing.
            * Literals extracting.
            * Words splitting.
    
        _extract_str_dbl_chr_literals:
            Extracts string, double and character literals, converting them to references or integer values.
    
    Examples:
    
        >>> lex = LexicalTokenizer(lg=None, raw_input=raw_input)
        >>> raw_input = 'fn main() -> void {\n    let x: int = 2;\n    putint(x);\n}\n'
        >>> tokens = lex.parse_tokens()
        >>> from pprint import pprint as pp
        >>> pp(tokens)
    
    """
    
    def __init__(self, lg: logging.Logger, raw_input: str):
        self.lg, self.raw_input = lg, raw_input
    
    def parse_tokens(self) -> Tuple[List[Token], List[str]]:
        words, str_literals, dbl_literals = self._pre_process(self.raw_input)
        tokens = []
        for w in words:
            token_type = STR_TO_TOKEN_TYPE.get(w, None)
            if token_type is not None:              # parse any key word or symbol
                tokens.append(Token(token_type=token_type, val=w))
            elif is_identifier(w):                  # parse an identifier
                tokens.append(Token(token_type=TokenType.IDENTIFIER, val=w))
            elif is_decimal(w):                     # parse a literal of `unsigned integer'
                tokens.append(Token(token_type=TokenType.UINT_LITERAL, val=int(w)))
            elif w[0] == STR_LITERAL_REFERENCE:     # parse a literal of `string'
                tokens.append(Token(token_type=TokenType.STR_LITERAL, val=int(w[1:])))
            elif w[0] == DBL_LITERAL_REFERENCE:     # parse a literal of `double'
                tokens.append(Token(token_type=TokenType.DBL_LITERAL, val=dbl_literals[int(w[1:])]))
            else:                                   # parsing failed
                raise UnknownTokenErr(f'"{w}"')
        tokens.append(Token(token_type=TokenType.EOF_TOKEN, val='EOF sentry'))
        tokens.append(Token(token_type=TokenType.EOF_TOKEN, val='EOF sentry for meta peek'))
        self.lg.info(
            f'\nstring literals:\n {pformat({f"{STR_LITERAL_REFERENCE}{i}": s for i, s in enumerate(str_literals)})}'
            f'\nparsed tokens:\n {pformat(tokens)}\n'
        )
        return tokens, str_literals
    
    def _pre_process(self, raw_input):
        lines = map(remove_inline_comment, filter(len, raw_input.splitlines()))
        codes, str_literals, dbl_literals = extract_str_dbl_chr_literals('\n'.join(lines))
        
        for k, v in [*SPREADING_OPERANDS.items(), *SHRINKING_OPERANDS.items()]:
            codes = codes.replace(k, v)
        
        self.lg.info(f'\ncodes after pre-processing:\n{codes}@EOF\n')
        return codes.split(), str_literals, dbl_literals
