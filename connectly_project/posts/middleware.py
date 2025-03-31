from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin

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