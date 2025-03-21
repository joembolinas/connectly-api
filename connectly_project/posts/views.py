import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
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
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"message": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user has already liked the post
        like_exists = Like.objects.filter(user=request.user, post=post).exists()
        
        if like_exists:
            # Unlike the post by deleting the like
            Like.objects.filter(user=request.user, post=post).delete()
            return Response({"message": "Post unliked successfully."}, status=status.HTTP_200_OK)
        else:
            # Like the post
            like = Like.objects.create(user=request.user, post=post)
            return Response({"message": "Post liked successfully."}, status=status.HTTP_201_CREATED)

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
        cache_key = f"user_feed_{request.user.id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following', flat=True)
        
        # Optimized query
        posts = Post.objects.filter(
            Q(author__in=following_ids) | Q(author=request.user)
        ).select_related('author').prefetch_related('comments', 'likes').order_by('-created_at')
        
        # Add pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(posts, request)
        
        # Serialize posts with context to determine if the user liked them
        serializer = PostSerializer(
            result_page, 
            many=True, 
            context={'request': request}
        )
        
        response_data = paginator.get_paginated_response(serializer.data).data
        cache.set(cache_key, response_data, 300)  # Cache for 5 minutes

        return Response(response_data)

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
