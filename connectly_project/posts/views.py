from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from django.db import models, transaction
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from collections import OrderedDict
from django.core.cache import cache, caches
from django.conf import settings
from django_redis import get_redis_connection
import time
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode
from django.db.models import Q
from .models import Post, Comment, Like, Follow
from users.models import CustomUser
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer
from .permissions import IsOwnerOrReadOnly, IsPostOwnerOrPublic, IsAdminUser
from .utils import is_debug_mode, CacheHelper, get_user_feed_posts, get_user_newsfeed_posts

def replace_query_param(url, key, val):
    """
    Given a URL and a key/val pair, set or replace an item in the query parameters.
    """
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    query_dict = parse_qs(query, keep_blank_values=True)
    query_dict[key] = [val]
    query = urlencode(query_dict, doseq=True)
    return urlunsplit((scheme, netloc, path, query, fragment))

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

class UserListCreate(APIView):
    """
    List all users or create a new user
    """
    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Create a new user account",
        request_body_example={
            "username": "newuser123",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User"
        },
        responses={
            201: UserSerializer,
            400: "Bad Request - Invalid data"
        }
    )
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PostListCreate(APIView):
    """
    List all posts or create a new post
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get(self, request):
        try:
            posts = Post.objects.all()
            
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(posts, request)
            
            serializer = PostSerializer(paginated_posts, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=PostSerializer,
        operation_description="Create a new post",
        request_body_example={
            "content": "This is a sample post content",
            "privacy": "public"
        }
    )
    def post(self, request):
        try:
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                post = serializer.save(author=request.user)
                
                # Get the cache backend
                cache_client = caches['default']
                
                # Check if we're using Redis before attempting Redis-specific methods
                if hasattr(cache_client, 'delete_pattern'):
                    # Redis cache - use pattern deletion
                    cache_client.delete_pattern(CacheHelper.get_key_pattern('feed', request.user.id))
                    cache_client.delete_pattern(CacheHelper.get_key_pattern('newsfeed', request.user.id))
                    
                    # Clear newsfeed caches for all followers
                    followers = Follow.objects.filter(followed=request.user).values_list('follower_id', flat=True)
                    for follower_id in followers:
                        cache_client.delete_pattern(CacheHelper.get_key_pattern('feed', follower_id))
                        cache_client.delete_pattern(CacheHelper.get_key_pattern('newsfeed', follower_id))
                else:
                    # Non-Redis cache - delete specific keys
                    cache.delete(f"feed_{request.user.id}_1_10")
                    cache.delete(f"newsfeed_{request.user.id}_1_10")
                    
                    # For followers, just clear first page
                    followers = Follow.objects.filter(followed=request.user).values_list('follower_id', flat=True)
                    for follower_id in followers:
                        cache.delete(f"feed_{follower_id}_1_10")
                        cache.delete(f"newsfeed_{follower_id}_1_10")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentListCreate(APIView):
    """
    List all comments or create a new comment
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostCommentList(APIView):
    """
    List all comments for a specific post
    """
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

