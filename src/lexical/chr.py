import re

str_literal_reg = re.compile(r'\"([^\"\\]|\\[\\\"\'nrt])*\"')
dbl_literal_reg = re.compile(r'\d+\.\d+[eE][+-]?\d+|\d+\.\d+')
chr_literal_reg = re.compile(r'\'([^\"\\]|\\[\\\"\'nrt])\'')


def is_alpha(s: str) -> bool:
    return all(ord('a') <= ord(ch) <= ord('z') or ord('A') <= ord(ch) <= ord('Z') for ch in s)


def is_al_udl(s: str) -> bool:
    return all(ord('a') <= ord(ch) <= ord('z') or ord('A') <= ord(ch) <= ord('Z') or ch == '_' for ch in s)


def is_decimal(s: str) -> bool:
    return all(ord('0') <= ord(ch) <= ord('9') for ch in s)


def is_al_num_udl(s: str) -> bool:
    return all(
        ord('a') <= ord(ch) <= ord('z')
        or ord('A') <= ord(ch) <= ord('Z')
        or ord('0') <= ord(ch) <= ord('9')
        or ch == '_'
        for ch in s
    )


def is_identifier(s: str) -> bool:
    return is_al_udl(s[:1]) and is_al_num_udl(s[1:])
