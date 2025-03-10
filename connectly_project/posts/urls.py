from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    UserListCreate, PostListCreate, CommentListCreate,
    PostCommentList, PostLikeCreate, PostCommentCreate,
    NewsFeedView, AdminOnlyView, UserView, ProtectedView,
    CreatePostView, FollowUserView
)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list-create', request=request, format=format),
        'posts': reverse('post-list-create', request=request, format=format),
        'comments': reverse('comment-list-create', request=request, format=format),
        'feed': reverse('news-feed', request=request, format=format),
    })

urlpatterns = [
    path('', api_root, name='api-root'),
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