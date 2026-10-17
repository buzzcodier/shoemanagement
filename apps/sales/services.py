from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.shoes.models import ShoeVariant
from .models import PaymentMethod, Sale, SaleItem


@transaction.atomic
def create_sale(*, cashier, payment_method, items_data):
    """
    items_data: list of dicts like:
        [{"shoe_variant_id": 1, "quantity": 2, "unit_price": "3200.00"}, ...]

    Raises ValidationError if stock is insufficient or data is invalid.
    """
    if not items_data:
        raise ValidationError("Sale must contain at least one item.")

    if payment_method not in PaymentMethod.values:
        raise ValidationError(f"Invalid payment method: {payment_method}")

    sale = Sale.objects.create(
        cashier=cashier,
        payment_method=payment_method,
    )

    for row in items_data:
        variant_id = row.get("shoe_variant_id")
        quantity = int(row.get("quantity", 0))
        unit_price = Decimal(str(row.get("unit_price", "0")))

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if unit_price <= 0:
            raise ValidationError("Unit price must be greater than zero.")

        # select_for_update locks the row for the duration of the transaction
        try:
            variant = (
                ShoeVariant.objects
                .select_for_update()
                .select_related("shoe")
                .get(pk=variant_id)
            )
        except ShoeVariant.DoesNotExist:
            raise ValidationError(f"Variant {variant_id} does not exist.")

        if variant.quantity < quantity:
            raise ValidationError(
                f"Insufficient stock for {variant}: "
                f"only {variant.quantity} available."
            )

        variant.quantity -= quantity
        variant.save(update_fields=["quantity"])

        SaleItem.objects.create(
            sale=sale,
            shoe_variant=variant,
            quantity=quantity,
            unit_price=unit_price,
        )

    sale.recalculate_total()
    return sale