#!/usr/bin/env python

import os
import stat
import ast
import sys
from _ast import *

class ForbiddenImport(Exception):
    pass

class WithistheFuture(Exception):
    pass

class ExceptionList(Exception):
    def __init__(self, list_of_exceptions):
        self.list_of_exceptions = self._flatten_exception_list(list_of_exceptions)

    def _flatten_exception_list(self, list_of_exceptions):
        loe = []
        for k in list_of_exceptions:
            if isinstance(k, ExceptionList):
                loe += self._flatten_exception_list(k.list_of_exceptions)
            else:
                loe.append(k)
        return loe

    def __str__(self):
        l = ['Exceptions Caught']
        for exception in self.list_of_exceptions:
            l.append("Exception:%s Message:%s" % (exception.__class__.__name__, exception.__str__()))
        return '\n'.join(l)

class DumbValidator(ast.NodeVisitor):
    """
    Some simple checks to make sure our code conforms to python 2.5

    Possible Problem: bubbling exceptions makes this really damn slow... (~5seconds execution time)
    """
    FORBIDDEN = ['json'] 

    def __init__(self):
        self.with_OK = False

    def visit(self, asdf):
        return super(DumbValidator, self).visit(asdf)

    def visit_Import(self, node):
        names = node.names
        for name in names:
            if name.name in self.FORBIDDEN:
                raise ForbiddenImport(name.name)

    def visit_ImportFrom(self, node):
        if node.module == '__future__':
            for name in node.names:
                if name.name == 'with_statement':
                    self.with_OK = True
    
    def visit_With(self, node):
        # crap out if not from __future__ import with_statement
        if not self.with_OK:
            raise WithistheFuture(node.lineno)

    # pretty much copied with the docs
    def generic_visit(self, node):
        exceptions = []
        for k, v in ast.iter_fields(node):
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, AST):
                        try:
                            self.visit(item)
                        except Exception as e:
                            exceptions.append(e)
            elif isinstance(v, AST):
                try:
                    self.visit(v)
                except Exception as e:
                    exceptions.append(e)
        if exceptions:
            raise ExceptionList(exceptions)

"""
Rather ugly utility functions

"""

def validate_file(fs):
    try:
        root_node = ast.parse(open(fs, 'r').read())
        DumbValidator().visit(root_node)
    except Exception as e:
        print e
        return False
    return True

def validate_path(path):
    mode = os.stat(path).st_mode
    return_values = []
    # just a file
    if stat.S_ISREG(mode):
        return_values += [validate_file(path)]
    # a dir
    elif stat.S_ISDIR(mode):
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames: 
                if f.endswith(".py") and not f.startswith('test'):
                    abs_path = os.path.join(dirpath, f) 
                    return_values += [validate_file(abs_path)]
    return all(return_values)

def main():
    fs = sys.argv[1]
    validate_path(fs)

if __name__ == '__main__':
    main()
