'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''


from lib3d_mec_ginac_ext import Matrix
from vtk import vtkProp, vtkMatrix4x4, vtkActor
import numpy as np
from threading import RLock
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor



class Drawing3D:
    '''
    An instance of this class represents any 3D renderable entity.
    '''

    def __init__(self, viewer, system, actor=None):
        # Validate & parse input arguments
        if actor is None:
            source = vtkSphereSource()
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(source.GetOutputPort())
            actor = vtkActor()
            actor.SetMapper(mapper)



        # Initialize internal fields
        self._transformation = np.eye(4).astype(np.float64)
        self._lock = RLock()
        self._children, self._parent = [], None
        self._viewer, self._system = viewer, system
        self._actor = None
        self._set_actor(actor)



    def get_actor(self):
        '''get_actor() -> vtkProp
        Get the vtk actor associated to this drawing object

        :rtype: vtkProp

        '''
        with self._lock:
            return self._actor


    def get_children(self):
        '''get_children() -> List[Drawing3D]
        Get all child drawing objects

        :rtype: List[Drawing3D]

        '''
        with self._lock:
            return tuple(self._children)


    def get_parent(self):
        '''get_parent() -> Drawing3D | None
        Get the parent of this drawing object if it has. None otherwise

        :rtype: Drawing3D | None

        '''
        with self._lock:
            return self._parent



    def _set_actor(self, actor):
        # Initialize vtk actor user matrix
        actor.SetUserMatrix(vtkMatrix4x4())
        # Set default properties for the actor
        actor.VisibilityOn()

        with self._lock:
            self._actor = actor



    def set_actor(self, actor):
        '''set_actor(actor: vtkProp)
        Change the vtk actor attached to this drawing object
        '''
        with self._lock:
            self._viewer.remove_actor(self._actor)
            self._set_actor(actor)
            # Update this drawing
            self.update()

        # Redraw
        self._viewer.redraw()



    def _add_child(self, child):
        # Add child to the list of children of this drawing
        with self._lock:
            self._children.append(child)

        # Change child parent
        with child._lock:
            child._parent = self



    def add_child(self, child):
        '''add_child(child: Drawing3D)
        Add a new child drawing object
        '''
        self._add_child(child)

        # Update child drawing
        child.update()

        # Redraw
        self._viewer.redraw()




    def update(self):
        '''update()
        Updates this drawing object
        '''
        # Update this drawing affine transformation matrix
        self.update_transformation()
        # Update child drawings
        self.update_children()



    def update_children(self):
        '''update_children()
        Update all child drawing objects
        '''
        with self._lock:
            for child in self._children:
                child.update()



    def update_transformation(self):
        '''update_transformation()
        Compute affine transformation for this drawing object and update vtk
        actor user matrix
        '''
        # Compute affine transformation numerically for this drawing
        matrix = np.eye(4).astype(np.float64)

        with self._lock:
            # Concatenate transformation of the parent drawing if any
            if self._parent is not None:
                matrix = self._parent._transformation @ matrix

            self._transformation = matrix
            self._actor.GetUserMatrix().DeepCopy(tuple(map(float, matrix.flat)))



    def show(self):
        '''show()
        Toogle visibility on for this drawing object
        '''
        # Toggle visibility on
        with self._lock:
            self._actor.VisibilityOn()

        # Redraw scene
        self._viewer.redraw()



    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object
        '''
        # Toggle visibility off
        with self._lock:
            self._actor.VisibilityOff()

        # Redraw scene
        self._viewer.redraw()
