from __future__ import absolute_import

from .mutex import RedisMutex


class with_redismutex(object):
    """Decorator to wrap a function in
    """
    def __init__(self, conn, key=None, **mutex_kwargs):
        self.conn = conn
        self.key = key
        self.mutex_kwargs = mutex_kwargs

    def __call__(self, func):

        def wrapped_func(*args, **kwargs):

            key = self.key or self.generate_key(*args, **kwargs)
            mutex = RedisMutex(self.conn, **self.mutex_kwargs)

            with mutex.acquire_lock(key):
                return_value = func(*args, **kwargs)

            return return_value

        return wrapped_func

    def generate_key(self, *args, **kwargs):
        """Proxy method to override mutex key generation based on
        function parameters.
        """
        return self.key
