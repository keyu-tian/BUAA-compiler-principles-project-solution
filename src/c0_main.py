import argparse
import logging
import os
import traceback

from lexical.lex_err import TokenCompilationError
from lexical.tokenizer import LexicalTokenizer
from utils.log import C0Logger, create_logger
from utils.misc import r_open, time_str


def main():
    parser = argparse.ArgumentParser(description='pure-python implementation of C0 by Keyu Tian')
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('-o', type=str, required=False, default=None)
    parser.add_argument('--verbose', action='store_true', default=False)
    
    args: argparse.Namespace = parser.parse_args()
    logger = create_logger('c0-lg', os.path.join('..', 'log', f'c0 {time_str(True)}.txt')) if args.verbose else None
    # noinspection PyTypeChecker
    lg: logging.Logger = C0Logger(logger) # just for the code completion
    
    with r_open(args.i) as fin:
        raw_inputs = fin.readlines()
        SyntacticCompilationError = TokenCompilationError
        
        try:
            tokens = LexicalTokenizer(lg=lg, raw_inputs=raw_inputs).parse_tokens()
            # instructions = SyntacticAnalyzer(tokens=tokens).generate_instructions()
        except TokenCompilationError or SyntacticCompilationError:
            traceback.print_exc()
            exit(-1)


if __name__ == '__main__':
    main()
