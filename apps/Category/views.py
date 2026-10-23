from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category
from .serializers import CategorySerializer
from apps.accounts.permissions import IsManagerOrOwner


class ReadOrManagerPermission(IsManagerOrOwner):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return super().has_permission(request, view)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOrManagerPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]