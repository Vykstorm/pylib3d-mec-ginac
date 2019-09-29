'''
Author: Víctor Ruiz Gómez
Description: This module defines the helper class DictView and its subclasses
'''

######## Imports ########

from collections.abc import Iterable, Mapping
from collections import OrderedDict
from abc import ABC, abstractmethod
from tabulate import tabulate
from asciitree import LeftAligned

from lib3d_mec_ginac_ext import _System
from lib3d_mec_ginac_ext import _symbol_types




######## Class TreeView ########


class TreeView(ABC):
    '''
    This class can be used to print a tree structure in text mode.
    You need to inherit from this class and implement the methods
    get_roots, get_children, format_node
    Then you can use __str__ and __repr__ metamethods to print the tree
    '''

    @abstractmethod
    def get_roots(self):
        '''get_roots() -> Iterable
        This method must be implemented by subclasses.
        It must return a list of all objects which are the roots of the tree to
        print
        '''
        pass

    @abstractmethod
    def get_children(self, node):
        '''get_children(node) -> Iterable
        This method must be implemented by subclasses.
        It must return a list of all objects which are the children of the given node.
        '''
        pass


    def format_node(self, node):
        '''format_node(node) -> str
        This method takes a node (object) and returns the label to be shown when
        printing the tree. By default it returns str(node)
        '''
        return str(node)


    def __str__(self):
        # This method prints the tree

        def _get_roots():
            roots = self.get_roots()
            if roots is not None and not isinstance(roots, Iterable):
                raise TypeError('get_roots should return an iterable or None')
            return tuple(roots) if roots is not None else ()

        def _get_children(node):
            children = self.get_children(node)
            if children is not None and not isinstance(children, Iterable):
                raise TypeError('get_children should return an iterable or None')
            return tuple(children) if children is not None else ()

        def _format_node(node):
            s = self.format_node(node)
            if not isinstance(s, str):
                raise TypeError('format_node should return a str object')
            return s


        roots = _get_roots()
        def get_tree(node):
            children = _get_children(node)
            return OrderedDict(dict(zip(map(_format_node, children), map(get_tree, children))))

        trees = [dict([(_format_node(root), get_tree(root))]) for root in roots]
        return '\n'.join(map(LeftAligned(), trees))


    def __repr__(self):
        return self.__str__()





######## Class TableView ########


class TableView(ABC):
    '''
    This class can be used to print a table structure in text mode.
    You need to implement the next abstract method get_rows.

    Metamethods __str__ & __repr__ can be used to print the table.
    '''
    def __init__(self, columns, show_headers=False):
        '''
        Initialize this instance

        :param columns: The columns of the table (a list of strings)
        :param show_headers: If true, the first row will be the names of the columns.
            By default is set to False
        '''
        self.columns, self.show_headers = columns, show_headers


    @abstractmethod
    def get_rows(self):
        '''
        This method should be implemented by subclasses.
        It must return a list of all rows that should be printed in the table
        (any kind of object can represent a row)
        '''
        pass

    def get_column_value(self, row, column):
        '''
        This method should return the value to be shown in the table for the given
        row and column (By default returns getattr(row, column, None))
        '''
        return getattr(row, column, None)


    def __str__(self):
        def _get_rows():
            rows = self.get_rows()
            if rows is not None and not isinstance(rows, Iterable):
                raise TypeError('get_rows should return an iterable or None')
            return tuple(rows) if rows is not None else ()

        def _get_column_value(row, column):
            value = self.get_column_value(row, column)
            return value


        # This method prints the table
        t = []
        if self.show_headers:
            t.append(self.columns)
        t.extend([[_get_column_value(row, column) for column in self.columns] for row in _get_rows()])

        return tabulate(t, headers='firstrow' if self.show_headers else (), tablefmt='plain')


    def __repr__(self):
        return self.__str__()




######## Class SymbolsView ########


class SymbolsView(TableView):
    '''
    Objects of this class are returned by System.get_symbols method.
    '''
    def __init__(self, system, kind=None):
        columns = ['name']
        if kind is None:
            columns.append('type')
        columns.append('value')
        super().__init__(
            show_headers=False,
            columns=columns
        )
        self.system, self.kind = system, kind

    def get_rows(self):
        return _System.get_symbols_by_type(self.system, self.kind)

    def get_column_value(self, symbol, attr):
        if attr in ('name', 'value'):
            return super().get_column_value(symbol, attr)

        for symbol_type in _symbol_types:
            if symbol in _System.get_symbols_by_type(self.system, symbol_type):
                return symbol_type.decode().replace('_', ' ')
        return None




######## Class BasesView ########


class BasesView(TreeView):
    '''
    Objects of this class are returned by System.get_bases method
    '''
    def __init__(self, system):
        super().__init__()
        self.system = system

    def get_roots(self):
        return [base for base in _System._get_geom_objs(self.system, 'base') if not base.has_previous()]

    def get_children(self, base):
        bases = _System._get_geom_objs(self.system, 'base')
        return [x for x in bases if x.has_previous() and x.get_previous() == base]

    def format_node(self, base):
        return base.name
