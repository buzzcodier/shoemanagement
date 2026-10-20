from decimal import Decimal

from django.conf import settings
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PackTemplate(models.Model):
    """
    Defines how a shoe arrives in bulk — e.g. "Sack of plastic sandals,
    6 bags × 6 pairs of sizes 37–41". Reused each time stock arrives.
    """
    shoe = models.ForeignKey(
        "shoes.Shoe",
        on_delete=models.CASCADE,
        related_name="pack_templates",
    )
    name = models.CharField(max_length=150, help_text='e.g. "Carton of 12" or "Sack of 6 bags"')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["shoe__name", "name"]
        unique_together = ("shoe", "name")

    def __str__(self):
        return f"{self.shoe} — {self.name}"

    @property
    def total_pairs(self):
        return sum(item.quantity for item in self.items.all())


class PackTemplateItem(models.Model):
    template = models.ForeignKey(
        PackTemplate,
        on_delete=models.CASCADE,
        related_name="items",
    )
    variant = models.ForeignKey(
        "shoes.ShoeVariant",
        on_delete=models.CASCADE,
        related_name="pack_template_items",
    )
    quantity = models.PositiveIntegerField(
        help_text="Pairs of this size in one pack.",
    )

    class Meta:
        unique_together = ("template", "variant")

    def __str__(self):
        return f"{self.template.name} → size {self.variant.size} × {self.quantity}"


class Purchase(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="purchases",
    )
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return f"Purchase #{self.pk}"

    def recalculate_total(self):
        total = sum((item.subtotal for item in self.items.all()), Decimal("0"))
        self.total_cost = total
        self.save(update_fields=["total_cost"])
from django.db import models

# Create your models here.


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    shoe_variant = models.ForeignKey(
        "shoes.ShoeVariant",
        on_delete=models.PROTECT,
        related_name="purchase_items",
    )
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.buying_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shoe_variant} × {self.quantity}"