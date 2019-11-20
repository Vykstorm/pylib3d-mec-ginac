'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Object
'''

from threading import RLock
from types import SimpleNamespace
from collections.abc import Iterable, Mapping
from operator import attrgetter
from itertools import filterfalse, chain
from inspect import isclass


class Object:
    '''
    Base class for the rest of classes in the submodule 'drawing'.
    '''
    def __init__(self):
        super().__init__()
        self._children, self._parent = [], None
        self._event_handlers = []
        self._lock = RLock()


    def get_parent(self):
        with self:
            return self._parent


    def has_parent(self):
        with self:
            return self._parent is not None


    def get_ancestor(self, kind):
        #assert isclass(kind)
        with self:
            parent = self._parent
            if parent is None:
                return None
            return parent if isinstance(parent, kind) else parent.get_ancestor(kind)


    def get_children(self, kind=None):
        #assert kind is None or isclass(kind)
        with self:
            if kind is None:
                return tuple(self._children)
            return tuple(filter(lambda child: isinstance(child, kind), self._children))


    def add_child(self, child):
        assert isinstance(child, Object)
        with self:
            self._children.append(child)
            with child._lock:
                child._parent = self
            child.fire_event('object_entered')


    def remove_child(self, child):
        assert isinstance(child, Object)
        with self:
            if child not in self._children:
                return
            self._children.remove(child)
            with child._lock:
                child.fire_event('object_exit')
                child._parent = None



    def add_event_handler(self, callback, event_type=None, args=[], kwargs={}):
        assert callable(callback)
        assert event_type is None or isinstance(event_type, str)
        assert isinstance(args, Iterable) and isinstance(kwargs, Mapping)

        args, kwargs = tuple(args), dict(kwargs)

        event_handler = SimpleNamespace(
            callback=callback,
            event_type=event_type,
            args=args,
            kwargs=kwargs
        )
        with self:
            self._event_handlers.append(event_handler)



    def remove_event_handler(self, callback, event_type=None):
        assert callable(callback)
        assert event_type is None or isinstance(event_type, str)

        with self:
            self._event_handler = list(filterfalse(
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
        assert isinstance(event_type, str)
        self._fire_event(self, event_type, *args, **kwargs)



    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()




if __name__ == '__main__':
    obj = Object()
    a, b = Object(), Object()
    obj.add_child(a)
    obj.add_child(b)
