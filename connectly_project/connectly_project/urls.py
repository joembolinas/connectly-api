"""
URL configuration for connectly_project project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from posts.views import api_root

# Configure Swagger documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Connectly API",
      default_version='v1',
      description="API documentation for Connectly social media platform",
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Redirect root URL to /api/
    path('', lambda request: redirect('/api/'), name='home'),
    
    # Admin site
    path('admin/', admin.site.urls),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # API endpoints
    path('api/posts/', include('posts.urls')),
    
    # Authentication endpoints
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/jwt/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('users.urls')),
    
    # Django REST browsable API auth 
    path('api-auth/', include('rest_framework.urls')),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Google OAuth (handled by allauth, redirects will be handled via API)
    path('accounts/', include('allauth.urls')),
]
