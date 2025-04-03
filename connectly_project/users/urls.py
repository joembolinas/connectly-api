from django.urls import path
from .views import (
    RegisterView, 
    SessionLoginView, 
    LogoutView, 
    UserProfileView, 
    UserDeleteView, 
    CurrentUserView,
    UserListView
)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
import os
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'http://127.0.0.1:8000/accounts/google/login/callback/')
    client_class = OAuth2Client
    
    def post(self, request, *args, **kwargs):
        # For OAuth debugging purposes
        print(f"Request data type: {type(request.data)}")
        print(f"Request data: {request.data}")
        
        # Create a new request data with only one parameter
        modified_data = {}
        if 'access_token' in request.data:
            modified_data['access_token'] = request.data.get('access_token')
        elif 'id_token' in request.data:
            modified_data['id_token'] = request.data.get('id_token')
        elif 'code' in request.data:
            modified_data['code'] = request.data.get('code')
        
        # Replace the request data with our modified version
        request._data = modified_data
        
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            # More detailed error handling
            print(f"Error in Google login: {str(e)}")
            print(f"Modified request data: {modified_data}")
            
            # Better error response
            return Response(
                {"detail": f"OAuth authentication failed: {str(e)}. Please provide a valid access_token or id_token."},
                status=status.HTTP_400_BAD_REQUEST
            )

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-registration'),
    path('login/', SessionLoginView.as_view(), name='session-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('<int:user_id>/delete/', UserDeleteView.as_view(), name='user-delete'),
]