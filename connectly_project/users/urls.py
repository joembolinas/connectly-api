from django.urls import path
from .views import RegisterView  # Changed from UserRegistrationView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
import os

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'http://127.0.0.1:8000/accounts/google/login/callback/')
    client_class = OAuth2Client

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-registration'),
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    # Your other auth-related URLs
]