@method_decorator(csrf_exempt, name='dispatch')
class PostCommentCreate(APIView):
    """
    Create a comment on a specific post
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Content of the comment'
                ),
            }
        ),
        operation_description="Create a new comment on a specific post",
        manual_parameters=[
            openapi.Parameter(
                'post_id',
                openapi.IN_PATH,
                description="ID of the post to comment on",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            201: CommentSerializer,
            400: "Bad Request - Invalid data",
            404: "Not Found - Post doesn't exist"
        }
    )
    def post(self, request, post_id, format=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PostLikeCreate(APIView):
    """
    Like or unlike a post
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id, format=None):
        post = get_object_or_404(Post, id=post_id)
        
        # Check if user already liked this post
        existing_like = Like.objects.filter(user=request.user, post=post).first()
        
        if existing_like:
            # Unlike the post
            existing_like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        else:
            # Like the post
            like = Like.objects.create(user=request.user, post=post)
            serializer = LikeSerializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class BulkLikeView(APIView):
    """Process multiple post likes in a single operation"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(auto_schema=None)
    def post(self, request):
        try:
            with transaction.atomic():
                post_ids = request.data.get('post_ids', [])
                action = request.data.get('action', 'like')
                
                if not post_ids:
                    return Response(
                        {"error": "No post_ids provided"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                if len(post_ids) > 100:
                    return Response(
                        {"error": "Maximum 100 posts can be processed in one request"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if action == 'like':
                    existing_likes = Like.objects.filter(
                        user=request.user, 
                        post_id__in=post_ids
                    ).values_list('post_id', flat=True)
                    
                    new_likes = []
                    for post_id in post_ids:
                        if post_id not in existing_likes:
                            new_likes.append(Like(user=request.user, post_id=post_id))
                    
                    if new_likes:
                        Like.objects.bulk_create(new_likes, ignore_conflicts=True)
                    
                    processed = len(new_likes)
                    
                elif action == 'unlike':
                    result = Like.objects.filter(
                        user=request.user, 
                        post_id__in=post_ids
                    ).delete()
                    
                    processed = result[0]
                    
                else:
                    return Response(
                        {"error": "Invalid action. Use 'like' or 'unlike'."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            SafeCacheHelper.delete_pattern(CacheHelper.get_key_pattern('feed', request.user.id))
            
            return Response({
                "status": "success",
                "message": f"{processed} posts {action}d successfully"
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class BulkFollowView(APIView):
    """Process multiple user follows in a single operation"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(auto_schema=None)  # Add this line to hide from Swagger
    @transaction.atomic
    def post(self, request):
        # Get parameters
        user_ids = request.data.get('user_ids', [])
        action = request.data.get('action', 'follow')
        
        if not user_ids:
            return Response(
                {"error": "No user_ids provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Limit batch size for security/performance
        if len(user_ids) > 100:
            return Response(
                {"error": "Maximum 100 users can be processed in one request"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Make sure user doesn't try to follow themselves
        if request.user.id in user_ids:
            return Response(
                {"error": "You cannot follow yourself"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # For follow action
        if action == 'follow':
            # Get existing follows to avoid duplicates
            existing_follows = Follow.objects.filter(
                follower=request.user, 
                followed_id__in=user_ids
            ).values_list('followed_id', flat=True)
            
            # Create follows for users that don't have them yet
            new_follows = []
            for user_id in user_ids:
                if user_id not in existing_follows:
                    new_follows.append(Follow(follower=request.user, followed_id=user_id))
            
            # Bulk create the new follows
            if new_follows:
                Follow.objects.bulk_create(new_follows, ignore_conflicts=True)
            
            processed = len(new_follows)
            
        # For unfollow action
        elif action == 'unfollow':
            # Bulk delete the follows
            result = Follow.objects.filter(
                follower=request.user, 
                followed_id__in=user_ids
            ).delete()
            
            processed = result[0]  # Number of deleted objects
            
        else:
            return Response(
                {"error": "Invalid action. Use 'follow' or 'unfollow'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clear caches that might be affected
        cache_client = caches['default']
        if hasattr(cache_client, 'delete_pattern'):
            cache_client.delete_pattern(CacheHelper.get_key_pattern('newsfeed', request.user.id))
        else:
            cache.delete(f"newsfeed_{request.user.id}_1_10")
        
        return Response({
            "processed": processed,
            "action": action
        })

@method_decorator(csrf_exempt, name='dispatch')
class FollowUserView(APIView):
    """
    Follow or unfollow a user
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id, format=None):
        user_to_follow = get_object_or_404(CustomUser, id=user_id)
        
        if request.user.id == user_id:
            return Response({'error': 'You cannot follow yourself'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already following
        existing_follow = Follow.objects.filter(follower=request.user, followed=user_to_follow).first()
        
        if existing_follow:
            # Unfollow
            existing_follow.delete()
            return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)
        else:
            # Follow
            follow = Follow.objects.create(follower=request.user, followed=user_to_follow)
            serializer = FollowSerializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class NewsFeedView(APIView):
    """
    Retrieve personalized news feed for authenticated user
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get(self, request, format=None):
        # Create a user-specific cache key
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        cache_key = CacheHelper.get_newsfeed_key(request.user.id, page, page_size)
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
            
        user = request.user
        
        # Get users that the current user follows
        followed_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
        
        # Get posts with optimized queries
        feed_posts = Post.objects.select_related('author').filter(
            models.Q(author__in=followed_users) | models.Q(author=user)
        ).order_by('-created_at')
        
        # Add annotated fields for performance - CORRECTED FIELD NAMES
        feed_posts = feed_posts.annotate(
            like_count=models.Count('likes', distinct=True),
            comment_count=models.Count('comments', distinct=True)
        )
        
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(feed_posts, request)
        
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        
        # Get paginated response
        response_data = OrderedDict([
            ('count', paginator.page.paginator.count),
            ('next', paginator.get_next_link()),
            ('previous', paginator.get_previous_link()),
            ('current_page', paginator.page.number),
            ('total_pages', paginator.page.paginator.num_pages),
            ('results', serializer.data)
        ])
        
        # Cache the result
        cache_ttl = getattr(settings, 'CACHE_TTL', 60)
        cache.set(cache_key, response_data, timeout=cache_ttl)
        
        return Response(response_data)

@method_decorator(csrf_exempt, name='dispatch')
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostOwnerOrPublic]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response({"message": "Post deleted successfully."}, 
                       status=status.HTTP_204_NO_CONTENT)

class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        # Use cached query function
        feed_data = get_user_feed_posts(request.user, page=page, page_size=page_size)
        
        # Serialize the results
        serializer = PostSerializer(feed_data['results'], many=True, context={'request': request})
        
        # Build response with pagination info
        response_data = OrderedDict([
            ('count', feed_data['count']),
            ('next', self.get_next_link(feed_data, request)),
            ('previous', self.get_previous_link(feed_data, request)),
            ('current_page', feed_data['current_page']),
            ('total_pages', feed_data['num_pages']),
            ('results', serializer.data)
        ])
        
        return Response(response_data)
    
    def get_next_link(self, feed_data, request):
        if not feed_data['has_next']:
            return None
            
        url = request.build_absolute_uri()
        page = feed_data['current_page'] + 1
        return replace_query_param(url, 'page', page)
        
    def get_previous_link(self, feed_data, request):
        if not feed_data['has_previous']:
            return None
            
        url = request.build_absolute_uri()
        page = feed_data['current_page'] - 1
        return replace_query_param(url, 'page', page)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API Root showing all available endpoints
    """
    return Response({
        'auth': {
            'register': reverse('user-registration', request=request, format=format),
            'login_jwt': reverse('token_obtain_pair', request=request, format=format),
            'login_session': reverse('session-login', request=request, format=format),
            'logout': reverse('user-logout', request=request, format=format),
            'me': reverse('current-user', request=request, format=format),
            'google_login': reverse('google-login', request=request, format=format),
            'token': reverse('api_token_auth', request=request, format=format),
            'jwt_refresh': reverse('token_refresh', request=request, format=format),
        },
        'users': {
            'list': reverse('user-list', request=request, format=format),
            'profile': '/api/auth/{user_id}/',
            'delete': '/api/auth/{user_id}/delete/',
            'followers': '/api/posts/users/{user_id}/followers/',
            'following': '/api/posts/users/{user_id}/following/',
            'follow': '/api/posts/follow/{user_id}/',
        },
        'posts': {
            'list_create': reverse('post-list-create', request=request, format=format),
            'detail': '/api/posts/posts/{post_id}/',
            'update': '/api/posts/posts/{post_id}/update/',
            'delete': '/api/posts/posts/{post_id}/delete/',
            'comments': '/api/posts/posts/{post_id}/comments/',
            'create_comment': '/api/posts/posts/{post_id}/comment/',
            'like': '/api/posts/posts/{post_id}/like/',
            'likes_list': '/api/posts/posts/{post_id}/likes/',
        },
        'comments': {
            'update': '/api/posts/comments/{comment_id}/update/',
            'delete': '/api/posts/comments/{comment_id}/delete/',
        },
        'feeds': {
            'general': reverse('feed', request=request, format=format),
            'personalized': reverse('newsfeed', request=request, format=format),
        },
        'admin': {
            'dashboard': reverse('admin-dashboard', request=request, format=format),
        },
        'protected': reverse('protected-view', request=request, format=format),
        'bulk_operations': {
            'likes': reverse('bulk-likes', request=request, format=format),
            'follows': reverse('bulk-follows', request=request, format=format),
        },
        'docs': {
            'swagger': reverse('schema-swagger-ui', request=request, format=format),
            'redoc': reverse('schema-redoc', request=request, format=format),
        }
    })

@method_decorator(csrf_exempt, name='dispatch')
class PostUpdateView(APIView):
    """
    API endpoint for updating posts
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    @swagger_auto_schema(
        request_body=PostSerializer,
        operation_description="Update a post",
        responses={
            200: PostSerializer,
            400: "Bad request - invalid data",
            403: "Permission denied - not your post",
            404: "Post not found"
        }
    )
    def patch(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(request, post)
        
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CommentUpdateView(APIView):
    """
    API endpoint for updating comments
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    @swagger_auto_schema(
        request_body=CommentSerializer,
        operation_description="Update a comment",
        responses={
            200: CommentSerializer,
            400: "Bad request - invalid data",
            403: "Permission denied - not your comment",
            404: "Comment not found"
        }
    )
    def patch(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        self.check_object_permissions(request, comment)
        
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CommentDeleteView(APIView):
    """
    API endpoint for deleting comments
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    @swagger_auto_schema(
        operation_description="Delete a comment",
        responses={
            204: "Comment deleted successfully",
            403: "Permission denied - not your comment",
            404: "Comment not found"
        }
    )
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        self.check_object_permissions(request, comment)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PostLikesListView(APIView):
    """
    API endpoint for listing likes on a post
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    @swagger_auto_schema(
        operation_description="Get all likes for a post",
        responses={
            200: "List of likes",
            404: "Post not found"
        },
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        likes = Like.objects.filter(post=post).select_related('user')
        
        paginator = self.pagination_class()
        paginated_likes = paginator.paginate_queryset(likes, request)
        
        serializer = LikeSerializer(paginated_likes, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserFollowersView(APIView):
    """
    API endpoint for listing a user's followers
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    @swagger_auto_schema(
        operation_description="Get all followers of a user",
        responses={
            200: "List of followers",
            404: "User not found"
        },
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        followers = Follow.objects.filter(followed=user).select_related('follower')
        
        paginator = self.pagination_class()
        paginated_followers = paginator.paginate_queryset(followers, request)
        
        serializer = FollowSerializer(paginated_followers, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserFollowingView(APIView):
    """
    API endpoint for listing users that a user is following
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    @swagger_auto_schema(
        operation_description="Get all users that a user is following",
        responses={
            200: "List of followed users",
            404: "User not found"
        },
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        following = Follow.objects.filter(follower=user).select_related('followed')
        
        paginator = self.pagination_class()
        paginated_following = paginator.paginate_queryset(following, request)
        
        serializer = FollowSerializer(paginated_following, many=True)
        return paginator.get_paginated_response(serializer.data)

class AdminDashboardView(APIView):
    """
    Admin-only dashboard
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Admin dashboard with system statistics (admin only)",
        responses={
            200: "Dashboard data",
            403: "Permission denied - not an admin"
        }
    )
    def get(self, request):
        # Get system stats
        user_count = CustomUser.objects.count()
        post_count = Post.objects.count()
        comment_count = Comment.objects.count()
        like_count = Like.objects.count()
        
        return Response({
            'user_count': user_count,
            'post_count': post_count,
            'comment_count': comment_count,
            'like_count': like_count,
            'admin_name': request.user.username
        })

class ProtectedView(APIView):
    """
    Example of a protected endpoint
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Protected endpoint requiring authentication",
        responses={
            200: "Access granted",
            401: "Authentication credentials not provided"
        }
    )
    def get(self, request):
        return Response({
            'message': 'This is a protected endpoint',
            'user': request.user.username
        })

