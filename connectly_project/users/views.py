from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RegisterSerializer

class RegisterView(APIView):
    """
    API endpoint for user registration
    """
    
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

class GoogleLoginView(SocialLoginView):
    """
    Google OAuth2 authentication API endpoint
    """
    adapter_class = GoogleOAuth2Adapter
    callback_url = os.getenv('GOOGLE_OAUTH_REDIRECT_URI')
    client_class = OAuth2Client
