from rest_framework import serializers
from .models import Post, Comment, Like, Follow
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'role']
        read_only_fields = ['role']
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        return value
    
    def validate_email(self, value):
        if not value.endswith(('.com', '.org', '.net', '.edu')):
            raise serializers.ValidationError("Email must end with a valid domain")
        return value
    
    def create(self, validated_data):
        # Extract password from validated_data
        password = validated_data.pop('password', None)
        
        # Create the user instance
        user = CustomUser.objects.create(**validated_data)
        
        # Set the password if provided
        if password:
            user.set_password(password)
            user.save()
            
        return user

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
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_username', 'post', 'created_at']
        read_only_fields = ['author', 'author_username', 'post', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Post
        fields = ['id', 'content', 'created_at', 'author', 'author_username', 'privacy']
        read_only_fields = ['author', 'author_username', 'created_at']

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