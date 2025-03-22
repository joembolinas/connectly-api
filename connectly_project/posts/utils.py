class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.settings = {}

from django.core.cache import cache
from django.conf import settings

class CacheHelper:
    @staticmethod
    def get_key(prefix, *args):
        """Generate a cache key with prefix and args"""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    @staticmethod
    def get_or_set(key, function, timeout=None):
        """Get value from cache or calculate and set it"""
        timeout = timeout or getattr(settings, 'CACHE_TTL', 900)  # Default 15 min
        value = cache.get(key)
        if value is None:
            value = function()
            cache.set(key, value, timeout=timeout)
        return value