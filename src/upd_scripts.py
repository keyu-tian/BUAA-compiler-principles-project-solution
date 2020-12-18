import os


def dfs_scripts(cwd, upd_fn):
    file_names = os.listdir(cwd)
    for name in file_names:
        path = os.path.join(cwd, name)
        if os.path.isdir(path):
            dfs_scripts(path, upd_fn)
        else:
            if name.endswith('.py'):
                upd_fn(path)


if __name__ == '__main__':
    
    cp = """# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

"""
    
    def upd(path):
        with open(path, 'r', encoding='utf-8') as fp:
            ctt = fp.read()
        if not ctt.startswith(cp):
            with open(path, 'w', encoding='utf-8') as fp:
                fp.write(cp + ctt)
    
    dfs_scripts(os.getcwd(), upd)
