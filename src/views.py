'''
Author: Víctor Ruiz Gómez
Description: This module defines the helper class DictView and its subclasses
'''

######## Imports ########

from collections.abc import Mapping
from collections import OrderedDict
from abc import ABC, abstractmethod
from operator import attrgetter
from functools import partial
from tabulate import tabulate
from asciitree import LeftAligned

from lib3d_mec_ginac_ext import _System
from lib3d_mec_ginac_ext import _symbol_types, _parse_symbol_type




class ObjectsView(Mapping):
    def __init__(self, get_objects, get_object, has_object):
        self._get_objects = get_objects
        self._get_object = get_object
        self._has_object = has_object

    def __getitem__(self, name):
        return self._get_object(name)

    def __len__(self):
        return len(self._get_objects())

    def __iter__(self):
        return map(attrgetter('name'), self._get_objects())

    def __contains__(self, name):
        return self._has_object(name)

    def __bool__(self):
        return len(self) > 0

    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return self.__str__()



class ObjectsTableView(ObjectsView):
    def __init__(self, get_objects, get_object, has_object, columns, show_headers=False):
        super().__init__(get_objects, get_object, has_object)
        self.columns, self.show_headers = columns, show_headers

    def get_row_values(self, object):
        return [getattr(object, column) for column in self.columns]

    def __str__(self):
        t = []
        if self.show_headers:
            t.append(self.columns)
        t.extend(map(self.get_row_values, self.values()))

        return tabulate(t, headers='firstrow' if self.show_headers else (), tablefmt='plain')




class BasesView(ObjectsView):
    def __init__(self, system):
        super().__init__(system._get_bases, system._get_base, system._has_base)

    def __str__(self):
        def get_roots():
            return [base for base in self.values() if not base.has_previous()]

        def get_children(base):
            return [x for x in self.values() if x.has_previous() and x.get_previous() == base]

        def format_base(base):
            return base.name


        roots = get_roots()

        def get_tree(node):
            children = get_children(node)
            return OrderedDict(dict(zip(map(format_base, children), map(get_tree, children))))

        trees = [dict([(format_base(root), get_tree(root))]) for root in roots]
        return '\n'.join(map(LeftAligned(), trees))




class SymbolsView(ObjectsTableView):
    def __init__(self, system, kind=None):
        columns = ['name', 'value']
        if kind is None:
            columns.insert(1, 'type')
        else:
            kind = _parse_symbol_type(kind)
        super().__init__(
            partial(system._get_symbols, kind=kind),
            partial(system._get_symbol, kind=kind),
            partial(system._has_symbol, kind=kind),
            columns=columns,
            show_headers=kind is None
        )
        self.system, self.kind = system, kind


    def get_row_values(self, symbol):
        values = [symbol.name, symbol.value]
        if self.kind is None:
            for symbol_type in _symbol_types:
                if symbol in self.system._get_symbols(symbol_type):
                    break
            values.insert(1, symbol_type.decode().replace('_', ' '))
        return values

    def __str__(self):
        if len(self) == 0:
            if self.kind is not None:
                return f'No {self.kind.decode().replace("_", " ")} symbols created yet'
            return 'No symbols created yet'
        return super().__str__()




class MatricesView(ObjectsTableView):
    def __init__(self, system):
        super().__init__(
            system._get_matrices, system._get_matrix, system._has_matrix,
            columns=('name', 'size')
        )

    def get_row_values(self, matrix):
        return matrix.name, f'{matrix.num_rows}x{matrix.num_cols}'

    def __str__(self):
        if len(self) == 0:
            return 'No matrices created yet'
        return super().__str__()




class VectorsView(ObjectsTableView):
    def __init__(self, system):
        super().__init__(
            system._get_vectors, system._get_vector, system._has_vector,
            columns=('name', 'x', 'y', 'z', 'base'),
            show_headers=True
        )

    def get_row_values(self, vector):
        return vector.name, vector.x, vector.y, vector.z, vector.base.name

    def __str__(self):
        if len(self) == 0:
            return 'No vectors created yet'
        return super().__str__()
