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
    """Helper for generating consistent cache keys"""
    
    @staticmethod
    def get_key(prefix, user_id, page=1, page_size=10):
        """Generate a cache key with prefix, user ID and pagination info"""
        return f"{prefix}:user-{user_id}:page-{page}:size-{page_size}"
    
    @staticmethod
    def get_feed_key(user_id, page=1, page_size=10):
        """Generate a key for feed cache"""
        return CacheHelper.get_key('feed', user_id, page, page_size)
    
    @staticmethod
    def get_newsfeed_key(user_id, page=1, page_size=10):
        """Generate a key for newsfeed cache"""
        return CacheHelper.get_key('newsfeed', user_id, page, page_size)
    
    @staticmethod
    def get_or_set(key, function, timeout=None):
        """Get value from cache or calculate and set it"""
        timeout = timeout or getattr(settings, 'CACHE_TTL', 900)  # Default 15 min
        value = cache.get(key)
        if value is None:
            value = function()
            cache.set(key, value, timeout=timeout)
        return value

def is_debug_mode():
    """
    Check if application is running in debug mode
    """
    return settings.DEBUG