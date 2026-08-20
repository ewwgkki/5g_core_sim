# utils/contextvars_stub.py
# Minimal contextvars stub for Python 3.6
# Must be injected into sys.modules BEFORE any other import

import sys

if sys.version_info < (3, 7) and 'contextvars' not in sys.modules:
    from threading import local as _local

    _storage = _local()

    class ContextVar(object):
        def __init__(self, name, default=None):
            self.name = name
            self._default = default

        def get(self, default=None):
            val = getattr(_storage, self.name, None)
            if val is None:
                return default if default is not None else self._default
            return val[0]

        def set(self, value):
            token = Token(self, getattr(_storage, self.name, None))
            setattr(_storage, self.name, (value,))
            return token

        def reset(self, token):
            if token._old is None:
                try:
                    delattr(_storage, self.name)
                except AttributeError:
                    pass
            else:
                setattr(_storage, self.name, token._old)

    class Token(object):
        MISSING = object()

        def __init__(self, var, old):
            self._var = var
            self._old = old

    class Context(object):
        def run(self, func, *args, **kwargs):
            return func(*args, **kwargs)

    def copy_context():
        return Context()

    # Build a fake module and inject it
    import types
    mod = types.ModuleType('contextvars')
    mod.ContextVar = ContextVar
    mod.Token = Token
    mod.Context = Context
    mod.copy_context = copy_context
    sys.modules['contextvars'] = mod
