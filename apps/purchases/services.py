from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.shoes.models import ShoeVariant
from .models import PackTemplate, Purchase, PurchaseItem


@transaction.atomic
def create_purchase(*, supplier, received_by, items_data, notes=""):
    """
    items_data: list of dicts.
    Two shapes are supported:

    Simple line (buy pairs of a single size):
        {"shoe_variant_id": 12, "quantity": 10, "buying_price": "2400.00"}

    Pack line (buy whole packs whose contents are defined by a PackTemplate):
        {"pack_template_id": 2, "packs": 1, "buying_price": "1800.00"}

    `buying_price` in a pack line means cost per pair (not per pack).
    """
    if not items_data:
        raise ValidationError("Purchase must contain at least one item.")

    purchase = Purchase.objects.create(
        supplier=supplier,
        received_by=received_by,
        notes=notes,
    )

    for row in items_data:
        buying_price = Decimal(str(row.get("buying_price", "0")))
        if buying_price <= 0:
            raise ValidationError("Buying price must be greater than zero.")

        # --- Pack line ---
        if "pack_template_id" in row and row["pack_template_id"]:
            packs = int(row.get("packs", 0))
            if packs <= 0:
                raise ValidationError("Number of packs must be greater than zero.")

            try:
                template = PackTemplate.objects.prefetch_related("items__variant").get(
                    pk=row["pack_template_id"]
                )
            except PackTemplate.DoesNotExist:
                raise ValidationError(f"Pack template {row['pack_template_id']} not found.")

            template_items = list(template.items.all())
            if not template_items:
                raise ValidationError(
                    f"Pack template '{template.name}' has no sizes defined."
                )

            for titem in template_items:
                total_qty = titem.quantity * packs

                variant = (
                    ShoeVariant.objects
                    .select_for_update()
                    .get(pk=titem.variant_id)
                )
                variant.quantity += total_qty
                variant.save(update_fields=["quantity"])

                PurchaseItem.objects.create(
                    purchase=purchase,
                    shoe_variant=variant,
                    quantity=total_qty,
                    buying_price=buying_price,
                )

        # --- Simple line ---
        else:
            variant_id = row.get("shoe_variant_id")
            quantity = int(row.get("quantity", 0))
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero.")

            try:
                variant = (
                    ShoeVariant.objects
                    .select_for_update()
                    .get(pk=variant_id)
                )
            except ShoeVariant.DoesNotExist:
                raise ValidationError(f"Variant {variant_id} does not exist.")

            variant.quantity += quantity
            variant.save(update_fields=["quantity"])

            PurchaseItem.objects.create(
                purchase=purchase,
                shoe_variant=variant,
                quantity=quantity,
                buying_price=buying_price,
            )

    purchase.recalculate_total()
    return purchase