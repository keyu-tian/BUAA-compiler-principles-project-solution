# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

from enum import Enum, unique
from typing import Union

from utils.crawler import parse_html


@unique
class InstrType(Enum):
    ADD_F = 0x24  # 计算 res = sta[-2] + sta[-1]，参数为浮点数；res 入栈
    ADD_I = 0x20  # 计算 res = sta[-2] + sta[-1]，参数为整数；res 入栈
    ALLOC = 0x18  # 在堆上分配 size 字节的内存；得到的 addr 入栈
    AND = 0x2b  # 计算 res = sta[-2] & sta[-1]；res 入栈
    ARGA = 0x0b  # 加载 off 个 slot 处参数/返回值的地址
    BR = 0x41  # 无条件跳转偏移 off
    BR_FALSE = 0x42  # 如果 test 是 0 则跳转偏移 off
    BR_TRUE = 0x43  # 如果 test 非 0 则跳转偏移 off
    CALL = 0x48  # 调用编号为 id 的函数
    CALLNAME = 0x4a  # 调用名称与编号为 id 的全局变量内容相同的函数
    CMP_F = 0x32  # 比较浮点数 sta[-2] 和 sta[-1] 大小；sta[-2] < sta[-1] 时压入 -1, sta[-2] > sta[-1] 时压入 1, sta[-2] == sta[-1] 时压入 0。浮点数无法比较时压入 0。
    CMP_I = 0x30  # 比较有符号整数 sta[-2] 和 sta[-1] 大小；sta[-2] < sta[-1] 时压入 -1, sta[-2] > sta[-1] 时压入 1, sta[-2] == sta[-1] 时压入 0。浮点数无法比较时压入 0。
    CMP_U = 0x31  # 比较无符号整数 sta[-2] 和 sta[-1] 大小；sta[-2] < sta[-1] 时压入 -1, sta[-2] > sta[-1] 时压入 1, sta[-2] == sta[-1] 时压入 0。浮点数无法比较时压入 0。
    DIV_F = 0x27  # 计算 res = sta[-2] / sta[-1]，参数为浮点数；res 入栈
    DIV_I = 0x23  # 计算 res = sta[-2] / sta[-1]，参数为有符号整数；res 入栈
    DIV_U = 0x28  # 计算 res = sta[-2] / sta[-1]，参数为无符号整数；res 入栈
    DUP = 0x04  # 复制栈顶 slot
    FREE = 0x19  # 释放 addr 指向的内存块
    FTOI = 0x37  # 把 sta[-1] 从浮点数转换成整数
    GLOBA = 0x0c  # 加载第 n 个全局变量/常量的地址
    ITOF = 0x36  # 把 sta[-1] 从整数转换成浮点数
    LOAD_16 = 0x11  # 从 addr 加载 16 位 value 压栈
    LOAD_32 = 0x12  # 从 addr 加载 32 位 value 压栈
    LOAD_64 = 0x13  # 从 addr 加载 64 位 value 压栈
    LOAD_8 = 0x10  # 从 addr 加载 8 位 value 压栈
    LOCA = 0x0a  # 加载 off 个 slot 处局部变量的地址
    MUL_F = 0x26  # 计算 res = sta[-2] * sta[-1]，参数为浮点数；res 入栈
    MUL_I = 0x22  # 计算 res = sta[-2] * sta[-1]，参数为整数；res 入栈
    NEG_F = 0x35  # 对 sta[-1] 取反
    NEG_I = 0x34  # 对 sta[-1] 取反
    NOP = 0x00  # 空指令
    NOT = 0x2e  # 计算 res = !sta[-1]；res 入栈
    OR = 0x2c  # 计算 res = sta[-2] | sta[-1]；res 入栈
    PANIC = 0xfe  # 恐慌（强行退出）
    POP = 0x02  # 弹栈 1 个 slot
    POPN = 0x03  # 弹栈 num 个 slot
    PRINT_C = 0x55  # 向标准输出写入字符 c
    PRINT_F = 0x56  # 向标准输出写入浮点数 f
    PRINT_I = 0x54  # 向标准输出写入一个有符号整数 x
    PRINT_S = 0x57  # 向标准输出写入全局变量 i 代表的字符串
    PRINTLN = 0x58  # 向标准输出写入一个换行
    PUSH = 0x01  # 将 num 压栈
    RET = 0x49  # 从当前函数返回
    SCAN_C = 0x51  # 从标准输入读入一个字符 c
    SCAN_F = 0x52  # 从标准输入读入一个浮点数 f
    SCAN_I = 0x50  # 从标准输入读入一个整数 n
    SET_GT = 0x3a  # 如果 sta[-1] > 0 则推入 1，否则 0
    SET_LT = 0x39  # 如果 sta[-1] < 0 则推入 1，否则 0
    SHL = 0x29  # 计算 res = sta[-2] << sta[-1]；res 入栈
    SHR = 0x2a  # 计算 res = sta[-2] >> sta[-1] （算术右移）；res 入栈
    SHRL = 0x38  # 计算 res = sta[-2] >>> sta[-1] （逻辑右移）；res 入栈
    STACKALLOC = 0x1a  # 在当前栈顶分配 size 个 slot，初始化为 0
    STORE_16 = 0x15  # 把 val(sta[-1]) 截断到 16 位存入 addr(sta[-2]) 所指的地址
    STORE_32 = 0x16  # 把 val(sta[-1]) 截断到 32 位存入 addr(sta[-2]) 所指的地址
    STORE_64 = 0x17  # 把 val(sta[-1]) 存入 addr(sta[-2]) 所指的地址
    STORE_8 = 0x14  # 把 val 截断到 8 位存入 addr 所指的地址
    SUB_F = 0x25  # 计算 res = sta[-2] - sta[-1]，参数为浮点数；res 入栈
    SUB_I = 0x21  # 计算 res = sta[-2] - sta[-1]，参数为整数；res 入栈
    XOR = 0x2d  # 计算 res = sta[-2] ^ sta[-1]；res 入栈


