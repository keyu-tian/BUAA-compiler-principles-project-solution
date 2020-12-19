# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.


class SyntacticCompilationError(Exception):
    pass


class SynTokenError(SyntacticCompilationError):
    pass


class SynReferenceErr(SyntacticCompilationError):
    pass


class SynProgramErr(SyntacticCompilationError):
    pass


class SynDeclarationErr(SyntacticCompilationError):
    pass


class SynStatementsErr(SyntacticCompilationError):
    pass


class SynIfStmtErr(SyntacticCompilationError):
    pass


class SynWhileStmtErr(SyntacticCompilationError):
    pass


class SynAssignmentErr(SyntacticCompilationError):
    pass


class SynTypeErr(SyntacticCompilationError):
    pass


class SynOutputErr(SyntacticCompilationError):
    pass


class SynExpressionErr(SyntacticCompilationError):
    pass


class SynFactorErr(SyntacticCompilationError):
    pass
