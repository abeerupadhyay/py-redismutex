import time
import uuid
import redis

from .errors import (
    MutexLockError, BlockTimeExceedError, MutexLockValueError
)

DEFAULT_BLOCK_TIME = 5
DEFAULT_DELAY = 0.5
DEFAULT_EXPIRY = 7


class RedisMutex(object):
    """
    """
    def __init__(self, redis_conn,  blocking=True,
                 block_time=DEFAULT_BLOCK_TIME, delay=DEFAULT_DELAY,
                 expiry=DEFAULT_EXPIRY):

        if not isinstance(redis_conn, redis.StrictRedis):
            raise TypeError(
                "Connection object must be of type 'redis.StrictRedis', "
                "got '{}' instead".format(type(redis_conn))
            )

        self.redis = redis_conn
        self.blocking = blocking
        self.expiry = expiry

        # block_time and delay are not relevant if the
        # mutex is non-blocking, i.e., if blocking=False.
        self.block_time = block_time if self.blocking else None
        self.delay = delay if self.blocking else None

        # Mutex key and mutex value are set to None by default. These
        # are automatically set when a lock is acquired and can be
        # accessed via self.key and self.value
        self.__mkey = None
        self.__mvalue = None

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.release_lock()
        return self

    @property
    def key(self):
        return self.__mkey

    @property
    def value(self):
        return self.__mvalue

    def generate_unique_id(self):
        return uuid.uuid4().__str__()

    def lock(self):
        """
        """
        # nx=True ensures that the value must be set only when the
        # provided key does not exists in redis.
        result = self.redis.set(
            self.__mkey, self.__mvalue, nx=True, ex=self.expiry
        )

        if not result:
            raise MutexLockError(
                "Unable to acquire lock using key '{}'".format(self.__mkey)
            )

        return self

    def unlock(self):
        """
        """
        stored_value = self.redis.get(self.__mkey).decode("utf-8")

        # The given key does not exists in redis
        if not stored_value:
            raise MutexLockError(
                "Unable to unlock. Key '{}' does not exists in redis."
                .format(self.__mkey)
            )

        # The given value is not equal to the stored value. This is
        # done to remove the lock in a safe way - A lock can only be
        # removed by the process which created it. Read more at
        # https://redis.io/topics/distlock#why-failover-based-implementations-are-not-enough
        elif not stored_value == self.__mvalue:
            raise MutexLockValueError(
                "Unable to unlock. Value for key '{}' was reset."
                .format(self.__mkey)
            )

        self.redis.delete(self.__mkey)

        self.__mkey = None
        self.__mvalue = None

        return self

    def acquire_lock(self, mutex_key):
        """
        """
        self.__mkey = mutex_key
        self.__mvalue = self.generate_unique_id()

        if not self.blocking:
            return self.lock()

        start = int(time.time())
        elapsed_time = 0

        # Poll redis to acquire lock on the given key for the allowed
        # blocking time
        while elapsed_time < self.block_time:
            try:
                return self.lock()
            except MutexLockError as e:
                # Add a delay before next poll
                time.sleep(self.delay)
                elapsed_time = int(time.time()) - start

        # Exceeded the allowed waiting time for the mutex and failed
        # to acquire lock in this duration. Hence raise TimeOutError
        raise BlockTimeExceedError(
            "Exceeded max allowed block time while acquiring lock. Allowed "
            "limit is {}s, took {}s.".format(self.block_time, elapsed_time)
        )

    def release_lock(self):
        """
        """
        if not self.__mkey or not self.__mvalue:
            raise MutexLockError(
                "Unable to perform operation. Found null values for mutex "
                "key and(or) value."
            )

        return self.unlock()
