from django.test import TestCase
from rest_framework.test import APIClient
from .models import Post
from users.models import CustomUser

class PostPrivacyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username="user", password="password", role="user")
        self.admin = CustomUser.objects.create_user(username="admin", password="password", role="admin")
        self.private_post = Post.objects.create(author=self.user, content="Private Post", privacy="private")
        self.public_post = Post.objects.create(author=self.user, content="Public Post", privacy="public")

    def test_private_post_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/posts/{self.private_post.id}/")  # Matches 'post-detail' URL
        self.assertEqual(response.status_code, 403)  # Admin cannot view private posts of others

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/posts/{self.private_post.id}/")  # Matches 'post-detail' URL
        self.assertEqual(response.status_code, 200)  # Owner can view private posts

    def test_public_post_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/posts/{self.public_post.id}/")  # Matches 'post-detail' URL
        self.assertEqual(response.status_code, 200)  # Public posts are accessible to all

    def test_admin_post_deletion(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/posts/{self.public_post.id}/delete/")  # Matches 'post-delete' URL
        self.assertEqual(response.status_code, 204)  # Admin can delete posts

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/posts/{self.public_post.id}/delete/")  # Matches 'post-delete' URL
        self.assertEqual(response.status_code, 403)  # Regular user cannot delete posts
