'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Object
'''

from threading import RLock
from types import SimpleNamespace
from collections.abc import Iterable, Mapping
from operator import attrgetter
from itertools import filterfalse
from inspect import isclass


class Object:
    '''
    Base class for the rest of classes in the submodule 'drawing'.
    '''
    def __init__(self):
        self._lock = RLock()
        self._children, self._parent = [], None
        self._event_handlers = []


    def get_parent(self):
        with self._lock:
            return self._parent


    def has_parent(self):
        with self._lock:
            return self._parent is not None


    def get_children(self, kind=None):
        assert kind is None or isclass(kind)

        with self._lock:
            if kind is None:
                return tuple(self._children)
            return tuple(filter(lambda child: isinstance(child, kind), self._children))


    def add_child(self, child):
        assert isinstance(child, Object)
        with self._lock:
            self._children.append(child)
            with child._lock:
                child._parent = self


    def remove_child(self, child):
        assert isinstance(child, Object)
        with self._lock:
            if child not in self._children:
                return
            self._children.remove(child)
            with child._lock:
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
        with self._lock:
            self._event_handlers.append(event_handler)


    def remove_event_handler(self, callback, event_type=None):
        assert callable(callback)
        assert event_type is None or isinstance(event_type, str)

        with self._lock:
            self._event_handler = list(filterfalse(
                lambda handler: handler.callback == callback and (event_type is None or handler.event_type == event_type),
                self._event_handlers
            ))


    def _fire_event(self, source, event_type, *args, **kwargs):
        with self._lock:
            for handler in self._event_handlers:
                if handler.event_type is not None and handler.event_type != event_type:
                    continue
                callback = handler.callback
                callback(source, *args, **kwargs)

            # Propagate the event from bottom to top
            if self._parent is not None:
                self._parent._fire_event(source, event_type, *args, **kwargs)


    def fire_event(self, event_type, *args, **kwargs):
        assert isinstance(event_type, str)
        self._fire_event(self, event_type, *args, **kwargs)



    def get_lock(self):
        return self._lock

    def lock(self):
        self._lock.acquire()

    def unlock(self):
        self._lock.release()

    @property
    def lock(self):
        return self._lock




if __name__ == '__main__':
    obj = Object()
    a, b = Object(), Object()
    obj.add_child(a)
    obj.add_child(b)
