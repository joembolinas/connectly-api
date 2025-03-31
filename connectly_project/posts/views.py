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
from django.db import models
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Post, Comment, Like, Follow
from users.models import CustomUser
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer
from .permissions import IsOwnerOrReadOnly, IsPostOwnerOrPublic, IsAdminUser

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserListCreate(APIView):
    """
    List all users or create a new user
    """
    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
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
    
    def get(self, request, format=None):
        posts = Post.objects.all().order_by('-created_at')
        
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
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
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        
        paginator = self.pagination_class()
        paginated_comments = paginator.paginate_queryset(comments, request)
        
        serializer = CommentSerializer(paginated_comments, many=True)
        return paginator.get_paginated_response(serializer.data)

class PostCommentCreate(APIView):
    """
    Create a comment on a specific post
    """
    permission_classes = [IsAuthenticated]
    
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
        user = request.user
        
        # Get users that the current user follows
        followed_users = Follow.objects.filter(follower=user).values_list('followed', flat=True)
        
        # Get posts from followed users and user's own posts
        feed_posts = Post.objects.filter(
            models.Q(author__in=followed_users) | models.Q(author=user)
        ).order_by('-created_at')
        
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(feed_posts, request)
        
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        # Check if the user is an admin
        if not request.user.role == 'admin':
            raise PermissionDenied("You do not have permission to delete this post.")

        post.delete()
        return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        # Enforce privacy settings
        if post.privacy == 'private' and post.author != request.user:
            raise PermissionDenied("You do not have permission to view this post.")

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve posts based on privacy settings
        posts = Post.objects.filter(
            models.Q(privacy='public') |
            models.Q(privacy='private', author=request.user)
        )

        return Response([{"id": post.id, "content": post.content, "privacy": post.privacy} for post in posts], status=status.HTTP_200_OK)

