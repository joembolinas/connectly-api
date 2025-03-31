from django.urls import path
from .views import (
    UserRegistrationView,
    GoogleLoginView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
]