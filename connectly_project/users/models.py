from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'Regular User'),
        ('guest', 'Guest User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_moderator(self):
        return self.role == 'moderator'
