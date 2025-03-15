from rest_framework import serializers
from .models import User, Post, Comment, Like, Follow
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'date_joined']  # Use date_joined instead of created_at
        
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        
    def validate(self, data):
        # Check if the user has already liked the post
        if Like.objects.filter(user=data['user'], post=data['post']).exists():
            raise serializers.ValidationError("You have already liked this post.")
        return data

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'parent_comment', 'created_at', 'replies']

    def get_replies(self, obj):
        replies = Comment.objects.filter(parent_comment=obj)
        return CommentSerializer(replies, many=True).data

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

class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'like_count', 'comment_count', 'is_liked']
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_is_liked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return Like.objects.filter(user=user, post=obj).exists()
        return False

# Add Follow serializer
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        
    def validate(self, data):
        # Check if the user is trying to follow themselves
        if data['follower'] == data['following']:
            raise serializers.ValidationError("You cannot follow yourself.")
            
        # Check if the user is already following this user
        if Follow.objects.filter(follower=data['follower'], following=data['following']).exists():
            raise serializers.ValidationError("You are already following this user.")
            
        return data