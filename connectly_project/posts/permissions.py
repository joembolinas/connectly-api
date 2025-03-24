from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    """
    Allow access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'admin' or request.user.is_superuser)

class IsModeratorUser(BasePermission):
    """
    Allow access only to moderator users.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'moderator' or request.user.role == 'admin' or request.user.is_superuser)

class IsRegularUser(BasePermission):
    """
    Allow access only to regular users and above (regular, moderator, admin).
    """
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'user' or request.user.role == 'moderator' or 
                                request.user.role == 'admin' or request.user.is_superuser)

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.author == request.user

class IsPostOwnerOrPublic(BasePermission):
    """
    Allow access to post based on privacy setting.
    """
    def has_object_permission(self, request, view, obj):
        # Admin and moderators can see all posts
        if request.user and (request.user.role in ['admin', 'moderator'] or request.user.is_superuser):
            return True
        
        # Public posts are visible to all authenticated users
        if obj.privacy == 'public':
            return True
        
        # Private posts are only visible to the owner
        return obj.author == request.user
