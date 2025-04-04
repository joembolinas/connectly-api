from django.urls import path
from .views import (
    UserListCreate, PostListCreate, CommentListCreate,
    PostCommentList, PostLikeCreate, PostCommentCreate,
    FeedView, FollowUserView, PostDetailView, PostDeleteView, NewsFeedView,
    BulkLikeView, BulkFollowView, PostUpdateView, CommentUpdateView, CommentDeleteView,
    PostLikesListView, UserFollowersView, UserFollowingView, AdminDashboardView, ProtectedView
)

urlpatterns = [
    # Existing endpoints
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('posts/<int:post_id>/comments/', PostCommentList.as_view(), name='post-comments'),
    path('posts/<int:post_id>/comment/', PostCommentCreate.as_view(), name='post-comment-create'),
    path('posts/<int:post_id>/like/', PostLikeCreate.as_view(), name='post-like'),
    path('feed/', FeedView.as_view(), name='feed'),
    path('newsfeed/', NewsFeedView.as_view(), name='newsfeed'),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('bulk/likes/', BulkLikeView.as_view(), name='bulk-likes'),
    path('bulk/follows/', BulkFollowView.as_view(), name='bulk-follows'),
    
    # New endpoints
    path('posts/<int:post_id>/update/', PostUpdateView.as_view(), name='post-update'),
    path('comments/<int:comment_id>/update/', CommentUpdateView.as_view(), name='comment-update'),
    path('comments/<int:comment_id>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('posts/<int:post_id>/likes/', PostLikesListView.as_view(), name='post-likes-list'),
    path('users/<int:user_id>/followers/', UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', UserFollowingView.as_view(), name='user-following'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
]