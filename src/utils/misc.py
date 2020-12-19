# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

import datetime
from functools import partial

from meta import FS_ENCODING

r_open = partial(open, mode='r', encoding=FS_ENCODING)
wb_open = partial(open, mode='wb', encoding=FS_ENCODING)


def time_str(fs=False):
    return (
        datetime.datetime.now().strftime('%m-%d %H-%M-%S') if fs
        else datetime.datetime.now().strftime('[%m-%d %H:%M:%S]')
    )


class SingletonMetaCls(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaCls, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
