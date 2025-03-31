from django.test import TestCase
from rest_framework.test import APIClient
from django.middleware.csrf import get_token
from .models import Post
from users.models import CustomUser

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
        self.csrf_token = get_token(self.client.request())
        self.client.defaults['HTTP_X_CSRFTOKEN'] = self.csrf_token

    def test_unauthorized_access(self):
        # Test without authentication
        response = self.client.get(f"/api/posts/posts/{self.private_post.id}/")
        self.assertEqual(response.status_code, 401)

    def test_private_post_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/posts/posts/{self.private_post.id}/")
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/posts/posts/{self.private_post.id}/")
        self.assertEqual(response.status_code, 200)

    def test_public_post_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/posts/posts/{self.public_post.id}/")
        self.assertEqual(response.status_code, 200)

    def test_admin_post_deletion(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(
            f"/api/posts/posts/{self.public_post.id}/delete/",
            HTTP_X_CSRFTOKEN=self.csrf_token
        )
        self.assertEqual(response.status_code, 204)

        # Create a new post for testing user deletion
        new_post = Post.objects.create(
            author=self.admin, 
            content="Test Post", 
            privacy="public"
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            f"/api/posts/posts/{new_post.id}/delete/"
        )
        self.assertEqual(response.status_code, 403)
