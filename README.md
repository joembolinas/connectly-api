
# Connectly API Documentation

## Overview

Connectly is a social media platform API built with Django REST Framework. It supports posts, comments, likes, user following, and personalized feeds with robust authentication and role-based access control.

## Base URL

```
http://127.0.0.1:8000/api/
```

## Authentication

All endpoints except registration and login require authentication via JWT token.

### Authentication Endpoints

#### Register a new user

```http
POST /api/auth/register/
```

**Parameters:**

- `username` (string, required): User's username
- `email` (string, required): User's email address
- `password` (string, required): User's password
- `password2` (string, required): Password confirmation

**Response:** `201 Created` with user data or `400 Bad Request` with error details

#### Obtain JWT token

```http
POST /api/auth/jwt/
```

**Parameters:**

- `username` (string, required): User's username
- `password` (string, required): User's password

**Response:** `200 OK` with access and refresh tokens or `401 Unauthorized`

#### Refresh JWT token

```http
POST /api/auth/jwt/refresh/
```

**Parameters:**

- `refresh` (string, required): Refresh token

**Response:** `200 OK` with new access token or `401 Unauthorized`

#### Google OAuth login

```http
POST /api/auth/google/login/
```

**Parameters:**

- `access_token` (string, required): Google OAuth access token
- `code` (string, required): Google auth code
- `id_token` (string, required): Google ID token

**Response:** `200 OK` with access and refresh tokens or `400 Bad Request`

#### Get standard token authentication

```http
POST /api/auth/token/
```

**Parameters:**

- `username` (string, required): User's username
- `password` (string, required): User's password

**Response:** `200 OK` with auth token or `401 Unauthorized`

## User Management

#### List all users

```http
GET /api/posts/users/
```

**Authentication:** JWT token required

**Response:** `200 OK` with list of users

#### Create a new user

```http
POST /api/posts/users/
```

**Parameters:**

- `username` (string, required): User's username
- `email` (string, required): User's email address
- `password` (string, required): User's password
- `first_name` (string, optional): User's first name
- `last_name` (string, optional): User's last name

**Response:** `201 Created` with user data or `400 Bad Request` with error details

## Posts

#### List all posts

```http
GET /api/posts/posts/
```

**Authentication:** JWT token required

**Query Parameters:**

- `page` (integer, optional): Page number for pagination
- `page_size` (integer, optional): Number of posts per page (max 100)

**Response:** `200 OK` with paginated list of posts

#### Create a new post

```http
POST /api/posts/posts/
```

**Authentication:** JWT token required

**Parameters:**

- `content` (string, required): Content of the post
- `privacy` (string, optional): Privacy setting (`public` or `private`, default `public`)

**Response:** `201 Created` with post data or `400 Bad Request` with error details

#### Get details of a specific post

```http
GET /api/posts/posts/{post_id}/
```

**Authentication:** JWT token required

**Path Parameters:**

- `post_id` (integer, required): ID of the post

**Response:** `200 OK` with post details or `404 Not Found`

#### Delete a specific post

```http
DELETE /api/posts/posts/{post_id}/delete/
```

**Authentication:** JWT token required (admin only)

**Path Parameters:**

- `post_id` (integer, required): ID of the post

**Response:** `204 No Content` or `403 Forbidden` if not admin

## Comments

#### List all comments for a post

```http
GET /api/posts/posts/{post_id}/comments/
```

**Authentication:** JWT token required

**Path Parameters:**

- `post_id` (integer, required): ID of the post

**Query Parameters:**

- `page` (integer, optional): Page number for pagination
- `page_size` (integer, optional): Number of comments per page (max 100)

**Response:** `200 OK` with paginated list of comments

#### Add a comment to a post

```http
POST /api/posts/posts/{post_id}/comment/
```

**Authentication:** JWT token required

**Path Parameters:**

- `post_id` (integer, required): ID of the post

**Parameters:**

- `content` (string, required): Content of the comment

**Response:** `201 Created` with comment data or `400 Bad Request` with error details

## Likes

#### Like or unlike a post

```http
POST /api/posts/posts/{post_id}/like/
```

**Authentication:** JWT token required

**Path Parameters:**

- `post_id` (integer, required): ID of the post

**Response:**

- `201 Created` with like data (when liking)
- `200 OK` with message "unliked" (when unliking)

## Following

#### Follow or unfollow a user

```http
POST /api/posts/follow/{user_id}/
```

**Authentication:** JWT token required

**Path Parameters:**

- `user_id` (integer, required): ID of the user to follow/unfollow

**Response:**

- `201 Created` with follow data (when following)
- `200 OK` with message "unfollowed" (when unfollowing)
- `400 Bad Request` if trying to follow yourself

## Feeds

#### Get general feed

```http
GET /api/posts/feed/
```

**Authentication:** JWT token required

**Description:** Shows all public posts and private posts owned by the requesting user

**Query Parameters:**

- `page` (integer, optional): Page number for pagination
- `page_size` (integer, optional): Number of posts per page (max 100)

**Response:** `200 OK` with paginated list of posts

#### Get personalized newsfeed

```http
GET /api/posts/newsfeed/
```

**Authentication:** JWT token required

**Description:** Shows posts from followed users and the requesting user's own posts

**Query Parameters:**

- `page` (integer, optional): Page number for pagination
- `page_size` (integer, optional): Number of posts per page (max 100)

**Response:** `200 OK` with paginated list of posts

## Documentation

#### Swagger UI documentation

```http
GET /swagger/
```

**Description:** Interactive API documentation with Swagger UI

#### ReDoc API documentation

```http
GET /redoc/
```

**Description:** Alternative API documentation with ReDoc

## Error Codes

- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Rate Limiting

The API implements rate limiting to prevent abuse. Users are limited to a certain number of requests per minute.

## Pagination

List endpoints return paginated results. Default page size is 10 items, with a maximum of 100 items per page.

---

*Note: This documentation reflects the current state of the API as of April 2, 2025. Future developments may add new endpoints or modify existing ones.*
