'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Object
'''


######## Import statements ########

# Standard imports
from threading import RLock
from types import SimpleNamespace
from collections.abc import Iterable, Mapping
from operator import attrgetter, methodcaller
from itertools import filterfalse, chain
from inspect import isclass





######## class Object ########

class EventProducer:
    '''
    Instances of this class are used to implemented the observer pattern:
    - An instance of this class can have an arbitrary number of children objects
    (also EventProducer instances) and only one parent (optional).
    An object can be seen in other way as a tree where nodes are objects of this class.

    - Objects can trigger events. Events are propagated from bottom to the top of the object
    hierachy.

    - All methods on this class are thread safe (You can also use the internal threading
    lock of the object to perform synchronization for a custom task on the given object)
    This class implements the "with" protocol with the metamethods __enter__ and __exit__
    to provide a scope where the internal lock of the object is locked

    '''
    def __init__(self, lock=None):
        super().__init__()
        self._children, self._parent = [], None
        self._event_handlers = []
        if lock is None:
            lock = RLock()
        self._lock = lock


    def get_parent(self):
        '''get_parent() -> Object | None
        Get the parent of this object if any. None otherwise

        :rtype: Object | None

        '''
        with self:
            return self._parent


    def has_parent(self):
        '''has_parent() -> bool
        Returns True if this object has parent. False otherwise.

        :rtype: bool

        '''
        with self:
            return self._parent is not None


    def get_ancestor(self, kind):
        '''get_ancestor(kind) -> Object | None
        Get the closest ancestor 'x' of this object such that isinstance(x, kind) is
        evaluated to True. Returns None no ancestor evaluates such predicate to True or
        this object has no parent.

        :rtype: Object | None

        '''
        with self:
            parent = self._parent
            if parent is None:
                return None
            return parent if isinstance(parent, kind) else parent.get_ancestor(kind)


    def get_children(self, kind=None):
        '''get_children([kind]) -> List[Object]
        Get all the child objects of this one with the given type. If kind is None
        returns all the childs.
        '''
        with self:
            if kind is None:
                return tuple(self._children)
            return tuple(filter(lambda child: isinstance(child, kind), self._children))


    def add_child(self, child):
        '''add_child(child: Object)
        Adds a new child to this object.

        :type child: Object

        .. note::
            Once the child was added to this object, it fires a 'object_entered' event.

        '''
        assert isinstance(child, EventProducer)
        with self:
            self._children.append(child)
            with child._lock:
                child._parent = self
            child.fire_event('object_entered')


    def remove_child(self, child):
        '''remove_child(child: Object)
        Removes a child from this object

        :type child: Object

        .. note::
            Before the given child is remove from this object, it fires a 'object_exit' event.

        '''
        assert isinstance(child, EventProducer)
        with self:
            if child not in self._children:
                return
            self._children.remove(child)
            with child._lock:
                child.fire_event('object_exit')
                child._parent = None




    def get_predecessors(self, kind=None):
        '''get_predecessors() -> List[Object]
        Get a list of all predecessors with the given type. If the input argument is set
        to None, return all the predecessors.
        '''
        def predecessors():
            if kind is None:
                yield from self._children
            else:
                yield from filter(lambda child: isinstance(child, kind), self._children)

            for child in self._children:
                yield from child.get_predecessors(kind)

        with self:
            return tuple(predecessors())





    def add_event_handler(self, callback, event_type=None):
        '''add_event_handler(callback: Callable[, event_type: str])
        Add a new handler that will listen the events fired by this object or any of its predecessors.

        :param callback: A callable object that will be invoked when a event is triggered by this object
            or any of its predecessors. It will receive the kind of event and the object who fired the
            event as positional arguments.

        :param event_type: Type of events to listen. None to listen to any kind.

        .. seealso:: :func:`fire_event`

        '''
        assert callable(callback)
        assert event_type is None or isinstance(event_type, str)

        event_handler = SimpleNamespace(
            callback=callback,
            event_type=event_type
        )
        with self:
            self._event_handlers.append(event_handler)



    def remove_event_handler(self, callback, event_type=None):
        '''remove_event_handler(callback: Callable[, event_type: str])
        Remove all the handlers listening to this object events with the given callback.

        :param event_type: If None, remove all handlers having the provided callback.
            Otherwise, removes only the ones listening the given event type.

        '''
        assert callable(callback)
        assert event_type is None or isinstance(event_type, str)

        with self:
            self._event_handlers = list(filterfalse(
                lambda handler: handler.callback == callback and (event_type is None or handler.event_type == event_type),
                self._event_handlers
            ))



    def _fire_event(self, source, event_type, *args, **kwargs):
        with self:
            for handler in self._event_handlers:
                if handler.event_type is not None and handler.event_type != event_type:
                    continue
                callback = handler.callback
                if callback(event_type, source, *args, **kwargs):
                    # Event handler cancelled the event
                    return

            # Propagate the event from bottom to top
            if self._parent is not None:
                self._parent._fire_event(source, event_type, *args, **kwargs)


    def fire_event(self, event_type, *args, **kwargs):
        '''fire_event(event_type: str, ...)
        Fires an event and propagate it to the top of the object hierachy.

        :param event_type: Kind of event to be fired.
        :param args: Additional positional arguments that will receive the event handlers listening
            for the event fired
        :param kwargs: Additional keyword arguments that will receive the event handlers listening
            for the event fired

        .. note::
            The event is propagated from the bottom to the top of the object hierachy.
            If an event handler listening for the event fired is invoked and returns True,
            the event will be cancelled and no more event handlers will be triggered.

        .. seealso:: :func:`add_event_handler`

        '''
        assert isinstance(event_type, str)
        self._fire_event(self, event_type, *args, **kwargs)



    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._lock.release()

    def acquire(self, *args, **kwargs):
        return self._lock.acquire(*args, **kwargs)

    def release(self):
        self._lock.release()




if __name__ == '__main__':
    obj = Object()
    a, b = Object(), Object()
    obj.add_child(a)
    obj.add_child(b)
