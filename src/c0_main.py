import argparse
import traceback

from lexical.err import TokenCompilationError
from lexical.tokenizer import LexicalTokenizer
from utils.io import r_open


def main():
    parser = argparse.ArgumentParser(description='pure-python implementation of C0 by Keyu Tian')
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('-o', type=str, required=False, default=None)
    parser.add_argument('--dbg', action='store_true', default=False)
    
    args: argparse.Namespace = parser.parse_args()
    
    with r_open(args.i) as fin:
        raw_inputs = fin.readlines()
        SyntacticCompilationError = TokenCompilationError
        
        try:
            tokens = LexicalTokenizer(raw_inputs=raw_inputs).parse_tokens()
            # instructions = SyntacticAnalyzer(tokens=tokens).generate_instructions()
        except TokenCompilationError or SyntacticCompilationError:
            traceback.print_exc()


if __name__ == '__main__':
    main()
