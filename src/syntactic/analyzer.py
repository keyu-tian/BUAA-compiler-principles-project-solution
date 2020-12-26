# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.
import logging
from copy import deepcopy
from functools import partial
from typing import List, Optional, NamedTuple, Iterable, Dict

from lexical.tokentype import Token, TokenType
from syntactic.symbol.maintainer import SymbolMaintainer
from syntactic.symbol.ty import TypeDeduction
from syntactic.syn_err import *
from vm.instruction import Instruction, InstrType

VM_OP_CLZ = []


class _BreakContinueInstr(NamedTuple):
    brk: List[Instruction]
    ctn: List[Instruction]


class SyntacticAnalyzer(object):
    """
    
    """
    
    def __init__(self, lg: logging.Logger, tokens: List[Token], str_literals: List[str]):
        self.lg = lg
        self._tokens, self._str_literals = tokens, str_literals
        self._tk_top = 0
        self._symbols = SymbolMaintainer(len(self._str_literals))
        self._parsed = False
        
        self._global_instr: List[Instruction] = []
        self._local_instr: List[Instruction] = []

        self._return_val_ty = False

    def _declare_builtin_funcs(self):
        self._symbols.declare_func('getint', [], 0, TypeDeduction.INT, [])
        self._symbols.declare_func('getdouble', [], 0, TypeDeduction.DOUBLE, [])
        self._symbols.declare_func('getchar', [], 0, TypeDeduction.INT, [])
        
        self._symbols.declare_func('putint', [TypeDeduction.INT], 0, TypeDeduction.VOID, [])
        self._symbols.declare_func('putdouble', [TypeDeduction.DOUBLE], 0, TypeDeduction.VOID, [])
        self._symbols.declare_func('putchar', [TypeDeduction.INT], 0, TypeDeduction.VOID, [])
        self._symbols.declare_func('putstr', [TypeDeduction.INT], 0, TypeDeduction.VOID, [])
        self._symbols.declare_func('putln', [], 0, TypeDeduction.VOID, [])
    
    def _finish_start_func(self):
        main = self._symbols.asserted_get_func('main')
        if len(main.arg_types) != 0:
            raise SynProgramErr(f'arguments found in the "main" func')
        
        if main.num_ret_vals:
            self._global_instr.append(Instruction(InstrType.STACKALLOC))
        self._global_instr.append(Instruction(InstrType.CALLNAME, main.offset))
        
    def analyze_tokens(self):
        if not self._parsed:
            self._symbols.declare_func('_start', [], 0, TypeDeduction.VOID, self._global_instr)
            self._declare_builtin_funcs()
            self._parsed = True
            self.parse_program()
            self._finish_start_func()
        return self._str_literals, self._symbols.global_symbols, self._symbols.global_funcs

    def get(self) -> Token:
        tok = self._tokens[self._tk_top]
        self._tk_top += 1
        return tok

    def peek(self):
        return self._tokens[self._tk_top]

    def meta_peek(self):
        return self._tokens[self._tk_top + 1]

    def asserted_get(self, expected: Iterable[TokenType]) -> Token:
        tok = self.get()
        if tok.token_type not in expected:
            ss = '", "'.join([t.value if isinstance(t.value, str) else t.name for t in expected])
            raise SynTokenError(f'"unexpected token; "{ss}" expected (got "{tok.token_type}")')
        return tok

    def parse_program(self):
        """
        .. note::
            program -> (func_decl | let_decl | const_decl)*
        """
        while self.peek().token_type != TokenType.EOF_TOKEN:
            tok = self.peek()
            if tok.token_type == TokenType.FN_KW:
                self.parse_func_decl()
            elif tok.token_type == TokenType.LET_KW:
                self.parse_var_decl(const=False)
            elif tok.token_type == TokenType.CONST_KW:
                self.parse_var_decl(const=True)
            else:
                raise SynProgramErr(f'unexpected token; FN, LET or CONST expected (got "{tok.token_type}")')
        
    def _append_instr(self, instr: Instruction):
        ls = self._global_instr if self._symbols.within_global_scope else self._local_instr
        instr.ip = len(ls)
        ls.append(instr)

    def parse_func_decl(self):
        """
        .. note::
            func_decl -> 'fn' IDENT '(' func_args? ')' '->' TYPE block_stmt
        """
        self._local_instr.clear()
        
        self.asserted_get({TokenType.FN_KW})
        ident = self.get()
        name = ident.val
        if ident.token_type != TokenType.IDENTIFIER:
            raise SynDeclarationErr('function name missing')
        
        self.asserted_get({TokenType.L_PAREN})
        decl_kws = []
        if self.peek().token_type != TokenType.R_PAREN:
            arg_types = self.parse_func_args(decl_kws)
        else:
            arg_types = []
        self.asserted_get({TokenType.R_PAREN})
        
        self.asserted_get({TokenType.ARROW})
        ty = self.asserted_get({TokenType.INT_TYPE_SPECIFIER, TokenType.DBL_LITERAL, TokenType.VOID_TYPE_SPECIFIER})
        self._return_val_ty = TypeDeduction.from_token_type(ty.token_type)
        
        has_ret_val = self._return_val_ty != TypeDeduction.VOID
        self._symbols.enter_func(f'func {name}', has_ret_val)
        [self._symbols.declare_func_arg(**kw) for kw in decl_kws]
        all_returned = self.parse_block_stmt(brk_ctn_instr=None, is_func=True)

        if not all_returned:
            if has_ret_val:
                raise SynDeclarationErr('control reaches end of non-void function')
            else:
                self._append_instr(Instruction(InstrType.RET))
        
        num_local_vars = self._symbols.exit_func()
        self._symbols.declare_func(
            name=name, arg_types=arg_types, num_local_vars=num_local_vars,
            return_val_ty=self._return_val_ty,
            instructions=deepcopy(self._local_instr)
        )
        
    def parse_func_args(self, decl_kws: List[Dict]) -> List[TypeDeduction]:
        """
        .. note::
            func_args -> func_arg (',' func_arg)*
        """
        arg_types = [self.parse_func_arg(decl_kws)]
        while self.peek().token_type == TokenType.COMMA:
            _ = self.get()
            arg_types.append(self.parse_func_arg(decl_kws))
        return arg_types

    def _parse_non_void_type_specifier(self) -> TypeDeduction:
        """
        .. note::
            type_specifier -> ':' TYPE
        """
        self.asserted_get({TokenType.COLON})
        ty = self.asserted_get({TokenType.INT_TYPE_SPECIFIER, TokenType.DBL_TYPE_SPECIFIER})
        return TypeDeduction.from_token_type(ty.token_type)
    
    def parse_func_arg(self, decl_kws: List[Dict]) -> TypeDeduction:
        """
        .. note::
            func_arg -> 'const'? IDENT type_specifier
        """
        tok = self.get()
        const = False
        if tok.token_type == TokenType.CONST_KW:
            const = True
            tok = self.get()
        if tok.token_type != TokenType.IDENTIFIER:
            raise SynDeclarationErr('argument name missing')
        ty = self._parse_non_void_type_specifier()
        decl_kws.append(dict(name=tok.val, is_int=ty == TypeDeduction.INT, const=const))
        return ty

    def parse_block_stmt(self, brk_ctn_instr: Optional[_BreakContinueInstr], is_func: bool=False) -> bool:
        """
        .. note::
            block_stmt -> '{'
                | let_decl_stmt | const_decl_stmt | if_stmt | while_stmt
                | break_stmt | continue_stmt | return_stmt | empty_stmt
                | block_stmt
                | expr_stmt
            '}'
        """
        block_name = 'block' if brk_ctn_instr is None else 'loop'
        if not is_func:
            self._symbols.enter_scope(block_name)

        self.asserted_get({TokenType.L_BRACE})

        branching = {
            TokenType.IF_KW: partial(self.parse_if_stmt, brk_ctn_instr=brk_ctn_instr),
            TokenType.WHILE_KW: self.parse_while_stmt,
    
            TokenType.LET_KW: partial(self.parse_var_decl, const=False),
            TokenType.CONST_KW: partial(self.parse_var_decl, const=True),
            TokenType.BREAK_KW: partial(self.parse_break_stmt, brk_ctn_instr=brk_ctn_instr),
            TokenType.CONTINUE_KW: partial(self.parse_continue_stmt, brk_ctn_instr=brk_ctn_instr),
            TokenType.RETURN_KW: self.parse_return_stmt,
            TokenType.SEMICOLON: self.get,
        }

        all_returned = False
        while self.peek().token_type not in {TokenType.R_BRACE, TokenType.EOF_TOKEN}:
            if all_returned:
                continue
            first = self.peek()
            if brk_ctn_instr is None and first.token_type in {TokenType.BREAK_KW, TokenType.CONTINUE_KW}:
                raise SynStatementsErr('break/continue statement not within a loop')
            if first.token_type in branching:
                sub_block_all_returned = branching[first.token_type]()
                if first.token_type in {TokenType.IF_KW, TokenType.WHILE_KW} and sub_block_all_returned:
                    all_returned = True
                if first.token_type == TokenType.RETURN_KW:
                    all_returned = True
            elif first.token_type == TokenType.L_BRACE:
                all_returned |= self.parse_block_stmt(brk_ctn_instr=brk_ctn_instr)
            else:   # must be expr_stmt
                self.parse_expr_stmt()
            
        self.asserted_get({TokenType.R_BRACE})
        if not is_func:
            self._symbols.exit_scope()
        return all_returned

    def parse_var_decl(self, const: bool):
        """
        .. note::
            let_decl -> 'let'? IDENT type_specifier ('=' summation)? ';'
            const_decl -> 'const'? IDENT type_specifier '=' summation ';'
        """
        target_tk = TokenType.CONST_KW if const else TokenType.LET_KW
        self.asserted_get({target_tk})
        ident = self.get()
        name = ident.val
        if ident.token_type != TokenType.IDENTIFIER:
            raise SynDeclarationErr('identifier missing')
        decl_ty = self._parse_non_void_type_specifier()

        tok = self.get()
        # parse '='
        if tok.token_type == TokenType.ASSIGN:
            inited = True
        else:
            inited = False
            if const:
                raise SynDeclarationErr(f'uninitialized const "{name}"')
        # perform
        offset = self._symbols.declare_var(name=name, is_int=decl_ty == TypeDeduction.INT, inited=inited, const=const)
        if inited:
            self._append_instr(Instruction(InstrType.GLOBA if self._symbols.within_global_scope else InstrType.LOCA, offset))
            val_ty = self.parse_summation()
            if val_ty != decl_ty:
                raise SynTypeErr(f'invalid assignment from "{val_ty}" to "{decl_ty}"')
                
            self._append_instr(Instruction(InstrType.STORE_64))
            tok = self.get()
        # parse ';'
        if tok.token_type != TokenType.SEMICOLON:
            raise SynDeclarationErr(f'";" missing in the declaration of var "{name}"')
    
    def _parse_cond_and_block_within_if_else(self, has_cond: bool, last_instr_in_each_block: List, brk_ctn_instr: Optional[_BreakContinueInstr]):
        if has_cond:
            cond_ty = self.parse_condition()
            if not cond_ty.evaluable():
                raise SynTypeErr(f'could not convert "{cond_ty}" to "bool"')
            br_false = Instruction(InstrType.BR_FALSE)
            self._append_instr(br_false)
        else:
            br_false = None
        
        all_returned = self.parse_block_stmt(brk_ctn_instr=brk_ctn_instr)     # parse the block statement
        last_instr_in_this_block = Instruction(InstrType.BR)
        self._append_instr(last_instr_in_this_block)
        last_instr_in_each_block.append(last_instr_in_this_block)
        if has_cond:
            br_false.set_operand_to_skip_this_instr(last_instr_in_this_block)
        return all_returned
    
    def parse_if_stmt(self, brk_ctn_instr: Optional[_BreakContinueInstr]) -> bool:
        """
        .. note::
            'if' expr block_stmt ('else' 'if' condition block_stmt)* ('else' block_stmt)?
        """
        self.asserted_get({TokenType.IF_KW})

        all_branches_returned = True
        last_instr_in_each_block = []
        this_branch_returned = self._parse_cond_and_block_within_if_else(True, last_instr_in_each_block, brk_ctn_instr)
        all_branches_returned &= this_branch_returned
        
        while self.peek().token_type == TokenType.ELSE_KW:
            self.get()
            
            if self.peek().token_type == TokenType.IF_KW:
                self.get()
                has_cond = True
            else:
                has_cond = False
            this_branch_returned = self._parse_cond_and_block_within_if_else(has_cond, last_instr_in_each_block, brk_ctn_instr)
            all_branches_returned &= this_branch_returned
            if not has_cond:
                break
        
        [br.set_operand_to_skip_this_instr(last_instr_in_each_block[-1]) for br in last_instr_in_each_block]
        
        return all_branches_returned
    
    def parse_while_stmt(self) -> bool:
        """
        .. note::
            while_stmt -> 'while' condition block_stmt
        """
        self.asserted_get({TokenType.WHILE_KW})

        first_instr_in_the_cond_ip = len(self._local_instr)
        cond_ty = self.parse_condition()
        first_instr_in_the_cond = self._local_instr[first_instr_in_the_cond_ip]
        if not cond_ty.evaluable():
            raise SynTypeErr(f'could not convert "{cond_ty}" to "bool"')
        br_false = Instruction(InstrType.BR_FALSE)
        self._append_instr(br_false)
        
        brk_ctn = _BreakContinueInstr([], [])
        all_returned = self.parse_block_stmt(brk_ctn_instr=brk_ctn)     # parse the block statement
        
        br_back = Instruction(InstrType.BR)
        self._append_instr(br_back)
        br_back.set_operand_to_reach_this_instr(first_instr_in_the_cond)
        br_false.set_operand_to_skip_this_instr(br_back)
        
        [br.set_operand_to_skip_this_instr(br_back) for br in brk_ctn.brk]
        [br.set_operand_to_reach_this_instr(first_instr_in_the_cond) for br in brk_ctn.ctn]
        
        return all_returned
    
    def parse_break_stmt(self, brk_ctn_instr: Optional[_BreakContinueInstr]):
        """
        .. note::
            break_stmt -> 'break' ';'

        """
        self.asserted_get({TokenType.BREAK_KW})
        self.asserted_get({TokenType.SEMICOLON})
        if brk_ctn_instr is None:
            raise SynStatementsErr('break statement not within a loop')
        br = Instruction(InstrType.BR)
        self._append_instr(br)
        brk_ctn_instr.brk.append(br)

    def parse_continue_stmt(self, brk_ctn_instr: Optional[_BreakContinueInstr]):
        """
        .. note::
            continue_stmt -> 'continue' ';'
        """
        self.asserted_get({TokenType.CONTINUE_KW})
        self.asserted_get({TokenType.SEMICOLON})
        if brk_ctn_instr is None:
            raise SynStatementsErr('continue statement not within a loop')
        br = Instruction(InstrType.BR)
        self._append_instr(br)
        brk_ctn_instr.ctn.append(br)

    def parse_return_stmt(self):
        """
        .. note::
            return_stmt -> 'return' summation? ';'
        """
        self.asserted_get({TokenType.RETURN_KW})
        if self._return_val_ty == TypeDeduction.VOID:
            self.asserted_get({TokenType.SEMICOLON})
        else:
            self._append_instr(Instruction(InstrType.ARGA, 0))
            ret_val_ty = self.parse_summation()
            if ret_val_ty != self._return_val_ty:
                raise SynTypeErr(f'invalid conversion from "{ret_val_ty}" to "{self._return_val_ty}"')
            self.asserted_get({TokenType.SEMICOLON})
            self._append_instr(Instruction(InstrType.STORE_64))
        self._append_instr(Instruction(InstrType.RET))
    
    def parse_expr_stmt(self):
        """
        .. note::
            expr_stmt -> condition | assignment ';'
        """
        if self.peek().token_type == TokenType.IDENTIFIER and self.meta_peek().token_type == TokenType.ASSIGN:
            self.parse_assignment()
        else:
            ty = self.parse_condition()
            if ty != TypeDeduction.VOID:
                self._append_instr(Instruction(InstrType.POP))
        self.asserted_get({TokenType.SEMICOLON})
        
    def parse_assignment(self):
        """
        .. note::
            assignment -> IDENT '=' summation
        """
        ident = self.get()
        if ident.token_type != TokenType.IDENTIFIER:
            raise SynAssignmentErr('identifier missing')
        var_name = ident.val
        var = self._symbols.asserted_init_var(var_name)
        var_ty = TypeDeduction.from_is_int(var.is_int)
        if var.const:
            raise SynAssignmentErr(f'assignment of read-only var "{var_name}"')
        
        self._append_instr(Instruction.from_var_loading(var))
        
        self.asserted_get({TokenType.ASSIGN})
        
        val_ty = self.parse_summation()
        if val_ty != var_ty:
            raise SynTypeErr(f'invalid conversion from "{val_ty}" to "{var_ty}"')
        self._append_instr(Instruction(InstrType.STORE_64))

    # NOTE: the result will be stored at the top of vm.stack
    def parse_condition(self) -> TypeDeduction:
        """
        .. note::
            expression -> summation ('>' | '<' | '>=' | '<=' | '==' | '!=' summation)?
        """
        expr_type = lhs_type = self.parse_summation()
        cmp = InstrType.CMP_I if lhs_type == TypeDeduction.INT else InstrType.CMP_F
        op_tt_to_instrs = {
            TokenType.GT: (cmp, InstrType.SET_GT),
            TokenType.LT: (cmp, InstrType.SET_LT),
            TokenType.GE: (cmp, InstrType.SET_LT, InstrType.NOT),
            TokenType.LE: (cmp, InstrType.SET_GT, InstrType.NOT),
            TokenType.EQ: (cmp, InstrType.NOT),
            TokenType.NEQ: (cmp,),
        }
        if self.peek().token_type in op_tt_to_instrs.keys():
            op = self.get()
            if lhs_type not in {TypeDeduction.INT, TypeDeduction.DOUBLE}:
                raise SynTypeErr(f'{lhs_type} cannot be calculated')
            rhs_type = self.parse_summation()
            if lhs_type != rhs_type:
                raise SynTypeErr(f'cannot compare "{lhs_type}" with "{rhs_type}"')
            [self._append_instr(Instruction(t)) for t in op_tt_to_instrs[op.token_type]]
            expr_type = TypeDeduction.BOOL
        return expr_type
        
    # NOTE: the result will be stored at the top of vm.stack
    def parse_summation(self) -> TypeDeduction:
        """
        .. note::
            summation -> product ('+'|'-' product)*
        """
        lhs_type = self.parse_product()
        while self.peek().token_type in {TokenType.PLUS, TokenType.MINUS}:
            pm = self.get()
            if pm.token_type == TokenType.PLUS:
                it = InstrType.ADD_I if lhs_type == TypeDeduction.INT else InstrType.ADD_F
            else:
                it = InstrType.SUB_I if lhs_type == TypeDeduction.INT else InstrType.SUB_F
            rhs_type = self.parse_product()
            if lhs_type != rhs_type:
                raise SynTypeErr(f'cannot add "{lhs_type}" with "{rhs_type}"')
            self._append_instr(Instruction(it))
        return lhs_type

    # NOTE: the result will be stored at the top of vm.stack
    def parse_product(self) -> TypeDeduction:
        """
        .. note::
            product -> factor ('*'|'/' factor)*
        """
        lhs_type = self.parse_factor()
        while self.peek().token_type in {TokenType.MUL, TokenType.DIV}:
            md = self.get()
            if md.token_type == TokenType.MUL:
                it = InstrType.MUL_I if lhs_type == TypeDeduction.INT else InstrType.MUL_F
            else:
                it = InstrType.DIV_I if lhs_type == TypeDeduction.INT else InstrType.DIV_F
            rhs_type = self.parse_factor()
            if lhs_type != rhs_type:
                raise SynTypeErr(f'cannot multiply "{lhs_type}" with "{rhs_type}"')
            self._append_instr(Instruction(it))
        return lhs_type

    # NOTE: the result will be stored at the top of vm.stack
    def parse_factor(self) -> TypeDeduction:
        """
        .. note::
            factor -> element ('as' TYPE)*
        """
        elem_ty = self.parse_element()
        while self.peek().token_type == TokenType.AS_KW:
            _ = self.get()
            as_ty = self.asserted_get({TokenType.INT_TYPE_SPECIFIER, TokenType.DBL_TYPE_SPECIFIER})
            if elem_ty == as_ty:
                continue
            cast = InstrType.ITOF if elem_ty == TypeDeduction.INT else InstrType.FTOI
            self._append_instr(Instruction(cast))
            elem_ty = TypeDeduction.from_token_type(as_ty.token_type)
        return elem_ty

    # NOTE: the result will be stored at the top of vm.stack
    def parse_element(self) -> TypeDeduction:
        """
        .. note::
            element -> '-'* literal | func_calling | IDENT | '(' condition ')'     # todo: '-'* or '-'?
        """
        sign = 1
        while self.peek().token_type == TokenType.MINUS:
            self.get()
            sign *= -1
        
        # if self.peek().token_type == TokenType.STR_LITERAL:
            # raise SynExpressionErr('string literal cannot be calculated')        # todo:
        
        if self.peek().token_type in {TokenType.UINT_LITERAL, TokenType.DBL_LITERAL, TokenType.STR_LITERAL}:
            lit = self.get()
            self._append_instr(Instruction(InstrType.PUSH, lit.val))
            ty = TypeDeduction.from_token_type(lit.token_type)
        
        elif self.peek().token_type == TokenType.IDENTIFIER:
            if self.meta_peek().token_type == TokenType.L_PAREN:
                ty = self.parse_func_calling()
            else:
                ident = self.get()
                var = self._symbols.asserted_get_var_or_arg(ident.val)
                self._append_instr(Instruction.from_var_loading(var))
                self._append_instr(Instruction(InstrType.LOAD_64))
                ty = TypeDeduction.from_is_int(var.is_int)
        else: # must be condition
            self.asserted_get({TokenType.L_PAREN})
            ty = self.parse_condition()
            self.asserted_get({TokenType.R_PAREN})
        if sign < 0:
            self._append_instr(Instruction(InstrType.NEG_I if ty == TypeDeduction.INT else InstrType.NEG_F))
        return ty

    def parse_func_calling(self) -> TypeDeduction:
        """
        .. note::
            func_calling -> IDENT '(' func_params? ')'
        """
        ident = self.get()
        func_name = ident.val
        if ident.token_type != TokenType.IDENTIFIER:
            raise SynCallErr(f'function\'s name missing')
        
        func = self._symbols.asserted_get_func(func_name)
        if func.num_ret_vals:
            self._append_instr(Instruction(InstrType.STACKALLOC, 1))
        
        self.asserted_get({TokenType.L_PAREN})
        if self.peek().token_type != TokenType.R_PAREN:
            param_types = self.parse_func_params()
        else:
            param_types = []
        self._append_instr(Instruction(InstrType.CALLNAME, func.offset))
        if not all(at == pt for at, pt in zip(func.arg_types, param_types)):
            raise SynTypeErr(f'type mismatched in function call of "{func_name}"')
        self.asserted_get({TokenType.R_PAREN})
        return func.return_val_ty
        
    def parse_func_params(self) -> List:
        """
        .. note::
            func_params -> summation (',' summation)*
        """
        param_types = [self.parse_summation()]
        while self.peek().token_type == TokenType.COMMA:
            _ = self.get()
            param_types.append(self.parse_summation())
        return param_types
