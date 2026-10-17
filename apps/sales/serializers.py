from rest_framework import serializers

from .models import Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    shoe_name = serializers.CharField(source="shoe_variant.shoe.name", read_only=True)
    shoe_id = serializers.IntegerField(source="shoe_variant.shoe.id", read_only=True)
    size = serializers.IntegerField(source="shoe_variant.size", read_only=True)
    company_name = serializers.CharField(
        source="shoe_variant.shoe.company.name", read_only=True
    )

    class Meta:
        model = SaleItem
        fields = [
            "id",
            "shoe_variant",
            "shoe_id",
            "shoe_name",
            "company_name",
            "size",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = ["subtotal"]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    cashier_username = serializers.CharField(source="cashier.username", read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = [
            "id",
            "cashier",
            "cashier_username",
            "total_amount",
            "payment_method",
            "created_at",
            "item_count",
            "items",
        ]
        read_only_fields = ["cashier", "total_amount", "created_at"]

    def get_item_count(self, obj):
        return obj.items.count()


class CheckoutItemSerializer(serializers.Serializer):
    shoe_variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class CheckoutSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(
        choices=["CASH", "MPESA"], default="CASH"
    )
    items = CheckoutItemSerializer(many=True, allow_empty=False)