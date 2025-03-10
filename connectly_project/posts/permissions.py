from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsRegularUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'user'
    