import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
#from ratelimit.decorators import ratelimit
from .models import Post, Comment, Like, Follow
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from .permissions import IsAdminUser, IsRegularUser
from posts.factory import PostFactory
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import CacheHelper

User = get_user_model()

def get_users(request):
    try:
        users = list(User.objects.values('id', 'username', 'email', 'created_at'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_posts(request):
    try:
        posts = list(Post.objects.values('id', 'content', 'author', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create(username=data['username'], email=data['email'])
            return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            author = User.objects.get(id=data['author'])
            post = Post.objects.create(content=data['content'], author=author)
            return JsonResponse({'id': post.id, 'message': 'Post created successfully'}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListCreate(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all posts",
        responses={200: PostSerializer(many=True)}
    )
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new post",
        request_body=PostSerializer,
        responses={
            201: PostSerializer,
            400: "Bad request"
        }
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostCommentList(APIView):
    pagination_class = CommentPagination
    
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post, parent_comment=None)  # Only top-level comments
        
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class PostLikeCreate(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Like a post",
        responses={
            201: "Like created",
            400: "Already liked",
            404: "Post not found"
        }
    )
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({"detail": "Already liked"}, status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user=request.user, post=post)
        return Response({"detail": "Like created"}, status=status.HTTP_201_CREATED)

class PostCommentCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"message": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CommentSerializer(data={
            'text': request.data.get('text'),
            'author': request.user.id,
            'post': post.id,
            'parent_comment': request.data.get('parent_comment')
        })
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'id': serializer.data['id'],
                'message': "Comment added successfully."
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "Admin-only content"})

class UserView(APIView):
    permission_classes = [IsRegularUser]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        return Response({"message": "User-specific content"})

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})

#@ratelimit(key='user', rate='5/m', block=True)
#def my_view(request):
#    return Response({"message": "Rate-limited view"})

class CreatePostView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        content = request.data.get('content')
        post = PostFactory.create_post(request.user, content)
        return Response({"id": post.id, "message": "Post created successfully"})

# News Feed API
class NewsFeedView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Create a cache key based on user ID and last update time of posts
        cache_key = CacheHelper.get_key(
            'feed', 
            user.id,
            Post.objects.filter(
                author__in=Follow.objects.filter(follower=user).values('following')
            ).order_by('-created_at').first().created_at if Post.objects.filter(
                author__in=Follow.objects.filter(follower=user).values('following')
            ).exists() else 'empty'
        )
        
        # Get or set the feed in cache
        def get_feed():
            # Get posts from users that the current user follows
            following_users = Follow.objects.filter(follower=user).values('following')
            posts = Post.objects.filter(
                author__in=following_users
            ).select_related('author').prefetch_related('comments', 'likes').order_by('-created_at')[:50]
            
            return PostSerializer(posts, many=True, context={'request': request}).data
        
        feed_data = CacheHelper.get_or_set(cache_key, get_feed)
        
        return Response(feed_data)

# Add Follow view
class FollowUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response(
                {"message": "You cannot follow yourself."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            return Response(
                {"message": f"You are now following {user_to_follow.username}"}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": f"You are already following {user_to_follow.username}"}, 
                status=status.HTTP_200_OK
            )
    
    def delete(self, request, user_id):
        try:
            user_to_unfollow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            follow = Follow.objects.get(
                follower=request.user, 
                following=user_to_unfollow
            )
            follow.delete()
            return Response(
                {"message": f"You have unfollowed {user_to_unfollow.username}"}, 
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {"message": "You are not following this user."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
