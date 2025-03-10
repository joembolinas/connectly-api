from django.urls import path
from .views import (
    UserListCreate, PostListCreate, CommentListCreate,
    PostCommentList, PostLikeCreate, PostCommentCreate,
    NewsFeedView, AdminOnlyView, UserView, ProtectedView,
    CreatePostView, FollowUserView
)

urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('posts/<int:post_id>/comments/', PostCommentList.as_view(), name='post-comment-list'),
    path('posts/<int:post_id>/like/', PostLikeCreate.as_view(), name='post-like-create'),
    path('posts/<int:post_id>/comment/', PostCommentCreate.as_view(), name='post-comment-create'),
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('user-view/', UserView.as_view(), name='user-view'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('create-post/', CreatePostView.as_view(), name='create-post'),
    path('users/<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
]