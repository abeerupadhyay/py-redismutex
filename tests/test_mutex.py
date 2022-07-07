import time
import unittest

import redis

from redismutex import RedisMutex
from redismutex.errors import BlockTimeExceedError, MutexLockError, MutexUnlockError

REDIS_CONN = redis.StrictRedis(host="localhost", port=6379, db=4)


class TestRedisMutex(unittest.TestCase):
    """Tests for basic locking and unlocking"""

    def setUp(self):
        self.redis = REDIS_CONN
        self.mutex = RedisMutex(self.redis)
        self.key = str(time.time())

    def test_basic_flow(self):

        self.mutex = self.mutex.acquire_lock(self.key)

        # Check if key and value are set properly
        self.assertEqual(self.mutex.key, self.key)
        self.assertTrue(self.mutex.value)
        self.assertIsInstance(self.mutex.value, str)

        self.mutex = self.mutex.release_lock()

        # Check if key and value are reset to None after unlock
        self.assertIsNone(self.mutex.key)
        self.assertIsNone(self.mutex.value)

    def test_as_context_manager(self):

        with self.mutex.acquire_lock(self.key):

            # Check if key and value are set properly
            self.assertEqual(self.mutex.key, self.key)
            self.assertTrue(self.mutex.value)
            self.assertIsInstance(self.mutex.value, str)

        # Check if key and value are reset to None after unlock
        self.assertIsNone(self.mutex.key)
        self.assertIsNone(self.mutex.value)

    def test_invalid_connection(self):
        """Check if correct redis connection is provided to RedisMutex"""
        with self.assertRaises(TypeError):
            RedisMutex("invlaid-connection")

        with self.assertRaises(TypeError):
            RedisMutex(1234)

        with self.assertRaises(TypeError):
            RedisMutex({"foo": "bar"})

    def test_generate_unique_id(self):
        """mutex.generate_unique_id() should always generate a different
        string and should be independent of any parameter.
        """
        unique_ids = []
        for i in range(100):
            unique_ids.append(self.mutex.generate_unique_id())

        self.assertIsInstance(unique_ids[0], str)

        set_unique_ids = set(unique_ids)
        self.assertEqual(len(unique_ids), len(set_unique_ids))

    def test_lock_already_exists(self):
        """When a lock on the given key already exists."""

        # Create a lock using a new mutex
        new_mutex = RedisMutex(self.redis, block_time=10, expiry=12)
        new_mutex = new_mutex.acquire_lock(self.key)

        self.mutex.block_time = 1
        with self.assertRaises(BlockTimeExceedError):
            self.mutex.acquire_lock(self.key)

        # A blocking mutex will raise a MutexLockError instead of
        # BlockTimeExceedError as blcok time does not comes into play
        # during locking of a non blocking mutex.
        self.mutex.blocking = False
        with self.assertRaises(MutexLockError):
            self.mutex.acquire_lock(self.key)

        new_mutex.release_lock()

    def test_unlock_without_locking(self):
        """When release_lock() or unlock() is called before acquiring
        a valid mutex lock.
        """
        with self.assertRaises(MutexUnlockError):
            self.mutex.release_lock()

        with self.assertRaises(MutexUnlockError):
            self.mutex.unlock()


class TestRedisMutexKeyExpiry(unittest.TestCase):
    """Tests related to mutex key expiration"""

    def setUp(self):
        self.redis = REDIS_CONN
        self.mutex = RedisMutex(self.redis, block_time=1, expiry=2)
        self.key = str(time.time())

    def test_key_expire(self):
        """When unlock is attempted after key is expired"""
        with self.assertRaises(MutexUnlockError):
            # Acquire lock and release after the expiration of the key.
            # This would raise MutexLockError as the key does not
            # exists in redis anymore and mutex is trying to delete it.
            self.mutex.acquire_lock(self.key)
            time.sleep(2.5)
            self.mutex.release_lock()

    def test_key_override(self):
        """When unlock is attempted after mutex key is overriden by
        another mutex after expiration.
        """
        new_mutex = RedisMutex(self.redis, block_time=1, expiry=2)

        with self.assertRaises(MutexUnlockError):
            # Acquire lock and release after the expiration of the key.
            # After the expiration a new mutex acquires the lock for the
            # same key. This key cannot be deleted by the old mutex as
            # the unique value generated for the key will be different
            # and would hence raise a MutexLockValueError
            self.mutex.acquire_lock(self.key)
            time.sleep(2.5)
            new_mutex = new_mutex.acquire_lock(self.key)
            self.mutex.release_lock()

        # cleanup
        new_mutex = new_mutex.release_lock()

    def test_new_mutex_lock_after_expiry(self):
        """When a new mutex tries to acquire an expried lock"""
        new_mutex = RedisMutex(self.redis, block_time=1, expiry=2)

        self.mutex.acquire_lock(self.key)
        # Let the key expire...
        time.sleep(2.5)

        # As the key has expired, a new mutex should be able to
        # acquire lock with the same key
        new_mutex.acquire_lock(self.key)

        self.assertEqual(new_mutex.key, self.key)
        self.assertTrue(new_mutex.value)
        self.assertIsInstance(new_mutex.value, str)

        new_mutex.release_lock()
