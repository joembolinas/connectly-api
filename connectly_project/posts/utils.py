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
import hashlib
import json
from functools import wraps
from django.db import connection, transaction, models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time

class CacheHelper:
    """Helper for cache operations with versioning and patterns"""
    
    # Cache version - bump this when changing cache structure
    VERSION = 1
    
    @staticmethod
    def get_key(prefix, user_id, page=1, page_size=10):
        """Generate a versioned cache key"""
        return f"v{CacheHelper.VERSION}:{prefix}:user-{user_id}:page-{page}:size-{page_size}"
    
    @staticmethod
    def get_feed_key(user_id, page=1, page_size=10):
        return CacheHelper.get_key('feed', user_id, page, page_size)
    
    @staticmethod
    def get_newsfeed_key(user_id, page=1, page_size=10):
        return CacheHelper.get_key('newsfeed', user_id, page, page_size)
    
    @staticmethod
    def get_user_key(user_id):
        return f"v{CacheHelper.VERSION}:user:{user_id}"
    
    @staticmethod
    def get_post_key(post_id):
        return f"v{CacheHelper.VERSION}:post:{post_id}"
        
    @staticmethod
    def get_key_pattern(prefix, user_id=None):
        """Get a pattern for cache key deletion with django-redis"""
        if user_id:
            return f"v{CacheHelper.VERSION}:{prefix}:user-{user_id}:*"
        return f"v{CacheHelper.VERSION}:{prefix}:*"
    
    @staticmethod
    def get_or_set(key, function, timeout=None):
        """Get value from cache or calculate and set it"""
        timeout = timeout or getattr(settings, 'CACHE_TTL', 900)  # Default 15 min
        value = cache.get(key)
        if value is None:
            value = function()
            cache.set(key, value, timeout=timeout)
        return value

class SafeCacheHelper:
    """A safer version of cache operations that won't crash if cache operations fail"""
    
    @staticmethod
    def delete(key):
        """Delete a cache key safely"""
        try:
            cache.delete(key)
        except Exception as e:
            # Log this but don't fail the request
            print(f"Cache delete error: {str(e)}")
    
    @staticmethod
    def delete_pattern(pattern):
        """Try to delete pattern if Redis, otherwise do nothing"""
        try:
            cache_client = caches['default']
            if hasattr(cache_client, 'delete_pattern'):
                cache_client.delete_pattern(pattern)
        except Exception as e:
            # Log this but don't fail the request
            print(f"Cache pattern delete error: {str(e)}")
    
    @staticmethod
    def get(key, default=None):
        """Get from cache safely"""
        try:
            return cache.get(key, default)
        except Exception as e:
            # Log but return default
            print(f"Cache get error: {str(e)}")
            return default
    
    @staticmethod
    def set(key, value, timeout=None):
        """Set cache safely"""
        try:
            cache.set(key, value, timeout=timeout)
        except Exception as e:
            # Log but don't fail
            print(f"Cache set error: {str(e)}")

def is_debug_mode():
    """
    Check if application is running in debug mode
    """
    return settings.DEBUG

def query_cache(ttl=None, prefix="querydata"):
    """
    Cache decorator for database query results
    
    Args:
        ttl: Cache time to live in seconds
        prefix: Cache key prefix
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function name, args and kwargs
            key_parts = [prefix, func.__name__]
            for arg in args:
                if hasattr(arg, 'id'):  # Handle model instances
                    key_parts.append(str(arg.id))
                else:
                    key_parts.append(str(arg))
            
            # Sort kwargs for consistent order
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                if hasattr(v, 'id'):  # Handle model instances
                    key_parts.append(f"{k}:{v.id}")
                else:
                    key_parts.append(f"{k}:{v}")
            
            # Create hash for complex/long keys
            key_str = ":".join(key_parts)
            if len(key_str) > 200:  # If key is too long, hash it
                key_str = hashlib.md5(key_str.encode()).hexdigest()
            
            cache_key = f"qc:{key_str}"
            
            # Try getting from cache first
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # If not in cache, execute function
            result = func(*args, **kwargs)
            
            # Set cache with appropriate TTL
            ttl_value = ttl or getattr(settings, 'CACHE_TTL', 60)
            cache.set(cache_key, result, timeout=ttl_value)
            
            return result
        return wrapper
    return decorator

@query_cache(ttl=60)
def get_user_feed_posts(user, privacy_filter=None, page=1, page_size=10):
    """Get posts for user feed with caching"""
    if privacy_filter is None:
        privacy_filter = models.Q(privacy='public') | models.Q(privacy='private', author=user)
    
    # Get posts based on privacy settings with select_related for author
    posts = Post.objects.select_related('author').filter(privacy_filter).order_by('-created_at')
    
    # Adding annotations for counts
    posts = posts.annotate(
        like_count=models.Count('likes', distinct=True),
        comment_count=models.Count('comments', distinct=True)
    )
    
    # Manual pagination to avoid Django REST pagination which can't be easily cached
    paginator = Paginator(posts, page_size)
    try:
        posts_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        posts_page = paginator.page(1)
    
    return {
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': posts_page.number,
        'results': list(posts_page.object_list),
        'has_next': posts_page.has_next(),
        'has_previous': posts_page.has_previous(),
    }

@query_cache(ttl=60)
def get_user_newsfeed_posts(user, page=1, page_size=10):
    """Get posts for user newsfeed with caching"""
    # Get users that the current user follows
    followed_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
    
    # Get posts from followed users and user's own posts with optimized queries
    feed_posts = Post.objects.select_related('author').filter(
        models.Q(author__in=followed_users) | models.Q(author=user)
    ).order_by('-created_at')
    
    # Add annotated fields for performance
    feed_posts = feed_posts.annotate(
        like_count=models.Count('likes', distinct=True),
        comment_count=models.Count('comments', distinct=True)
    )
    
    # Manual pagination
    paginator = Paginator(feed_posts, page_size)
    try:
        posts_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        posts_page = paginator.page(1)
    
    return {
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': posts_page.number,
        'results': list(posts_page.object_list),
        'has_next': posts_page.has_next(),
        'has_previous': posts_page.has_previous(),
    }

class BatchProcessor:
    """Utility for processing large datasets in batches"""
    
    @staticmethod
    def process_in_batches(queryset, batch_size, processing_func, *args, **kwargs):
        """
        Process a queryset in batches to avoid loading everything into memory
        
        Args:
            queryset: The base queryset to process
            batch_size: Number of objects to process in each batch
            processing_func: Function to call for each batch
            *args, **kwargs: Additional arguments for processing_func
        
        Returns:
            Total processed count
        """
        total_processed = 0
        # Get the primary key name
        pk_name = queryset.model._meta.pk.name
        
        # Start with no offset
        last_pk = None
        
        while True:
            # Clone the queryset to avoid modifying the original
            batch_qs = queryset
            
            if last_pk is not None:
                # Filter queryset to get next batch
                batch_qs = batch_qs.filter(**{f'{pk_name}__gt': last_pk})
            
            # Order by pk to ensure consistent batches
            batch_qs = batch_qs.order_by(pk_name)[:batch_size]
            
            # Materialize the batch
            batch = list(batch_qs)
            
            # If we got an empty batch, we're done
            if not batch:
                break
                
            # Process this batch
            processed = processing_func(batch, *args, **kwargs)
            total_processed += processed
            
            # Get the last PK in this batch
            last_pk = getattr(batch[-1], pk_name)
            
            # Optional: Sleep briefly to avoid database contention
            time.sleep(0.01)
            
        return total_processed