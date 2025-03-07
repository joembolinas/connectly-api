from .models import Post

class PostFactory:
    @staticmethod
    def create_post(user, content):
        return Post.objects.create(author=user, content=content)