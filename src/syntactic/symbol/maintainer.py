# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

from typing import List

from syntactic.symbol.ty import TypeDeduction
from syntactic.symbol.table import _ScopeWiseSymbolTable, VarAttrs, FuncAttrs
from syntactic.syn_err import SynReferenceErr
from vm.instruction import Instruction


class SymbolMaintainer(object):
    
    def __init__(self, num_str_literals):
        super(SymbolMaintainer, self).__init__()
        self._global_symbol_cnt = num_str_literals
        self._num_func_args = self._num_local_vars = 0
        self._num_ret_vals = False
        self._global_table = _ScopeWiseSymbolTable('global')
        self._local_tables: List[_ScopeWiseSymbolTable] = []
        self._cur_func_name: str = ...

    @property
    def global_symbols(self):
        return list(self._global_table.values())

    @property
    def global_funcs(self):
        return list(filter(lambda x: x.is_func() and len(x.instructions), self._global_table.values()))
    
    def enter_func(self, name: str, has_return_value: bool):
        self._num_func_args = self._num_local_vars = 0
        self._cur_func_name = name
        self._num_ret_vals = int(has_return_value)
        self.enter_scope(f'@func {name}')
    
    def enter_scope(self, name):
        self._local_tables.append(_ScopeWiseSymbolTable(name))
    
    def exit_scope(self):
        return self._local_tables.pop()
    
    def exit_func(self):
        self.exit_scope()
        return self._num_local_vars
    
    def declare_func(self, name: str, arg_types: List[TypeDeduction], num_local_vars: int, return_val_ty: TypeDeduction, instructions: List[Instruction]):
        self._global_table[name] = FuncAttrs(self._global_symbol_cnt, name, arg_types, num_local_vars, return_val_ty, instructions)
        self._global_symbol_cnt += 1   # indexing from 0

    def declare_func_arg(self, name: str, is_int: bool, const: bool):
        self._local_tables[-1][name] = VarAttrs(self._num_ret_vals + self._num_func_args, is_global=False, is_arg=True, is_int=is_int, inited=True, const=const)
        self._num_func_args += 1

    @property
    def within_global_scope(self):
        return len(self._local_tables) == 0

    def declare_var(self, name: str, is_int: bool, inited: bool, const: bool):
        kw = dict(is_arg=False, is_int=is_int, inited=inited, const=const)
        if self.within_global_scope:
            kw['is_global'] = True
            tbl, offset_attr_name = self._global_table, '_global_symbol_cnt'
        else:
            kw['is_global'] = False
            tbl, offset_attr_name = self._local_tables[-1], '_num_local_vars'
        return self._declare_var(tbl, name, offset_attr_name, kw)   # returns the offset for generating LOAD instruction

    def _declare_var(self, tbl, name, offset_attr_name, kw):
        offset = getattr(self, offset_attr_name)
        tbl[name] = VarAttrs(offset=offset, **kw)
        setattr(self, offset_attr_name, offset + 1)
        return offset

    # def declare_global_var(self, name: str, is_int: bool, inited: bool, const: bool):
    #     self._global_table[name] = _VarAttrs(self._global_symbol_cnt, is_arg=False, is_int=is_int, inited=inited, const=const)
    #     self._global_symbol_cnt += 1
    #     return self._global_symbol_cnt - 1     # returns the offset for generating LOAD instruction
    #
    # def declare_local_var(self, name: str, is_int: bool, inited: bool, const: bool):
    #     self._local_tables[-1][name] = _VarAttrs(self._num_local_vars, is_arg=False, is_int=is_int, inited=inited, const=const)
    #     self._num_local_vars += 1
    #     return self._num_local_vars - 1        # returns the offset for generating LOAD instruction
    
    def asserted_get_var_or_arg(self, name):
        return self._asserted_get_symbol(name, expect_func=False)[0]
    
    def asserted_get_func(self, name):
        return self._asserted_get_symbol(name, expect_func=True)[0]
    
    def asserted_init_var(self, name) -> VarAttrs:
        var, tbl = self._asserted_get_symbol(name, expect_func=False)
        tbl.update({name: var.inited_replica})
        return var
    
    def _asserted_get_symbol(self, name: str, expect_func: bool):
        clz, hint = (FuncAttrs, 'function') if expect_func else (VarAttrs, 'local variable or argument')
        for tbl in reversed([self._global_table] + self._local_tables):
            syb = tbl.get(name, None)
            if isinstance(syb, clz):
                return syb, tbl
        raise SynReferenceErr(f'reference of undefined {hint} "{name}"')
    
    def __str__(self):
        return f'=> global:\n{self._global_table}\n=> locals:\n{chr(10).join(map(str, self._local_tables))}\n'


if __name__ == '__main__':
    sm = SymbolMaintainer()
    sm.declare_func('f1', 1, 1, True, [])
    sm.declare_global_var('g1', True, True, False)
    
    sm.enter_func('main')
    sm.declare_local_var('m1', True, True, False)
    
    sm.enter_scope('if')
    sm.declare_local_var('i1', True, True, False)
    
    sm.enter_scope('while')
    sm.declare_local_var('w1', True, True, False)
    sm.declare_local_var('w2', True, True, False)
    sm.declare_local_var('w3', False, False, False)
    sm.init_var('w3')
    print('sm1', sm, sep='\n')
    sm.exit_scope()
    
    sm.exit_scope()
    
    sm.declare_local_var('m2', True, True, False)
    sm.declare_local_var('m3', True, True, False)
    print('sm2', sm, sep='\n')
    
    sm.exit_func()
    
    print('sm3', sm, sep='\n')
