# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import argparse
import logging
import os
import traceback

from lexical.lex_err import TokenCompilationError
from lexical.tokenizer import LexicalTokenizer
from syntactic.analyzer import SyntacticAnalyzer
from syntactic.syn_err import SyntacticCompilationError
from utils.log import C0Logger, create_logger
from utils.misc import r_open, time_str


def main():
    parser = argparse.ArgumentParser(description='pure-python implementation of C0 by Keyu Tian')
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('-o', type=str, required=False, default=None)
    parser.add_argument('--verbose', action='store_true', default=False)
    
    args: argparse.Namespace = parser.parse_args()
    logger = create_logger('c0-lg', os.path.join('..', 'log', f'{time_str(True)}.log')) if args.verbose else None
    # noinspection PyTypeChecker
    lg: logging.Logger = C0Logger(logger) # just for the code completion
    
    with r_open(args.i) as fin:
        raw_input = fin.read()
        try:
            tokens, str_literals = LexicalTokenizer(lg=lg, raw_input=raw_input).parse_tokens()
            str_literals, global_instr, global_vars, global_funcs = SyntacticAnalyzer(lg=lg, tokens=tokens, str_literals=str_literals).analyze_tokens()
            print(str_literals)
            print(global_instr)
            print(global_vars)
            print(global_funcs)
        except TokenCompilationError or SyntacticCompilationError:
            traceback.print_exc()
            exit(-1)


if __name__ == '__main__':
    main()
