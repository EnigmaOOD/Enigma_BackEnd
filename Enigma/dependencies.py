from cache import RedisCache

def get_cache_instance():
    return RedisCache()

API_VIEW_DEPENDENCIES = {
    'ShowMembers': get_cache_instance,
    'GroupInfo': get_cache_instance,
}
