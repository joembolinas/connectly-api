from rest_framework import serializers
from .models import Post, Comment, Like, Follow
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['role']
        
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        return value
    
    def validate_email(self, value):
        if not value.endswith(('.com', '.org', '.net', '.edu')):
            raise serializers.ValidationError("Email must end with a valid domain")
        return value

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']
        
    def validate(self, data):
        # Check if the user has already liked this post
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if Like.objects.filter(user=user, post=data['post']).exists():
                raise serializers.ValidationError("You have already liked this post")
        return data

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'content', 'post', 'author', 'author_username', 'parent', 'created_at', 'replies']
        read_only_fields = ['author', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post does not exist")
        return value

    def validate_author(self, value):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return request.user
        raise serializers.ValidationError("Author must be authenticated")

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'author_username', 'created_at', 'privacy', 'like_count', 'comment_count']
        read_only_fields = ['author', 'created_at']
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.ReadOnlyField(source='follower.username')
    followed_username = serializers.ReadOnlyField(source='followed.username')
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'follower_username', 'followed', 'followed_username', 'created_at']
        read_only_fields = ['follower', 'created_at']
        
    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Set follower to current user
            data['follower'] = request.user
            # Check if already following
            if Follow.objects.filter(follower=request.user, followed=data['followed']).exists():
                raise serializers.ValidationError("You are already following this user")
            # Prevent self-following
            if data['follower'] == data['followed']:
                raise serializers.ValidationError("You cannot follow yourself")
        return data