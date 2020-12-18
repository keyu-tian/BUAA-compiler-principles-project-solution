import datetime
from functools import partial

from meta import F_ENCODING

r_open = partial(open, mode='r', encoding=F_ENCODING)
wb_open = partial(open, mode='wb', encoding=F_ENCODING)


def time_str(fsys=False):
    return (
        datetime.datetime.now().strftime('%m-%d %H-%M-%S') if fsys
        else datetime.datetime.now().strftime('[%m-%d %H:%M:%S]')
    )
