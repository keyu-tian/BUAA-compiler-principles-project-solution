# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

class C0ELF:
    
    def __init__(self):
        self.magic_num, self.version = 0x72303b3e, 0x1
        self.g_vars, self.g_fns = [], []
