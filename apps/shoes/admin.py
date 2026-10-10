from django.contrib import admin
from .models import ShoeCompany, Shoe, ShoeVariant


# Register your models here.
class ShoeVariantInline(admin.TabularInline):
    model = ShoeVariant
    extra = 1

@admin.register(ShoeCompany)
class ShoeCompanyAdmin(admin.ModelAdmin):
    list_display = ('id','name','phone','email')
    search_fields = ('name',)



@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company", "category", "gender",  "buying_price", "selling_price", "active", "total_stock")
    list_filter = ("category", "company", "gender", "active")
    search_fields = ("name", "model_number")
    inlines = [ShoeVariantInline]


@admin.register(ShoeVariant)
class ShoeVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "shoe", "size", "quantity", "effective_price")
    list_filter = ("size",)
    search_fields = ("shoe__name",)
