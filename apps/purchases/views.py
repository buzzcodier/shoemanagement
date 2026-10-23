from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsManagerOrOwner 
from .models import PackTemplate, Purchase, Supplier
from .serializers import (
    PackTemplateSerializer,
    PurchaseSerializer,
    ReceiveSerializer,
    SupplierSerializer,
)
from .services import create_purchase


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsManagerOrOwner]


class PackTemplateViewSet(viewsets.ModelViewSet):
    queryset = PackTemplate.objects.select_related("shoe", "shoe__company").prefetch_related(
        "items__variant"
    )
    serializer_class = PackTemplateSerializer
    permission_classes = [IsAuthenticated, IsManagerOrOwner]

    def get_queryset(self):
        qs = super().get_queryset()
        shoe = self.request.query_params.get("shoe")
        if shoe:
            qs = qs.filter(shoe_id=shoe)
        return qs


class PurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Purchase.objects
        .select_related("supplier", "received_by")
        .prefetch_related("items__shoe_variant__shoe__company")
    )
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated, IsManagerOrOwner]

    @action(
        detail=False,
        methods=["post"],
        url_path="receive",
        permission_classes=[IsAuthenticated, IsManagerOrOwner],
    )
    def receive(self, request):
        serializer = ReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            supplier = Supplier.objects.get(pk=data["supplier"])
        except Supplier.DoesNotExist:
            return Response(
                {"detail": "Supplier not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            purchase = create_purchase(
                supplier=supplier,
                received_by=request.user,
                items_data=data["items"],
                notes=data.get("notes", ""),
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PurchaseSerializer(purchase).data,
            status=status.HTTP_201_CREATED,
        )