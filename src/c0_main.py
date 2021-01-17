# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import argparse
import logging
import os
import sys
import time
import traceback
from pprint import pformat as pf

from lexical.lex_err import TokenCompilationError
from lexical.tokenizer import LexicalTokenizer
from meta import LOCAL
from obj.assembler import Assembler
from syntactic.analyzer import SyntacticAnalyzer
from syntactic.syn_err import SyntacticCompilationError
from utils.log import C0Logger, create_logger
from utils.misc import r_open, time_str, wb_open, w_open


def main():
    parser = argparse.ArgumentParser(description='pure-python implementation of C0 by Keyu Tian')
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('-o', type=str, required=False, default=None)
    parser.add_argument('--verbose', action='store_true', default=False)
    
    args: argparse.Namespace = parser.parse_args()
    logger = create_logger('c0-lg', os.path.join('..', 'log', f'{time_str(True)}.log')) if args.verbose else None
    # noinspection PyTypeChecker
    lg: logging.Logger = C0Logger(logger) # just for the code completion
    
    with r_open(args.i) as fin, wb_open(args.o) as fout:
        obj_hint_fp = w_open(args.o + '.txt') if LOCAL else sys.stdout
        raw_input = fin.read()
        try:
            tokens, str_literals = LexicalTokenizer(lg=lg, raw_input=raw_input).parse_tokens()
            st_t = time.time()
            s = SyntacticAnalyzer(lg=lg, tokens=tokens, str_literals=str_literals)
            str_literals, global_symbols, global_funcs = s.analyze_tokens()
            b_arr = Assembler(lg, str_literals, global_symbols, global_funcs).dump()
            fout.write(b_arr)
            print('\n'.join(b_arr.hints), file=obj_hint_fp)
            if LOCAL:
                obj_hint_fp.close()
            
            dt = (time.time() - st_t) * 1000
            lg.info(f'str_literals = ({len(str_literals)}) \n {pf(str_literals)}')
            lg.info(f'global_symbols = ({len(global_symbols)}) \n {pf(global_symbols)}')
            lg.info(f'global_funcs = ({len(global_funcs)}) \n {pf(global_funcs)}')
            lg.info(f'time cost: {dt:.2f}ms')
        except (TokenCompilationError, SyntacticCompilationError):
            traceback.print_exc()
            print(f'@ {" ".join([str(t.val) for t in s._tokens[s._tk_top:s._tk_top+20]])} ...')
            exit(-1)


if __name__ == '__main__':
    if LOCAL:
        k = '0-basic/ac2-1-christmas-tree'
        sys.argv[2] = f'../tests/{k}.input.txt'
    main()
