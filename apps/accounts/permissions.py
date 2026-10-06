from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Role


class IsManagerOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.MANAGER, Role.OWNER]



class IsCashierOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.CASHIER, Role.MANAGER, Role.OWNER]



