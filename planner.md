
# Performance Optimization Plan for Connectly API

Based on your project setup and requirements, let's create a comprehensive plan to optimize your API's performance. I'll focus on three key areas: pagination, caching, and query optimization.

## 1. Pagination Enhancements

I see you've already implemented a `StandardResultsPagination` class, but let's enhance it and apply it consistently to all list endpoints.

### Update `StandardResultsPagination` Class

```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
  
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))
```

### Apply Pagination to All List Views

Ensure all list endpoints use pagination by setting it in each list view:

```python
class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get(self, request):
        # Get posts based on privacy settings
        posts = Post.objects.filter(
            models.Q(privacy='public') |
            models.Q(privacy='private', author=request.user)
        ).order_by('-created_at')
      
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)
```

## 2. Caching Implementation

Your project already has Redis configured in the settings. Let's implement caching for frequently accessed endpoints.

### Update Key Endpoints with Caching

```python
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from posts.utils import CacheHelper

class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get(self, request):
        # Create a user-specific cache key
        cache_key = CacheHelper.get_key('feed', request.user.id, 
                                      request.query_params.get('page', 1),
                                      request.query_params.get('page_size', 10))
      
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
      
        # If not in cache, generate the feed
        posts = Post.objects.filter(
            models.Q(privacy='public') |
            models.Q(privacy='private', author=request.user)
        ).order_by('-created_at')
      
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True)
      
        # Get the paginated response data
        response_data = OrderedDict([
            ('count', paginator.page.paginator.count),
            ('next', paginator.get_next_link()),
            ('previous', paginator.get_previous_link()),
            ('current_page', paginator.page.number),
            ('total_pages', paginator.page.paginator.num_pages),
            ('results', serializer.data)
        ])
      
        # Cache the result (15 minutes by default)
        cache.set(cache_key, response_data, timeout=settings.CACHE_TTL)
      
        return Response(response_data)
```

### Create Cache Invalidation Logic

When new posts are created or existing ones are modified, we need to invalidate related caches:

```python
# Add to PostListCreate
def post(self, request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        post = serializer.save(author=request.user)
      
        # Invalidate feed caches for relevant users
        # Get all followers of the user
        followers = Follow.objects.filter(followed=request.user).values_list('follower_id', flat=True)
      
        # Invalidate cache for the author and all followers
        cache.delete(CacheHelper.get_key('feed', request.user.id))
        cache.delete(CacheHelper.get_key('newsfeed', request.user.id))
      
        for follower_id in followers:
            cache.delete(CacheHelper.get_key('feed', follower_id))
            cache.delete(CacheHelper.get_key('newsfeed', follower_id))
      
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

## 3. Query Optimization with select_related and prefetch_related

To reduce database queries, let's optimize data retrieval by pre-loading related data.

### Optimize Post Queries with Author Information

```python
class FeedView(APIView):
    # ...existing code...

    def get(self, request):
        # Use select_related to prefetch author data
        posts = Post.objects.select_related('author').filter(
            models.Q(privacy='public') |
            models.Q(privacy='private', author=request.user)
        ).order_by('-created_at')
      
        # ...rest of the method...
```

### Optimize Comment Queries with Author and Post Data

```python
class PostCommentList(APIView):
    pagination_class = StandardResultsPagination
  
    def get(self, request, post_id, format=None):
        post = get_object_or_404(Post, id=post_id)
      
        # Use select_related to prefetch author data
        comments = Comment.objects.select_related('author', 'post').filter(
            post=post
        ).order_by('-created_at')
      
        paginator = self.pagination_class()
        paginated_comments = paginator.paginate_queryset(comments, request)
      
        serializer = CommentSerializer(paginated_comments, many=True)
        return paginator.get_paginated_response(serializer.data)
```

### Optimize News Feed with prefetch_related for Likes and Comments Count

```python
class NewsFeedView(APIView):
    # ...existing code...
  
    def get(self, request, format=None):
        user = request.user
      
        # Get users that the current user follows
        followed_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
      
        # Get posts from followed users and user's own posts with optimized queries
        feed_posts = Post.objects.select_related('author').prefetch_related(
            'likes', 'comments'
        ).filter(
            models.Q(author__in=followed_users) | models.Q(author=user)
        ).order_by('-created_at')
      
        # Add annotated fields for performance
        feed_posts = feed_posts.annotate(
            like_count=models.Count('likes', distinct=True),
            comment_count=models.Count('comments', distinct=True)
        )
      
        # ...rest of the method...
```

## 4. Performance Monitoring Implementation

Let's add a simple timing middleware to monitor endpoint performance:

```python
# posts/middleware.py (add this to your existing file)
import time
import logging

logger = logging.getLogger('api.performance')

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer
        start_time = time.time()
      
        # Process the request
        response = self.get_response(request)
      
        # Calculate request duration
        duration = time.time() - start_time
      
        # Log slow requests (over 0.5 seconds)
        if duration > 0.5:
            logger.warning(
                f'Slow API request: {request.method} {request.path} took {duration:.2f}s'
            )
      
        # Add timing header to all API responses
        if request.path.startswith('/api/'):
            response['X-Request-Duration'] = f"{duration:.2f}s"
      
        return response
```

Add this middleware to your settings:

```python
MIDDLEWARE = [
    # ...existing middleware...
    'posts.middleware.PerformanceMiddleware',
]
```

## 5. Database Indexing for Better Performance

Let's ensure your models have appropriate indexes:

```python
# posts/models.py (add to your existing models)

class Post(models.Model):
    # ...existing fields...
  
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
            models.Index(fields=['privacy']),
        ]

class Comment(models.Model):
    # ...existing fields...
  
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]

class Like(models.Model):
    # ...existing fields...
  
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]

class Follow(models.Model):
    # ...existing fields...
  
    class Meta:
        unique_together = ('follower', 'followed')
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['followed']),
        ]
```

Create and apply migrations for these index changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Testing Plan

### Pagination Testing

1. Test pagination with different page sizes:

   ```bash
   # Test with default page size
   curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/posts/feed/

   # Test with custom page size
   curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/posts/feed/?page_size=5

   # Test second page
   curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/posts/feed/?page=2
   ```
2. Validate pagination metadata:

   - Verify the response includes:
     - `count` (total items)
     - `next` and `previous` links
     - `current_page` and `total_pages`
     - Correct number of results

### Cache Testing

1. Test cache hits and misses:

   ```bash
   # First request (cache miss)
   time curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/posts/feed/

   # Second request (cache hit)
   time curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/posts/feed/
   ```
2. Validate cache invalidation:

   - Create a new post
   - Verify the feed cache is invalidated
   - Make a fresh request and check timing
3. Monitor Redis cache with:

   ```bash
   redis-cli monitor
   ```

### Query Optimization Testing

1. Monitor SQL queries during requests:

   - Install Django Debug Toolbar for development
   - Check number of queries before and after optimization
2. Test query performance with different dataset sizes

## Summary

By implementing these optimizations, your Connectly API will be significantly more scalable and performant:

1. **Pagination** ensures that large datasets are handled efficiently
2. **Caching** reduces database load for frequently accessed endpoints
3. **Query optimization** minimizes database roundtrips
4. **Performance monitoring** helps identify bottlenecks
5. **Database indexing** speeds up common queries

These changes will ensure your API can handle more users and data without performance degradation.

Similar code found with 1 license type
