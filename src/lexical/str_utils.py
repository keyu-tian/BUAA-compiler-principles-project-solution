# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import re

from lexical.lex_err import QuoteMismatchErr
from meta import FS_ENCODING


def is_alpha(s: str) -> bool:
    return all(ord('a') <= ord(ch) <= ord('z') or ord('A') <= ord(ch) <= ord('Z') for ch in s)


def is_al_udl(s: str) -> bool:
    return all(ord('a') <= ord(ch) <= ord('z') or ord('A') <= ord(ch) <= ord('Z') or ch == '_' for ch in s)


def is_decimal(s: str) -> bool:
    return all(ord('0') <= ord(ch) <= ord('9') for ch in s)


def is_al_num_udl(s: str) -> bool:
    return all(
        ord('a') <= ord(ch) <= ord('z') or ord('A') <= ord(ch) <= ord('Z')
        or ord('0') <= ord(ch) <= ord('9') or ch == '_'
        for ch in s
    )


def is_identifier(s: str) -> bool:
    return is_al_udl(s[:1]) and is_al_num_udl(s[1:])


def remove_inline_comment(line: str) -> str:
    tag = chr(500) * 2
    ln = re.sub(r'\\\"', tag, line)
    for p in map(lambda m: m.start(), re.finditer('//', ln)):
        lefts = ln[:p]
        if lefts.count('"') % 2 == 0:
            ln = lefts
            break
    if ln.count('"') % 2 == 1:
        raise QuoteMismatchErr('quote missing')
    ln = ln.replace(tag, r'\"')
    return ln


str_literal_reg = re.compile(r'\"([^\"\\]|\\[\\\"\'nrt])*\"')
dbl_literal_reg = re.compile(r'\d+\.\d+[eE][+-]?\d+|\d+\.\d+')
chr_literal_reg = re.compile(r'\'([^\"\\]|\\[\\\"\'nrt])\'')

STR_LITERAL_REFERENCE, DBL_LITERAL_REFERENCE = chr(352), chr(270)


def escaping(s: str):
    return s.encode(FS_ENCODING).decode('unicode_escape')


def extract_str_dbl_chr_literals(codes):
    str_literals, dbl_literals = [], []
    _ex_str = lambda m: f"{STR_LITERAL_REFERENCE}{len(str_literals)}" \
                        f"{str_literals.append(escaping(m.group()[1:-1])) or ''}"
    _ex_dbl = lambda m: f"{DBL_LITERAL_REFERENCE}{len(dbl_literals)}" \
                        f"{dbl_literals.append(eval(m.group())) or ''}"
    _ex_chr = lambda m: str(ord(escaping(m.group()[1:-1])))
    
    codes = str_literal_reg.sub(_ex_str, codes)
    codes = dbl_literal_reg.sub(_ex_dbl, codes)
    codes = chr_literal_reg.sub(_ex_chr, codes)
    return codes, str_literals, dbl_literals
