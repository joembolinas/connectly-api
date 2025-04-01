from django.urls import path
from .views import (
    UserListCreate, PostListCreate, CommentListCreate,
    PostCommentList, PostLikeCreate, PostCommentCreate,
    FeedView, FollowUserView, PostDetailView, PostDeleteView, NewsFeedView, api_root
)

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