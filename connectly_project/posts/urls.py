from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    UserListCreate, PostListCreate, CommentListCreate,
    PostCommentList, PostLikeCreate, PostCommentCreate,
    NewsFeedView, FollowUserView, PostDetailView, PostDeleteView, FeedView
)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list-create', request=request, format=format),
        'posts': reverse('post-list-create', request=request, format=format),
        'comments': reverse('comment-list-create', request=request, format=format),
        'feed': reverse('feed', request=request, format=format),
        'newsfeed': reverse('newsfeed', request=request, format=format),
    })

urlpatterns = [
    # User endpoints
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    
    # Post endpoints
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'),
    
    # Comment endpoints
    path('posts/<int:post_id>/comments/', PostCommentList.as_view(), name='post-comments'),
    path('posts/<int:post_id>/comment/', PostCommentCreate.as_view(), name='post-comment-create'),
    
    # Like endpoints
    path('posts/<int:post_id>/like/', PostLikeCreate.as_view(), name='post-like'),
    
    # Feed endpoints
    path('feed/', FeedView.as_view(), name='feed'),
    path('newsfeed/', NewsFeedView.as_view(), name='newsfeed'),
    
    # Follow endpoints
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
]