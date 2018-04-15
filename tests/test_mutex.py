import unittest
import redis
import time

from redismutex import RedisMutex


class TestRedisMutex(unittest.TestCase):

    def setUp(self):

        self.redis = redis.StrictRedis(host='localhost', port=6379, db=4)
        self.mutex = RedisMutex(self.redis)
        self.key = str(time.time())

    def test_basic_flow(self):

        self.mutex = self.mutex.acquire_lock(self.key)

        # Check if key and value are set properly
        self.assertEqual(self.mutex.key, self.key)
        self.assertTrue(self.mutex.value)
        self.assertIsInstance(self.mutex.value, str)
        # Check if value is same as that in redis
        redis_value = self.redis.get(self.key).decode("utf-8")
        self.assertEqual(self.mutex.value, redis_value)

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
            # Check if value is same as that in redis
            redis_value = self.redis.get(self.key).decode("utf-8")
            self.assertEqual(self.mutex.value, redis_value)

        # Check if key and value are reset to None after unlock
        self.assertIsNone(self.mutex.key)
        self.assertIsNone(self.mutex.value)
