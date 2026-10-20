from rest_framework import serializers
from django.db import transaction

from .models import (
    PackTemplate,
    PackTemplateItem,
    Purchase,
    PurchaseItem,
    Supplier,
)


class SupplierSerializer(serializers.ModelSerializer):
    purchase_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            "id", "name", "contact_person", "phone", "email",
            "address", "notes", "created_at", "purchase_count",
        ]
        read_only_fields = ["created_at"]

    def get_purchase_count(self, obj):
        return obj.purchases.count()


class PackTemplateItemSerializer(serializers.ModelSerializer):
    size = serializers.IntegerField(source="variant.size", read_only=True)
    shoe_id = serializers.IntegerField(source="variant.shoe.id", read_only=True)

    class Meta:
        model = PackTemplateItem
        fields = ["id", "template", "variant", "size", "shoe_id", "quantity"]
        read_only_fields = ["template"]  # set via nested create





# ... (other serializers unchanged)


class PackTemplateSerializer(serializers.ModelSerializer):
    items = PackTemplateItemSerializer(many=True)
    total_pairs = serializers.IntegerField(read_only=True)
    shoe_name = serializers.CharField(source="shoe.name", read_only=True)
    company_name = serializers.CharField(source="shoe.company.name", read_only=True)

    class Meta:
        model = PackTemplate
        fields = [
            "id", "shoe", "shoe_name", "company_name",
            "name", "notes", "total_pairs",
            "items", "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_items(self, items):
        ids = [item["variant"].id for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Each size can only appear once in a pack template."
            )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        template = PackTemplate.objects.create(**validated_data)
        for item in items_data:
            PackTemplateItem.objects.create(template=template, **item)
        return template

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                PackTemplateItem.objects.create(template=instance, **item)
        return instance

class PurchaseItemSerializer(serializers.ModelSerializer):
    shoe_name = serializers.CharField(source="shoe_variant.shoe.name", read_only=True)
    shoe_id = serializers.IntegerField(source="shoe_variant.shoe.id", read_only=True)
    company_name = serializers.CharField(
        source="shoe_variant.shoe.company.name", read_only=True
    )
    size = serializers.IntegerField(source="shoe_variant.size", read_only=True)

    class Meta:
        model = PurchaseItem
        fields = [
            "id", "shoe_variant", "shoe_id", "shoe_name", "company_name",
            "size", "quantity", "buying_price", "subtotal",
        ]
        read_only_fields = ["subtotal"]


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    received_by_username = serializers.CharField(
        source="received_by.username", read_only=True
    )
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = [
            "id", "supplier", "supplier_name",
            "received_by", "received_by_username",
            "total_cost", "notes", "created_at",
            "item_count", "items",
        ]
        read_only_fields = ["received_by", "total_cost", "created_at"]

    def get_item_count(self, obj):
        return obj.items.count()


class SimpleReceiveLineSerializer(serializers.Serializer):
    shoe_variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    buying_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class PackReceiveLineSerializer(serializers.Serializer):
    pack_template_id = serializers.IntegerField()
    packs = serializers.IntegerField(min_value=1)
    buying_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class ReceiveLineSerializer(serializers.Serializer):
    """
    Accepts either shape, validates accordingly.
    """
    shoe_variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=False, allow_null=True)
    pack_template_id = serializers.IntegerField(required=False, allow_null=True)
    packs = serializers.IntegerField(required=False, allow_null=True)
    buying_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, attrs):
        has_simple = attrs.get("shoe_variant_id") and attrs.get("quantity")
        has_pack = attrs.get("pack_template_id") and attrs.get("packs")

        if has_simple and has_pack:
            raise serializers.ValidationError(
                "Line must be either a simple line or a pack line, not both."
            )
        if not has_simple and not has_pack:
            raise serializers.ValidationError(
                "Line must be either a simple line (shoe_variant_id + quantity) "
                "or a pack line (pack_template_id + packs)."
            )
        return attrs


class ReceiveSerializer(serializers.Serializer):
    supplier = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    items = ReceiveLineSerializer(many=True, allow_empty=False)