from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import ShoeCompany, Shoe, ShoeVariant
from .serializers import ShoeCompanySerializer, ShoeSerializer, ShoeVariantSerializer
from .filters import ShoeFilter, ShoeVariantFilter
from apps.accounts.permissions import IsManagerOrOwner


class ReadOrManagerPermission(IsManagerOrOwner):
    """
    Everyone authenticated can READ (GET, HEAD, OPTIONS).
    Only managers/owners can WRITE (POST, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return super().has_permission(request, view)


class ShoeCompanyViewset(viewsets.ModelViewSet):
    queryset = ShoeCompany.objects.all()
    serializer_class = ShoeCompanySerializer
    permission_classes = [ReadOrManagerPermission]      # was IsManagerOrOwner
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "contact_person", "phone", "email"]
    ordering_fields = ["name", "created_at"]

class ShoeViewset(viewsets.ModelViewSet):
    queryset = (
        Shoe.objects
        .select_related("category", "company")
        .prefetch_related("variants")
    )
    serializer_class = ShoeSerializer
    permission_classes = [ReadOrManagerPermission]        # ← changed
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ShoeFilter
    search_fields = ["name", "model_number", "description"]
    ordering_fields = ["name", "selling_price", "buying_price", "created_at"]


class ShoeVariantViewset(viewsets.ModelViewSet):
    queryset = ShoeVariant.objects.select_related("shoe")
    serializer_class = ShoeVariantSerializer
    permission_classes = [ReadOrManagerPermission]        # ← changed
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ShoeVariantFilter
    ordering_fields = ["size", "quantity"]