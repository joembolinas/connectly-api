from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'Regular User'),
        ('guest', 'Guest User'),
    )

    name = models.CharField(max_length=255, default="No name")
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
