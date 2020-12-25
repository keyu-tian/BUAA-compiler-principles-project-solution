# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import argparse
import logging
import os
import traceback
from pprint import pformat as pf

import time
import sys

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
            st_t = time.time()
            s = SyntacticAnalyzer(lg=lg, tokens=tokens, str_literals=str_literals)
            str_literals, global_instr, global_vars, global_funcs = s.analyze_tokens()
            dt = (time.time() - st_t) * 1000
            lg.info(f'str_literals = \n {pf(str_literals)}')
            lg.info(f'global_instr = \n {pf(global_instr)}')
            lg.info(f'global_vars = \n {pf(global_vars)}')
            lg.info(f'global_funcs = \n {pf(global_funcs)}')
            lg.info(f'time cost: {dt:.2f}ms')
        except (TokenCompilationError, SyntacticCompilationError):
            traceback.print_exc()
            print(f'cur = {" ".join([str(t.val) for t in s._tokens[s._tk_top:s._tk_top+10]])} ...')
            exit(-1)


if __name__ == '__main__':
    # sys.argv[2] = '../tests/1-comment/ac1.input.txt'
    main()
