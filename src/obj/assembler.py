# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import logging
from typing import List, Union

from obj.byte_casting import *
from syntactic.symbol.table import VarAttrs, FuncAttrs
from vm.instruction import Instruction


class _VerboseBArr(bytearray):
    def __init__(self, hints: List[str]):
        super(_VerboseBArr, self).__init__()
        self.hints = hints

    def append(self, obj, hint: str) -> None:
        super(_VerboseBArr, self).append(obj)
        self.hints.append(f'{hint:17s}: {obj:02x}')

    def extend(self, byts, hint: str) -> None:
        super(_VerboseBArr, self).extend(byts)
        if hint.endswith('str'):
            s = ' '.join(f' {chr(x)}' for x in byts)
        else:
            s = ' '.join(f'{x:02x}' for x in byts)
        self.hints.append(f'{hint:17s}: {s}')
    
    # def join(self, __iterable_of_bytes, hint: str):
    #     _new = _VerboseBArr(self.hints)
    #     _new.extend(bytes(bytearray().join(__iterable_of_bytes)), hint)
    #     return _new
    

class Assembler(object):
    def __init__(
            self, lg: logging.Logger,
            str_literals: List[str],
            global_symbols: List[Union[VarAttrs, FuncAttrs]],
            global_funcs: List[FuncAttrs],
    ):
        super(Assembler, self).__init__()
        self.lg = lg
        self._hints: List[str] = []
        self._magic_num, self._version = 0x72303b3e, 0x1
        self._str_literals = str_literals
        self._global_symbols, self._global_funcs = global_symbols, global_funcs
        self._barr = _VerboseBArr(self._hints)
        self._barr.extend(u32_to_bytes(self._magic_num), 'magic num')
        self._barr.extend(u32_to_bytes(self._version), 'version')
        self._dumped = False
    
    def dump(self):
        if not self._dumped:
            self._dumped = True
            self._dump_str_literals()
            self._dump_global_symbols()
            self._dump_functions()
        return self._barr
    
    def _dump_str_literals(self):
        for s in self._str_literals:
            self._barr.append(1, ' const')
            self._barr.extend(u32_to_bytes(len(s)), ' len(str ltr)')
            self._barr.extend(str_to_bytes(s), ' str')
    
    def _dump_global_symbols(self):
        """
        .. note::
            count: u32,
            items: global_symbol[],
        """
        self._barr.extend(u32_to_bytes(len(self._global_symbols)), 'num globals')
        [self._dump_a_global_symbol(s) for s in self._global_symbols]
    
    def _dump_a_global_symbol(self, symbol: Union[VarAttrs, FuncAttrs]):
        """
        .. note::
            is_const: u8,
            value:
                count: u32
                items: u8[],
        """
        if symbol.is_func():
            self._barr.append(1, ' const')
            name_b = str_to_bytes(symbol.name)
            self._barr.extend(u32_to_bytes(len(name_b)), ' len(func name)')
            self._barr.extend(name_b, ' func name str')
        else:
            self._barr.append(int(symbol.const), ' const')
            self._barr.extend(u32_to_bytes(8), ' num gvar btyes')
            self._barr.extend(u64_to_bytes(0), ' gvar values')
            
    def _dump_functions(self):
        """
        .. note::
            count: u32,
            items: function[],
        """
        self._barr.extend(u32_to_bytes(len(self._global_funcs)), 'num funcs')
        [self._dump_a_function(f) for f in self._global_funcs]
    
    def _dump_a_function(self, func: FuncAttrs):
        """
        .. note::
            name: u32,
            num_ret_vals: u32,
            num_args: u32,
            num_loc_vars: u32,
            body:
                count: u32,
                items: Instruction[]
        """
        metas = [func.offset, func.num_ret_vals, len(func.arg_types), func.num_local_vars]
        [self._barr.extend(u32_to_bytes(m), hint) for m, hint in zip(
            metas,
            [' func idx', ' num rets', ' num args', ' num loc vars']
        )]
        
        self._barr.extend(u32_to_bytes(len(func.instructions)), ' num instrs')
        [self._dump_an_instruction(i) for i in func.instructions]
        
    def _dump_an_instruction(self, instr: Instruction):
        """
        .. note::
            code: u8
            or code: u8, operand: u32,
            or code: u8, operand: u64,
        """
        self._barr.append(instr.instr_type.value, f'  instr {instr.instr_type.name.lower()}')
        if instr.operand is not None:
            if instr.op_is_int:
                if instr.operand_signed:
                    cvt = i32_to_bytes
                else:
                    cvt = u32_to_bytes if instr.operand_32bits else u64_to_bytes
            else:
                cvt = f64_to_bytes
            self._barr.extend(cvt(instr.operand), '  instr op')
