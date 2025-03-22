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
from .permissions import IsAdminUser, IsRegularUser, IsModeratorUser, IsOwnerOrReadOnly, IsPostOwnerOrPublic
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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get(self, request):
        # Admin/moderators see all posts
        if request.user.role in ['admin', 'moderator'] or request.user.is_superuser:
            posts = Post.objects.all()
        else:
            # Regular users see public posts and their own private posts
            posts = Post.objects.filter(
                Q(privacy='public') | 
                Q(author=request.user) |
                Q(privacy='followers', author__in=Follow.objects.filter(follower=request.user).values_list('following', flat=True))
            )
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetail(APIView):
    permission_classes = [IsAuthenticated, IsPostOwnerOrPublic]
    
    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)
    
    def get(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk):
        post = self.get_object(pk)
        # Only post owner can edit
        if post.author != request.user:
            return Response({"detail": "Not authorized to edit this post"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        post = self.get_object(pk)
        # Admin, moderator, or post owner can delete
        if request.user.role in ['admin', 'moderator'] or post.author == request.user or request.user.is_superuser:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not authorized to delete this post"}, status=status.HTTP_403_FORBIDDEN)

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
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        return Response({"message": "Hello, admin!"})

class ModeratorView(APIView):
    permission_classes = [IsAuthenticated, IsModeratorUser]
    
    def get(self, request):
        return Response({"message": "Hello, moderator or admin!"})

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
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get all users that the current user follows
        following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        
        # Get posts based on privacy settings:
        # 1. Public posts from followed users
        # 2. Followers-only posts from followed users
        # 3. User's own posts
        feed_posts = Post.objects.filter(
            (Q(privacy='public') & Q(author__in=following_users)) |
            (Q(privacy='followers') & Q(author__in=following_users)) |
            Q(author=request.user)
        ).order_by('-created_at')
        
        serializer = PostSerializer(feed_posts, many=True)
        return Response(serializer.data)

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
