from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    UserListCreate, PostListCreate, CommentListCreate,  # Include CommentListCreate here
    PostCommentList, PostLikeCreate, PostCommentCreate,
    NewsFeedView, FollowUserView, PostDetailView, PostDeleteView
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
    path('posts/<int:post_id>/comment/', PostCommentCreate.as_view(), name='post-comment-create'),
    path('posts/<int:post_id>/like/', PostLikeCreate.as_view(), name='post-like-create'),
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
    path('users/<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'),
]