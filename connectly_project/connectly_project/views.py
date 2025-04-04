from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API root endpoint
    """
    return Response({
        'auth': {
            'register': reverse('user-registration', request=request, format=format),
            'login': reverse('session-login', request=request, format=format),
            'jwt': reverse('token_obtain_pair', request=request, format=format),
            'jwt-refresh': reverse('token_refresh', request=request, format=format),
            'me': reverse('current-user', request=request, format=format),
        },
        'posts': '/api/posts/',
        'documentation': {
            'swagger': reverse('schema-swagger-ui', request=request, format=format),
            'redoc': reverse('schema-redoc', request=request, format=format),
        }
    })