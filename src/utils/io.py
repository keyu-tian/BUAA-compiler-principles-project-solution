from functools import partial

from meta import F_ENCODING

r_open = partial(open, mode='r', encoding=F_ENCODING)
wb_open = partial(open, mode='wb', encoding=F_ENCODING)
