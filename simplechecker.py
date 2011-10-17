#!/usr/bin/env python

import ast
import sys

class DumbValidator(ast.NodeVisitor):
    FORBIDDEN = ['json'] 

    def __init__(self):
        self.with_OK = False

    def visit(self, asdf):
        return super(DumbValidator, self).visit(asdf)

    def visit_Import(self, node):
        names = node.names
        for name in names:
            if name.name in self.FORBIDDEN:
                raise Exception("don't import forbidden stuff. it is bad for you.")

    def visit_ImportFrom(self, node):
        if node.module == '__future__':
            for name in node.names:
                if name.name == 'with_statement':
                    self.with_OK = True
    
    def visit_With(self, node):
        # crap out if not from __future__ import with_statement
        if not self.with_OK:
            raise Exception("with statements are not ok yet! from __future__ import with_statement")

def main():
    fs = sys.argv[1]
    try:
        root_node = ast.parse(open(fs, 'r').read())
    except SyntaxError as e:
        print "Cannot parse source"
        sys.exit(1)

    DumbValidator().visit(root_node)

if __name__ == '__main__':
    main()
