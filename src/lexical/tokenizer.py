from typing import List


from lexical.chr import is_identifier, str_literal_reg, dbl_literal_reg, chr_literal_reg, is_decimal
from lexical.err import UnknownTokenErr
from lexical.tokentype import Token, TokenType, STR_TO_TOKEN_TYPE, STR_LITERAL_REFERENCE, DBL_LITERAL_REFERENCE, SPREADING_OPERANDS, SHRINKING_OPERANDS
from meta import F_ENCODING


class LexicalTokenizer(object):
    r"""
    Performs lexical analysis for a given text.
    
    Methods:
    
        __init__:
            Construct the tokenizer and performs pre-preparation
            for the later lexical analysis, including:
        
            * Comments removing.
            * Literals extracting.
            * Words splitting.
        
        parse_tokens:
            Parse all tokens from the separated words.
    
    Examples:
    
        >>> lex = LexicalTokenizer('fn main() -> void {\n    let x: int = 2;\n    putint(x);\n}\n'.splitlines())
        >>> tokens = lex.parse_tokens()
        >>> from pprint import pprint as pp
        >>> pp(tokens)
    
    """
    
    def __init__(self, raw_inputs: List[str]):
        lines = map(lambda s: s.split('//')[0].strip(), raw_inputs)
        codes = '\n'.join(filter(len, lines))
        
        self.str_literals, self.dbl_literals = [], []
        codes = self.__extract_str_dbl_chr_literals(codes)
        
        for k, v in [*SPREADING_OPERANDS.items(), *SHRINKING_OPERANDS.items()]:
            codes = codes.replace(k, v)
        self.words = codes.split()
    
    def __extract_str_dbl_chr_literals(self, codes):
        _ex_str = lambda m: f"{STR_LITERAL_REFERENCE}{len(self.str_literals)}" \
                            f"{self.str_literals.append(m.group()[1:-1].encode(F_ENCODING).decode('unicode_escape')) or ''}"
        _ex_dbl = lambda m: f"{DBL_LITERAL_REFERENCE}{len(self.dbl_literals)}" \
                            f"{self.dbl_literals.append(eval(m.group())) or ''}"
        _ex_chr = lambda m: str(ord(m.group()[1:-1].encode(F_ENCODING).decode('unicode_escape')))
        codes = dbl_literal_reg.sub(_ex_dbl, str_literal_reg.sub(_ex_str, codes))
        return chr_literal_reg.sub(_ex_chr, codes)
    
    def parse_tokens(self) -> List[Token]:
        tokens = []
        for w in self.words:
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
                tokens.append(Token(token_type=TokenType.DBL_LITERAL, val=self.dbl_literals[int(w[1:])]))
            else:                                   # parsing failed
                raise UnknownTokenErr(f'"{w}"')
        return tokens


if __name__ == '__main__':
    from pprint import pprint as pp
    
    pp(
        LexicalTokenizer(
            """
fn main()->void{
    let _x_1:int='1'+'\\n'-1.3+1.0e3-1.0E-3-3 as int;
    if x==0{}
    if x!=0{}
    if x>=0{}
    if x>0{}
    if x<=0{}
    if x<0{}
    putstr("aew");
    putstr("a'a'e1.3 1.3E-3w\\n");
    putstr("\\n");
    while x<=0 {break; continue;}
}

""".splitlines()
        ).parse_tokens()
    )
