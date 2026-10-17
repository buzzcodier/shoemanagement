from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings
from django.db import models


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    MPESA = "MPESA", "M-Pesa"


class Sale(models.Model):
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return f"Sale #{self.pk}"

    def recalculate_total(self):
        total = sum((item.subtotal for item in self.items.all()), Decimal("0"))
        self.total_amount = total
        self.save(update_fields=["total_amount"])


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    shoe_variant = models.ForeignKey(
        "shoes.ShoeVariant",
        on_delete=models.PROTECT,
        related_name="sale_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shoe_variant} × {self.quantity}"