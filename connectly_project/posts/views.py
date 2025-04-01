from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from django.db import models
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from collections import OrderedDict
from django.core.cache import cache
from django.conf import settings
from .models import Post, Comment, Like, Follow
from users.models import CustomUser
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer
from .permissions import IsOwnerOrReadOnly, IsPostOwnerOrPublic, IsAdminUser
from .utils import is_debug_mode, CacheHelper

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

class PostListCreate(APIView):
    """
    List all posts or create a new post
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    def get(self, request):
        posts = Post.objects.all()
        
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=PostSerializer,
        operation_description="Create a new post",
        request_body_example={
            "content": "This is a sample post content",
            "privacy": "public"
        }
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            
            # Invalidate feed caches when new post is created
            # Clear the user's own feed and newsfeed caches
            # Replace cache.delete_pattern with individual deletes
            cache.delete(f"feed:user-{request.user.id}:page-1:size-10")
            cache.delete(f"newsfeed:user-{request.user.id}:page-1:size-10")
            
            # Clear newsfeed caches for all followers
            followers = Follow.objects.filter(followed=request.user).values_list('follower_id', flat=True)
            for follower_id in followers:
                cache.delete(f"feed:user-{follower_id}:page-1:size-10")
                cache.delete(f"newsfeed:user-{follower_id}:page-1:size-10")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@method_decorator(csrf_protect, name='dispatch')
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostOwnerOrPublic]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

@method_decorator(csrf_protect, name='dispatch')
class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response({"message": "Post deleted successfully."}, 
                       status=status.HTTP_204_NO_CONTENT)

class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get(self, request):
        # Create a user-specific cache key
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        cache_key = CacheHelper.get_feed_key(request.user.id, page, page_size)
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Get posts based on privacy settings with select_related for author
        posts = Post.objects.select_related('author').filter(
            models.Q(privacy='public') |
            models.Q(privacy='private', author=request.user)
        ).order_by('-created_at')
        
        # Adding annotations for counts - CORRECTED FIELD NAMES
        posts = posts.annotate(
            like_count=models.Count('likes', distinct=True),
            comment_count=models.Count('comments', distinct=True)
        )
        
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True)
        
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

@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root showing all available endpoints
    """
    return Response({
        'auth': {
            'register': reverse('user-registration', request=request, format=format),
            'google-login': reverse('google-login', request=request, format=format),
            'token': reverse('api_token_auth', request=request, format=format),
            'jwt': reverse('token_obtain_pair', request=request, format=format),
            'jwt-refresh': reverse('token_refresh', request=request, format=format),
        },
        'posts': {
            'list': reverse('post-list-create', request=request, format=format),
            'feed': reverse('feed', request=request, format=format),
            'newsfeed': reverse('newsfeed', request=request, format=format),
        },
        'users': {
            'list': reverse('user-list-create', request=request, format=format),
        },
        'docs': {
            'swagger': reverse('schema-swagger-ui', request=request, format=format),
            'redoc': reverse('schema-redoc', request=request, format=format),
        }
    })

