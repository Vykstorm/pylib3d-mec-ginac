'''
Author: Víctor Ruiz Gómez
Description: This file defines the class VtkObjectWrapper
'''

######## Import statements ########

from .object import Object
from .viewer import VtkViewer




######## class VtkObjectWrapper ########

class VtkObjectWrapper(Object):
    '''
    This class inherits the features of the Object class and its a wrapper around
    a vtk object (it holds a reference to an instance of the class vtk.vtkObject)

    If an instance of this class was added to a viewer object (VtkViewer instace),
    when the user tries to acquire the lock for such object, the viewer lock will also
    be locked (This is done to provide thread safety layer using the VTK library).

    '''
    def __init__(self, handler):
        if not isinstance(handler, vtkObject):
            raise TypeError('handler must be an instance of vtkObject')
        super().__init__()
        self._handler = handler


    def get_handler(self):
        '''get_handler() -> vtkObject
        Get the vtkObject attached to this instance

        :rtype: vtkObject

        '''
        return self._handler


    def __enter__(self):
        self._lock.acquire()
        node = self._parent
        while node is not None:
            node._lock.acquire()
            if isinstance(node, VtkViewer):
                break
            parent = node._parent
            node._lock.release()
            node = parent

        return self


    def __exit__(self, exc_type, exc_value, tb):
        node = self._parent
        while node is not None:
            if isinstance(node, VtkViewer):
                node._lock.release()
                break
            node._lock.acquire()
            parent = node._parent
            node._lock.release()
            node = parent

        self._lock.release()
