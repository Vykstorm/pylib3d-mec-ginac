'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class View and all its subclasses
'''






######## Class View ########

cdef class View:
    def __str__(self):
        return ConsolePrinter().print(self)

    def __repr__(self):
        return self.__str__()



######## Class TableView ########

cdef class TableView(View):
    def __init__(self, data=None, headers=None):
        self.data = data if data is not None else []
        self.headers = headers if headers is not None else ()





######## Subclasses of TableView ########


class SymbolsTableView(TableView):
    def __init__(self, system, kind=None):
        if kind is None:
            data = [(symbol.name, symbol.type, symbol.value) for symbol in system._get_symbols()]
            headers = ['name', 'type', 'value']
        else:
            data = [(symbol.name, symbol.value) for symbol in system._get_symbols()]
            headers = None

        super().__init__(
            headers=headers,
            data=data
        )




class MatricesTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'size'],
            data=[(m.name, f'{m.num_rows}x{m.num_cols}') for m in system._get_matrices()]
        )



class VectorsTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'x', 'y', 'z', 'base'],
            data=[(v.name, v.x, v.y, v.z, v.base.name) for v in system._get_vectors()]
        )



class TensorsTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'base'],
            data=[(t.name, t.base.name) for t in system._get_tensors()]
        )



class BasesTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'previous', 'rot.tupla', 'rot.angle'],
            data=[(b.name, b.previous if b.has_previous() else None,
                '  '.join(map(str, b.rotation_tupla)), b.rotation_angle) for b in system._get_bases()]
        )



class PointsTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'position'],
            data=[(p.name, p.position.name if p.has_previous() else None) for p in system._get_points()]
        )



class FramesTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'point', 'base'],
            data=[(f.name, f.point.name, f.base.name) for f in system._get_frames()]
        )



class SolidsTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'point', 'base', 'mass', 'CM', 'IT'],
            data=[(s.name, s.point.name, s.base.name, str(s.mass), s.CM.name, s.IT.name) for s in system._get_solids()]
        )



class WrenchesTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name', 'force', 'moment', 'solid', 'type'],
            data=[(w.name, w.force.name, w.moment.name, w.solid.name, w.type) for w in system._get_wrenches()]
        )


class DrawingsTableView(TableView):
    def __init__(self, system):
        super().__init__(
            headers=['name'],
            data=[(d.name,) for d in system._get_drawings()]
        )
