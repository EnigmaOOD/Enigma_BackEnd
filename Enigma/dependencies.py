import importlib
from Enigma import settings

cache_servise_class_neme = settings.Cache_Redis_SERVICE
cache_servise_class = getattr(importlib.import_module(cache_servise_class_neme.rsplit('.', 1)[0]), cache_servise_class_neme.rsplit('.', 1)[1])
cache_servise_instance = cache_servise_class()
