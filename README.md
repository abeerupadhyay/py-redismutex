# py-redismutex
[![Build Status](https://travis-ci.org/esquarer/py-redismutex.svg?branch=master)](https://travis-ci.org/esquarer/py-redismutex) [![Documentation Status](https://readthedocs.org/projects/py-redismutex/badge/?version=latest)](http://py-redismutex.readthedocs.io/en/latest/?badge=latest)

Python implementation of Mutex using Redis

### Installation

Install using the github link
```shell
pip install -e git+https://github.com/esquarer/py-redismutex@master#egg=redismutex
```

### Usage

To apply mutex to a block of code, first create a redis connection object using `redis.StrictRedis`. This connection object is necessary as all the mutex keys are stored in redis. Now use the `RedisMutex` to create a mutex object.

```python
import redis
from redismutex import RedisMutex

conn = redis.StrictRedis(host='localhost', port=6379, db=1)
mutex = RedisMutex(conn)
mutex_key = 'YOUR-MUTEX-KEY'

with mutex.acquire_lock(mutex_key):
    # your blocking code
    # goes here...
    print(mutex.key, mutex.value)
```

View detailed docs at http://py-redismutex.readthedocs.io/en/latest/
