from rest_framework.permissions import BasePermission

from .models import Role


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.OWNER


class IsManagerOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            Role.OWNER,
            Role.MANAGER,
        )


class IsCashierOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            Role.OWNER,
            Role.MANAGER,
            Role.CASHIER,
        )


class IsStockManagerOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            Role.OWNER,
            Role.MANAGER,
            Role.STOCK_MANAGER,
        )