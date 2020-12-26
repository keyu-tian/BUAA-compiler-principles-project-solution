# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

from abc import ABCMeta, abstractmethod
from pprint import pformat
from typing import Dict, List, Union

from syntactic.symbol.ty import TypeDeduction
from syntactic.syn_err import SynDeclarationErr
from vm.instruction import Instruction


class Attrs(metaclass=ABCMeta):
    def __init__(self, offset):
        self.offset = offset
    
    @abstractmethod
    def is_func(self):
        pass


class VarAttrs(Attrs):
    
    def __init__(
            self, offset: int,
            is_global: bool, is_arg: bool,
            is_int: bool, inited: bool, const: bool,
    ):
        super(VarAttrs, self).__init__(offset)
        self.is_global, self.is_arg, self.is_int, self.inited, self.const = (
            is_global, is_arg, is_int, inited, const
        )
    
    def is_func(self):
        return False


class FuncAttrs(Attrs):
    
    def __init__(
            self, offset: int,
            name: str, arg_types: List[TypeDeduction],
            num_local_vars: int, return_val_ty: TypeDeduction,
            instructions: List[Instruction],
    ):
        super(FuncAttrs, self).__init__(offset)
        self.name, self.arg_types, self.num_local_vars, self.return_val_ty, self.instructions = (
            name, arg_types, num_local_vars, return_val_ty, instructions
        )
    
    def is_func(self):
        return True
    
    @property
    def num_ret_vals(self):
        return int(self.return_val_ty != TypeDeduction.VOID)
    
    def __repr__(self):
        ins_s = '\t' + '\n\t'.join([
            f'{instr.ip}: {instr}'
            for instr in self.instructions
        ])
        if len(ins_s) > 1:
            ins_s = '\n' + ins_s + '\n'
        else:
            ins_s = ' '
        args_s = ", ".join(map(str, self.arg_types))
        return f'fn {self.name} [{self.offset}] loc={self.num_local_vars}, args=[{args_s}] -> ret={self.return_val_ty} {{{ins_s}}}'


class _ScopeWiseSymbolTable(Dict[str, Union[VarAttrs, FuncAttrs]]):
    
    def __init__(self, name):
        super(_ScopeWiseSymbolTable, self).__init__()
        self.__name = name
    
    def __setitem__(self, name, attr):
        if name in self:
            raise SynDeclarationErr(f'conflicting declaration of symbol "{name}"')
        super(_ScopeWiseSymbolTable, self).__setitem__(name, attr)
    
    def __str__(self):
        return f'scope-wise symbol table @{self.__name}:\n{pformat(self)}'
