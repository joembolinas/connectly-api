from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from users.models import CustomUser  # Import CustomUser from users app

User = CustomUser  # Use this alias if you want to keep using 'User' in your code

class CustomUser(AbstractUser):  # This is correct capitalization
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    # Add these related_name parameters to resolve the conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Changed from user_set
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Changed from user_set
        related_query_name='custom_user',
    )

class Post(models.Model):
    """
    Model representing a user post in the social network.
    
    Attributes:
        author (ForeignKey): The user who created the post
        content (TextField): The content of the post
        created_at (DateTimeField): When the post was created
        updated_at (DateTimeField): When the post was last updated
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """Return a string representation of the post"""
        return f"Post by {self.author.username}: {self.content[:50]}"
    
    def clean(self):
        """Validate the post data"""
        if not self.content or self.content.isspace():
            raise ValidationError("Post content cannot be empty.")
        
        if len(self.content) > 5000:
            raise ValidationError("Post content cannot exceed 5000 characters.")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation is called"""
        self.clean()
        super().save(*args, **kwargs)


class Comment(models.Model):
    """
    Model representing a comment on a post.
    
    Attributes:
        post (ForeignKey): The post being commented on
        author (ForeignKey): The user who created the comment
        content (TextField): The content of the comment
        parent (ForeignKey): Parent comment if this is a reply
        created_at (DateTimeField): When the comment was created
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """Return a string representation of the comment"""
        return f"Comment by {self.author.username} on {self.post}"
    
    def clean(self):
        """Validate the comment data"""
        if not self.content or self.content.isspace():
            raise ValidationError("Comment content cannot be empty.")
        
        if len(self.content) > 1000:
            raise ValidationError("Comment content cannot exceed 1000 characters.")
        
        # Prevent deep nesting of comments (more than 2 levels)
        if self.parent and self.parent.parent:
            raise ValidationError("Comments can only be nested up to 2 levels deep.")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation is called"""
        self.clean()
        super().save(*args, **kwargs)


class Like(models.Model):
    """
    Model representing a like on a post.
    
    Attributes:
        post (ForeignKey): The post being liked
        user (ForeignKey): The user who created the like
        created_at (DateTimeField): When the like was created
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for the Like model"""
        unique_together = ('post', 'user')  # A user can only like a post once
    
    def __str__(self):
        """Return a string representation of the like"""
        return f"Like by {self.user.username} on {self.post}"
    
    def clean(self):
        """Validate the like data"""
        # Check if the user has already liked this post
        if Like.objects.filter(post=self.post, user=self.user).exists() and not self.pk:
            raise ValidationError("You have already liked this post.")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation is called"""
        self.clean()
        super().save(*args, **kwargs)


class Follow(models.Model):
    """
    Model representing a follow relationship between users.
    
    Attributes:
        follower (ForeignKey): The user who is following
        following (ForeignKey): The user being followed
        created_at (DateTimeField): When the follow relationship was created
    """
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for the Follow model"""
        unique_together = ('follower', 'following')  # A user can only follow another user once
    
    def __str__(self):
        """Return a string representation of the follow relationship"""
        return f"{self.follower.username} follows {self.following.username}"
    
    def clean(self):
        """Validate the follow data"""
        # Prevent self-following
        if self.follower == self.following:
            raise ValidationError("You cannot follow yourself.")
        
        # Check if the follow relationship already exists
        if Follow.objects.filter(follower=self.follower, following=self.following).exists() and not self.pk:
            raise ValidationError("You are already following this user.")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation is called"""
        self.clean()
        super().save(*args, **kwargs)
