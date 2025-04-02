from django.test import TestCase
from rest_framework.test import APIClient
from django.middleware.csrf import get_token
from .models import Post, Like, Comment, Follow
from users.models import CustomUser
from django.urls import reverse

class PostPrivacyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="user", 
            password="password", 
            role="user"
        )
        self.admin = CustomUser.objects.create_user(
            username="admin", 
            password="password", 
            role="admin"
        )
        self.private_post = Post.objects.create(
            author=self.user, 
            content="Private Post", 
            privacy="private"
        )
        self.public_post = Post.objects.create(
            author=self.user, 
            content="Public Post", 
            privacy="public"
        )
        
        # DRF tests don't need CSRF tokens when using force_authenticate
        # Django test client handles this internally

    def test_private_post_access(self):
        # Test admin cannot view private posts of others
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/posts/posts/{self.private_post.id}/")
        self.assertEqual(response.status_code, 403)
        
        # Test owner can view private posts
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/posts/posts/{self.private_post.id}/")
        self.assertEqual(response.status_code, 200)
    
    def test_public_post_access(self):
        # Test public posts are accessible to all
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/posts/posts/{self.public_post.id}/")
        self.assertEqual(response.status_code, 200)

class RoleBasedAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="user2", password="password", role="user"
        )
        self.admin = CustomUser.objects.create_user(
            username="admin2", password="password", role="admin"
        )
        self.post = Post.objects.create(
            author=self.user, content="Test Post", privacy="public"
        )
    
    def test_admin_post_deletion(self):
        # Test admin can delete posts
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/api/posts/posts/{self.post.id}/delete/")
        self.assertEqual(response.status_code, 204)
    
    def test_user_post_deletion(self):
        # Test regular user cannot delete posts
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/posts/posts/{self.post.id}/delete/")
        self.assertEqual(response.status_code, 403)

class SocialFeatureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            username="user1", password="password", role="user"
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2", password="password", role="user"
        )
        self.post = Post.objects.create(
            author=self.user1, content="Test Post", privacy="public"
        )
    
    def test_comment_creation(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f"/api/posts/posts/{self.post.id}/comment/",
            {"content": "Test comment"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)
        
    def test_like_post(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f"/api/posts/posts/{self.post.id}/like/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Like.objects.count(), 1)
        
        # Test unliking
        response = self.client.post(f"/api/posts/posts/{self.post.id}/like/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Like.objects.count(), 0)
    
    def test_follow_user(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f"/api/posts/follow/{self.user1.id}/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Follow.objects.count(), 1)
        
        # Test unfollowing
        response = self.client.post(f"/api/posts/follow/{self.user1.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Follow.objects.count(), 0)
