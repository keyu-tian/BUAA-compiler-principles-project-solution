# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

from pprint import pformat
from typing import NamedTuple, Dict, List, Union

from syntactic.symbol.ty import TypeDeduction
from syntactic.syn_err import SynDeclarationErr
from vm.instruction import Instruction


class _VarAttrs(NamedTuple):
    offset: int
    is_global: bool
    is_arg: bool
    is_int: bool
    inited: bool
    const: bool
    
    @staticmethod
    def is_func(): return False
    
    @property
    def inited_replica(self): return self._replace(inited=True)


class _FuncAttrs(NamedTuple):
    offset: int
    name: str
    arg_types: List[TypeDeduction]
    num_local_vars: int
    return_val_ty: TypeDeduction
    instructions: List[Instruction]
    
    @staticmethod
    def is_func(): return True

    def __repr__(self):
        ins_s = '\t' + '\n\t'.join([
            f'{instr.ip}: {instr}'
            for instr in self.instructions
        ])
        args_s = ", ".join(map(str, self.arg_types))
        return f'fn {self.name} [{self.offset}] loc={self.num_local_vars}, args=[{args_s}] -> ret={self.return_val_ty} {{\n{ins_s}\n}}'


class _ScopeWiseSymbolTable(Dict[str, Union[_VarAttrs, _FuncAttrs]]):
    
    def __init__(self, name):
        super(_ScopeWiseSymbolTable, self).__init__()
        self.__name = name
    
    def __setitem__(self, name, attr):
        if name in self:
            raise SynDeclarationErr(f'conflicting declaration of symbol "{name}"')
        super(_ScopeWiseSymbolTable, self).__setitem__(name, attr)
    
    def __str__(self):
        return f'scope-wise symbol table @{self.__name}:\n{pformat(self)}'

