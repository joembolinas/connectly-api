
# Connectly API

A social media platform API built with Django REST Framework that supports posts, comments, likes, and user following features with robust authentication and role-based access control.

## Features

- **Authentication**: JWT-based authentication with Google OAuth integration
- **Posts Management**: Create, view, and delete posts with privacy controls
- **Social Features**: Comments, likes, and user following
- **Role-Based Access Control**: Different permission levels for admins and regular users
- **Feed Generation**: Personalized feed based on follows

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/connectly-api.git
cd connectly-api
```

2. Create and activate a virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create .env file (see .env.example for reference)
5. Run migrations

```bash
python connectly_project/manage.py migrate
```

6. Start the development server

```bash
python connectly_project/manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/jwt/` - Get JWT token
- `POST /api/auth/jwt/refresh/` - Refresh JWT token
- `POST /api/auth/google/login/` - Google OAuth login

### Posts

- `GET /api/posts/posts/` - List all posts
- `POST /api/posts/posts/` - Create a new post
- `GET /api/posts/posts/{id}/` - Get post details
- `DELETE /api/posts/posts/{id}/delete/` - Delete a post (admin only)

### Comments

- `GET /api/posts/posts/{id}/comments/` - List comments for a post
- `POST /api/posts/posts/{id}/comment/` - Add a comment to a post

### Likes

- `POST /api/posts/posts/{id}/like/` - Like/unlike a post

### Feed

- `GET /api/posts/feed/` - Get general feed
- `GET /api/posts/newsfeed/` - Get personalized feed based on follows

### Following

- `POST /api/posts/follow/{user_id}/` - Follow/unfollow a user

## Documentation

- API documentation is available at `/swagger/` and `/redoc/`
