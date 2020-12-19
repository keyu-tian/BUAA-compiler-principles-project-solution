# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import struct


u8_to_bytes = lambda u8: struct.pack('>B', u8)
i32_to_bytes = lambda i32: struct.pack('>l', i32)
u32_to_bytes = lambda u32: struct.pack('>L', u32)
u64_to_bytes = lambda u64: struct.pack('>Q', u64)
f64_to_bytes = lambda f64: struct.pack('>d', f64)
u8arr_to_bytes = lambda u8arr: u32_to_bytes(len(u8arr)) + bytes(u8arr)
u32arr_to_bytes = lambda u32arr: u32_to_bytes(len(u32arr)) + bytearray().join(map(u32_to_bytes, u32arr))
u64arr_to_bytes = lambda u64arr: u32_to_bytes(len(u64arr)) + bytearray().join(map(u64_to_bytes, u64arr))
str_to_bytes = lambda s: bytes(s, encoding='ascii')


if __name__ == '__main__':
    print(f64_to_bytes(-2 ** -1))
    print(str_to_bytes('1122'))
    print(u8arr_to_bytes([49, 49, 50, 50]))
    print(u32arr_to_bytes([49, 49, 50, 50]))

