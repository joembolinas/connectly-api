"""
URL configuration for connectly_project project.
"""
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Connectly API",
        default_version='v1',
        description="A social media platform API",
        terms_of_service="https://www.connectly.com/terms/",
        contact=openapi.Contact(email="contact@connectly.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

def home(request):
    return redirect('schema-swagger-ui')

router = DefaultRouter()
# Register your viewsets here if you have any

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # Adds login/logout to browsable API
    path('api/posts/', include('posts.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include(router.urls)),  # This will provide a root API view
    
    # Swagger documentation URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/token-auth/', obtain_auth_token, name='api_token_auth'),
    
]
