from django.contrib import admin
from django.urls import path, include
from .views import UserListCreate, PostListCreate, CommentListCreate

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
]