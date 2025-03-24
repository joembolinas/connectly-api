from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'POST':
        data = request.data
        if CustomUser.objects.filter(username=data.get('username')).exists():
            return Response({'error': 'Username already exists'}, status=400)
        if CustomUser.objects.filter(email=data.get('email')).exists():
            return Response({'error': 'Email already exists'}, status=400)

        user = CustomUser.objects.create(
            username=data.get('username'),
            email=data.get('email'),
            name=data.get('name'),
            role=data.get('role', 'user'),  # Default role is 'user'
            password=make_password(data.get('password'))
        )
        return Response(UserSerializer(user).data, status=201)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)  # Log the user in (session-based)
        
        # Generate or get existing token for the user
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Login successful',
            'token': token.key,  # Append token to response
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
