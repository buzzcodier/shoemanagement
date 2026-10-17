from django.contrib import admin

# Register your models here.

from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ["subtotal"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "cashier", "payment_method", "total_amount", "created_at")
    list_filter = ("payment_method", "created_at")
    search_fields = ("cashier__username",)
    inlines = [SaleItemInline]
    readonly_fields = ["total_amount", "created_at"]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sale", "shoe_variant", "quantity", "unit_price", "subtotal")
    readonly_fields = ["subtotal"]