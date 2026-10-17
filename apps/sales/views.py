from django.shortcuts import render

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.accounts.permissions import IsCashierOrAbove
from .models import Sale
from .serializers import CheckoutSerializer, SaleSerializer
from .services import create_sale


class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated, IsCashierOrAbove]

    def get_queryset(self):
        qs = (
            Sale.objects
            .select_related("cashier")
            .prefetch_related("items__shoe_variant__shoe__company")
        )
        user = self.request.user
        # Cashiers only see their own sales
        if user.role == Role.CASHIER:
            return qs.filter(cashier=user)
        return qs

    @action(
        detail=False,
        methods=["post"],
        url_path="checkout",
        permission_classes=[IsAuthenticated, IsCashierOrAbove],
    )
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            sale = create_sale(
                cashier=request.user,
                payment_method=data["payment_method"],
                items_data=data["items"],
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            SaleSerializer(sale).data,
            status=status.HTTP_201_CREATED,
        )