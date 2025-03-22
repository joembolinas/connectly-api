from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from users.models import CustomUser  # Import CustomUser from users app

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
    content = models.TextField()  # The text content of the post
    author = models.ForeignKey(CustomUser, related_name='posts', on_delete=models.CASCADE)  # The user who created the post
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the post was created

    class Meta:
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

class Comment(models.Model):
    text = models.TextField()  # The text content of the comment
    author = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)  # The user who created the comment
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)  # The post the comment is related to
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)  # The parent comment for replies
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the comment was created
    
    class Meta:
        unique_together = ['author', 'post', 'text']

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

    def clean(self):
        if self.parent_comment and self.parent_comment.post != self.post:
            raise ValidationError("Parent comment must belong to the same post.")
        if self.parent_comment == self:
            raise ValidationError("A comment cannot be a reply to itself.")

class Like(models.Model):
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        
    def __str__(self):
        return f"Like by {self.user.username} on Post {self.post.id}"

class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")
