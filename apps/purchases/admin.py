from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import (
    PackTemplate,
    PackTemplateItem,
    Purchase,
    PurchaseItem,
    Supplier,
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "created_at")
    search_fields = ("name", "phone", "email")


class PackTemplateItemInline(admin.TabularInline):
    model = PackTemplateItem
    extra = 1


@admin.register(PackTemplate)
class PackTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "shoe", "name", "total_pairs")
    list_filter = ("shoe__company",)
    search_fields = ("name", "shoe__name")
    inlines = [PackTemplateItemInline]


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = ["subtotal"]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "received_by", "total_cost", "created_at")
    list_filter = ("supplier", "created_at")
    search_fields = ("supplier__name", "received_by__username")
    inlines = [PurchaseItemInline]
    readonly_fields = ["total_cost", "created_at"]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ("id", "purchase", "shoe_variant", "quantity", "buying_price", "subtotal")
    readonly_fields = ["subtotal"]