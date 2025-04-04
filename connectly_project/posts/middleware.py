from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
import time
import logging

logger = logging.getLogger('api.performance')

class RoleMiddleware(MiddlewareMixin):
    """
    Middleware to check user roles for specific operations
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check for admin-only operations
        if 'delete' in request.path and not request.user.is_anonymous:
            if request.user.role != 'admin':
                raise PermissionDenied("Only admins can perform this operation")
        return None

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log slow requests (over 0.5 seconds)
        if duration > 0.5 and request.path.startswith('/api/'):
            logger.warning(
                f'Slow API request: {request.method} {request.path} took {duration:.2f}s'
            )
        
        # Add timing header to all API responses
        if request.path.startswith('/api/'):
            response['X-Request-Duration'] = f"{duration:.2f}s"
        
        return response

class DisableCSRFMiddleware:
    """Completely disable CSRF for all requests - USE FOR TESTING ONLY"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Set attribute that exempts this request from CSRF verification
        setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)