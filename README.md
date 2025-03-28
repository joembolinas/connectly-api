# Connectly API Documentation

## 1. Introduction

Connectly API is a social media backend platform built using Django REST Framework. It provides the core functionality for a social networking application, including user management, posts, comments, likes, follows, and a personalized news feed.

---

## 2. System Architecture

### 2.1 Technology Stack

- **Framework**: Django 5.1.7, Django REST Framework
- **Database**: SQLite (Development), configurable for PostgreSQL in production
- **Authentication**: Multiple auth methods including Token, JWT, Session, and OAuth2 (Google)
- **Password Hashing**: Argon2 (primary), PBKDF2 (backup)
- **Security**: CORS support, CSRF protection

### 2.2 Project Structure

```
connectly-api/
├── connectly_project/
│   ├── connectly_project/        # Project configuration
│   │   ├── asgi.py               # ASGI configuration
│   │   ├── settings.py           # Project settings
│   │   ├── urls.py               # Main URL configuration
│   │   └── wsgi.py               # WSGI configuration
│   ├── posts/                    # Posts app
│   │   ├── admin.py              # Admin configurations
│   │   ├── apps.py               # App configuration
│   │   ├── factory.py            # Factory for post creation
│   │   ├── models.py             # Models: Post, Comment, Like, Follow
│   │   ├── permissions.py        # Custom permissions
│   │   ├── serializers.py        # API serializers
│   │   ├── urls.py               # Posts app URL routing
│   │   ├── utils.py              # Utility functions
│   │   └── views.py              # API views
│   ├── users/                    # Users app
│   │   ├── admin.py              # User admin configuration
│   │   ├── apps.py               # App configuration
│   │   ├── models.py             # CustomUser model
│   │   └── views.py              # User-related views
│   └── manage.py                 # Django management script
```

---

## 3. Core Features

### 3.1 Authentication System

Connectly API supports multiple authentication methods:

- **Token Authentication**: For API clients and mobile apps
- **JWT Authentication**: For secure, stateless auth with auto-refresh
- **Session Authentication**: For browser-based clients
- **Google OAuth**: Social login integration

### 3.2 User Management

- Custom user model with role-based permissions (`admin` and `user` roles)
- User registration and profile management
- Follow/unfollow functionality

### 3.3 Content Features

- **Posts**: Create, read, update, and delete text posts
- **Comments**: Add comments to posts with threaded replies support
- **Likes**: Like/unlike posts with duplicate prevention
- **News Feed**: Personalized feed showing posts from followed users and self

### 3.4 Security Features

- Role-based access control
- Token and JWT authentication
- Argon2 password hashing (more secure than default PBKDF2)
- CSRF protection for browser-based interactions

---

## 4. Data Models

### 4.1 User Models

```python
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    # Custom related names to avoid conflicts with auth models
    groups = models.ManyToManyField('auth.Group', related_name='customuser_set')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_set')
```

### 4.2 Content Models

```python
class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(CustomUser, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['author', 'post', 'text']  # Prevents duplicate comments

class Like(models.Model):
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # Prevents duplicate likes

class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')  # Prevents duplicate follows
```

---

## 5. API Endpoints

### 5.1 Authentication Endpoints

- `POST /api/token/` - Obtain DRF Token authentication token
- `POST /api/jwt/` - Obtain JWT token
- `POST /api/jwt/refresh/` - Refresh JWT token
- `/accounts/login/` - Django allauth login
- `/accounts/google/login/` - Google OAuth login

### 5.2 User Endpoints

- `GET /api/posts/users/` - List all users
- `POST /api/posts/users/` - Create a new user
- `POST /api/posts/users/<id>/follow/` - Follow a user
- `DELETE /api/posts/users/<id>/follow/` - Unfollow a user

### 5.3 Post Endpoints

- `GET /api/posts/posts/` - List all posts
- `POST /api/posts/posts/` - Create a new post
- `GET /api/posts/posts/<id>/` - Get a specific post
- `PUT /api/posts/posts/<id>/` - Update a post
- `DELETE /api/posts/posts/<id>/` - Delete a post
- `POST /api/posts/posts/<id>/like/` - Like/unlike a post
- `POST /api/posts/create-post/` - Create a post using Factory pattern

### 5.4 Comment Endpoints

- `GET /api/posts/comments/` - List all comments
- `POST /api/posts/comments/` - Create a new comment
- `GET /api/posts/posts/<id>/comments/` - Get comments for a specific post

### 5.5 Feed Endpoints

- `GET /api/posts/feed/` - Get personalized news feed

### 5.6 Role-based Endpoints

- `GET /api/posts/admin-only/` - Admin-only access endpoint
- `GET /api/posts/user-view/` - Regular user access endpoint

---

## 6. Authentication & Permissions

### 6.1 Authentication Configuration

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

### 6.2 Permission Classes

- `IsAuthenticated` - User must be authenticated
- `IsAuthenticatedOrReadOnly` - Read operations for anyone, write operations require authentication
- `IsAdminUser` - Requires user to have the 'admin' role
- `IsRegularUser` - Requires user to have the 'user' role

---

## 7. Performance Features

### 7.1 Pagination

All list endpoints use pagination with 10 items per page by default:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

### 7.2 Optimized Queries

The News Feed view uses optimized database queries:

```python
posts = Post.objects.filter(
    Q(author__in=following_ids) | Q(author=request.user)
).select_related('author').prefetch_related(
    Prefetch('likes', queryset=Like.objects.filter(user=request.user), to_attr='user_likes'),
    'comments',
).order_by('-created_at')
```

---

## 8. Design Patterns

### 8.1 Factory Pattern

The application uses a Factory pattern for post creation:

```python
class PostFactory:
    @staticmethod
    def create_post(user, content):
        return Post.objects.create(author=user, content=content)
```

### 8.2 Serializer Pattern

Django REST Framework serializers handle complex data conversion:

```python
class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    # Methods to calculate these fields at serialization time
```

---

## 9. Installation & Setup

### 9.1 Prerequisites

- Python 3.9+
- pip

### 9.2 Installation Steps

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/connectly-api.git
   cd connectly-api
   ```

2. Create a virtual environment
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations
   ```bash
   cd connectly_project
   python manage.py migrate
   ```

5. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server
   ```bash
   python manage.py runserver
   ```

### 9.3 Configuration

Key settings that may need adjustment:

- `ALLOWED_HOSTS` - Add your domain
- `DEBUG` - Set to False in production
- `SECRET_KEY` - Change in production
- `DATABASE` - Configure for PostgreSQL in production
- `SOCIALACCOUNT_PROVIDERS` - Add your Google OAuth credentials

---

## 10. Current Limitations & Future Enhancements

### 10.1 Current Limitations

- Limited media support (no image uploads for posts or profiles)
- Basic privacy controls
- SQLite database (suitable for development only)
- Limited test coverage

### 10.2 Planned Enhancements

- Media upload functionality
- Enhanced privacy settings
- Redis caching integration
- PostgreSQL migration for production
- Comprehensive test suite
- API documentation with Swagger/OpenAPI

---

## 11. Security Considerations

- Strong password hashing with Argon2
- CSRF protection
- Secure cookie settings (in production)
- Multiple authentication methods
- Role-based access control

---

This documentation represents the current state of the Connectly API project. As development continues, this document should be updated to reflect new features and changes.

Similar code found with 1 license type
