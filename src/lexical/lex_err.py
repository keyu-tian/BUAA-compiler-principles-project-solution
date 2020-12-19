# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.


class TokenCompilationError(Exception):
    pass


class QuoteMismatchErr(TokenCompilationError):
    pass


class UnknownTokenErr(TokenCompilationError):
    pass
