import json
import redis
from django.conf import settings
from django_redis import get_redis_connection

#def cache_set(key, data, expire=settings.CACHE_EXPIRATION):
def cache_set(key, data):
    redis_conn = get_redis_connection("default")
    #redis_conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    serialized_data = json.dumps(data)
    redis_conn.set(key, serialized_data)
    #redis_conn.expire(key, expire)
    redis_conn.expire(key, 3600) #تغییر داده شود
    return

def cache_get(key):
    redis_conn = get_redis_connection("default")
    #redis_conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    cached_data = redis_conn.get(key)
    if cached_data:
        deserialized_data = json.loads(cached_data.decode())
        return deserialized_data
    return None