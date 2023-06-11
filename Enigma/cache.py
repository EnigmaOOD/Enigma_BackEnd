import json
from django_redis import get_redis_connection
from abc import ABC, abstractmethod

class CacheInterface(ABC):
    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def set(self, key, value, expiration):
        pass


class RedisCache(CacheInterface):
    def __init__(self):
        self.redis_conn = get_redis_connection("default")

    def get(self, key):
        cached_data = self.redis_conn.get(key)
        return cached_data.decode() if cached_data else None

    def set(self, key, value, expiration):
        serialized_value = json.dumps(value)
        self.redis_conn.set(key, serialized_value)
        self.redis_conn.expire(key, expiration)
        return
