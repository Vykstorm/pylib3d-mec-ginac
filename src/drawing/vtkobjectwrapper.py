'''
Author: Víctor Ruiz Gómez
Description: This file defines the class VtkObjectWrapper
'''

######## Import statements ########

# imports from other modules
from ..utils.events import EventProducer

# vtk
from vtk import vtkObject



######## class VtkObjectWrapper ########

class VtkObjectWrapper(EventProducer):
    '''
    This class inherits the features of the Object class and its a wrapper around
    a vtk object (it holds a reference to an instance of the class vtk.vtkObject)
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
