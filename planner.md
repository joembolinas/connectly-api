Enhancing the Connectly API with Validation and Relationships
Overview
This documentation provides a detailed overview of the enhancements made to the Connectly API, focusing on validation logic, relational data integrity, and improved response handling. The Connectly API is designed to support a social media platform with features such as user management, posts, and nested comments.
Table of Contents
Models
Serializers
Views
URLs
Settings
Testing
Conclusion

Models
User Model
The User model represents a user in the system.


Python








from django.db import models
class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username


Post Model
The Post model represents a post created by a user.


Python








class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


Comment Model
The Comment model supports nested comments with a parent_comment field.


Python








class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['author', 'post', 'text']
    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
    def clean(self):
        if self.parent_comment and self.parent_comment.post != self.post:
            raise ValidationError("Parent comment must belong to the same post.")
        if self.parent_comment == self:
            raise ValidationError("A comment cannot be a reply to itself.")


Serializers
UserSerializer
The UserSerializer handles serialization and validation for the User model.


Python








from rest_framework import serializers
from .models import User, Post, Comment
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


PostSerializer
The PostSerializer handles serialization and validation for the Post model.


Python








class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'comments']
    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value


CommentSerializer
The CommentSerializer handles serialization and validation for the Comment model, including nested replies.


Python








class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'parent_comment', 'created_at', 'replies']
    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value
    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
    def validate_parent_comment(self, value):
        if value and value.post_id != self.initial_data.get('post'):
            raise serializers.ValidationError("Parent comment must belong to the same post.")
        return value
    def get_replies(self, obj):
        replies = Comment.objects.filter(parent_comment=obj)
        return CommentSerializer(replies, many=True).data


Views
UserListCreate
Handles the creation and listing of users.


Python








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
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


PostListCreate
Handles the creation and listing of posts.


Python








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


CommentListCreate
Handles the creation and listing of comments, including nested replies.


Python








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


URLs
URL Configuration
The URL configuration includes paths for the admin interface and the API endpoints.


Python








from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('posts.urls')),
]


Posts URLs
The posts app URL configuration includes paths for users, posts, and comments.


Python








from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate
urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
]


Settings
REST Framework Configuration
Enable pagination for large datasets.


Python








REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}


Testing
Test Cases
Document comprehensive test cases for nested comments and edge cases.
EndpointMethodInputExpected Output/api/comments/





POST





{ "text": "Top-level comment", "author": 1, "post": 1 }





{"id": 1, "message": "Comment created successfully"}





/api/comments/





POST





{ "text": "Reply", "author": 1, "post": 1, "parent_comment": 1 }





{"id": 2, "message": "Comment created successfully"}





/api/comments/





POST





{ "text": "Invalid reply", "author": 1, "post": 2, "parent_comment": 1 }





{"error": "Parent comment must belong to the same post."}






Testing with Postman
Test the following endpoints using Postman:
Retrieve All Users (GET /api/users/)
Create a User (POST /api/users/)
Retrieve All Posts (GET /api/posts/)
Create a Post (POST /api/posts/)
Retrieve All Comments (GET /api/comments/)
Create a Comment (POST /api/comments/)

Conclusion
The enhancements made to the Connectly API include validation logic, relational data integrity, and improved response handling. These changes support nested comments, ensure data integrity, and provide a robust API for a social media platform. By following the recommendations and testing the endpoints, the Connectly API is now ready for further enhancements, including security and design patterns.
Let me know if you need further assistance!
Similar code found with 1 license type


