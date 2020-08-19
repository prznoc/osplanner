from rest_framework import permissions

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.employee == request.user or request.user.is_superuser or request.method in permissions.SAFE_METHODS

class IsAdminUserOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_superuser
