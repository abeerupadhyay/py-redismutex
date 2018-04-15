# py-redismutex
[![Build Status](https://travis-ci.org/esquarer/py-redismutex.svg?branch=master)](https://travis-ci.org/esquarer/py-redismutex)

Python implementation of Mutex using Redis

### Installation

Install using the github link
```shell
pip install -e git+https://github.com/esquarer/py-redismutex@master#egg=redismutex
```

### Usage

Create a redis connection using `redis.StrictRedis` and pass it to `RedisMutex` class to create a mutex. 
```python
import redis
from redismutex import RedisMutex

conn = redis.StrictRedis(host='localhost', port=6379, db=1)
mutex = RedisMutex(conn)
mutex_key = 'YOUR-MUTEX-KEY'

with mutex.acquire_lock(mutex_key):
    print(mutex.key, mutex.value)
    # your blocking code
    # goes here...
```
