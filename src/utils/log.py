import logging
import os
from typing import Optional


class C0Logger(object):
    def __init__(self, lg: Optional[logging.Logger]):
        self.__lg = lg
        self.__verbose = self.__lg is not None
    
    @property
    def verbose(self):
        return self.__verbose
    
    @staticmethod
    def do_nothing(*args, **kwargs):
        pass
    
    def __getattr__(self, attr: str):
        return getattr(self.__lg, attr) if self.verbose else C0Logger.do_nothing


def create_logger(lg_name, f_name, level=logging.INFO, stream=True):
    d_name = os.path.split(f_name)[0]
    if not os.path.exists(d_name):
        os.makedirs(d_name)
    
    l = logging.getLogger(lg_name)
    formatter = logging.Formatter(
        fmt='[%(asctime)s][%(filename)10s][line:%(lineno)4d][%(levelname)4s] %(message)s',
        datefmt='%m-%d %H:%M:%S'
    )
    fh = logging.FileHandler(f_name)
    fh.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fh)
    if stream:
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        l.addHandler(sh)
    return l
