from __future__ import unicode_literals, print_function


class lazy_property(object):
    """
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    """

    def __init__(self, fn):
        self.fn = fn
        self.func_name = fn.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fn(obj)
        setattr(obj, self.func_name, value)
        return value