_operand_64bits_instr_types = {
    InstrType.PUSH,
}
_operand_signed_instr_types = {
    InstrType.BR, InstrType.BR_FALSE, InstrType.BR_TRUE
}


class Instruction(object):
    
    def __init__(self, instr_type: InstrType, operand: Union[int, float] = None):
        self.instr_type, self.operand = instr_type, operand
        self.op_is_int = isinstance(self.operand, int)
        self.operand_signed = self.instr_type in _operand_signed_instr_types
        self.operand_32bits = self.instr_type not in _operand_64bits_instr_types
        self.ip = 0
    
    def __repr__(self):
        ty_str = 'ui'[self.operand_signed] + ['64', '32'][self.operand_32bits]
        # op_str = '' if self.operand is None else f' ({ty_str}: {self.operand})'
        op_str = '' if self.operand is None else f' ({self.operand})'
        if self.operand_signed:
            op_str = op_str[:-1] + ', ' + f'next={self.ip + self.operand + 1})'
        return self.instr_type.name + op_str

    def set_operand_to_skip_this_instr(self, instr):
        self.operand = instr.ip - self.ip

    def set_operand_to_reach_this_instr(self, instr):
        self.operand = instr.ip - self.ip - 1
    
    @staticmethod
    def from_var_loading(var):
        if var.is_global:
            it = InstrType.GLOBA
        elif var.is_arg:
            it = InstrType.ARGA
        else:
            it = InstrType.LOCA
        return Instruction(it, var.offset)
    
if __name__ == '__main__':
    table = parse_html(url=r'https://c0.karenia.cc/navm/instruction.html', target_name='table')
    tuples = sorted(
        list(map(
            lambda x: list(x.stripped_strings)[:2][::-1] + [list(x.stripped_strings)[-1]],
            table.find_all('tr')
        ))[1:]
    )
    # from pprint import pprint as pp
    # pp(tuples)
    
    res_str = '\n\t'.join(
        f'{name.replace(".", "_").upper()} = {code}\t\t# {comment}'
        for name, code, comment in tuples
    )
    
    print(f"""from enum import Enum


class InstructionCode(Enum):
    {res_str}
""")
