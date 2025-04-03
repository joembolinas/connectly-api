from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate, login, logout
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from collections import OrderedDict
from .models import CustomUser
from .serializers import (
    RegisterSerializer, 
    UserDetailSerializer, 
    UserUpdateSerializer,
    UserListSerializer
)

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))

class RegisterView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        operation_description="Create a new user account",
        responses={
            201: "User created successfully",
            400: "Bad request - invalid data"
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SessionLoginView(APIView):
    """
    API endpoint for session-based login
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
        ),
        operation_description="Login with username and password for session authentication",
        responses={
            200: "Login successful",
            400: "Invalid credentials"
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    API endpoint for logging out
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Log out current user",
        responses={
            200: "Logout successful",
        }
    )
    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out."})

class UserProfileView(APIView):
    """
    API endpoint for retrieving and updating user profiles
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get user profile details",
        responses={
            200: UserDetailSerializer,
            404: "User not found"
        }
    )
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=UserUpdateSerializer,
        operation_description="Update user profile",
        responses={
            200: UserDetailSerializer,
            400: "Bad request - invalid data",
            403: "Permission denied - not your profile"
        }
    )
    def patch(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Check if user is updating their own profile or is admin
        if request.user.id != user_id and not request.user.is_admin():
            return Response(
                {"detail": "You do not have permission to update this profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    """
    API endpoint for deleting users (admin only)
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Delete a user (admin only)",
        responses={
            204: "User deleted successfully",
            404: "User not found"
        }
    )
    def delete(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CurrentUserView(APIView):
    """
    API endpoint for retrieving current user's information
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get current authenticated user's information",
        responses={
            200: UserDetailSerializer,
        }
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

class UserListView(APIView):
    """
    API endpoint for listing all users
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    
    @swagger_auto_schema(
        operation_description="List all users",
        responses={
            200: "List of users",
        },
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        users = CustomUser.objects.all().order_by('-date_joined')
        
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request)
        
        serializer = UserListSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)
