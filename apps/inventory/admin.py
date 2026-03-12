from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "category",
        "supplier",
        "stock_current",
        "stock_minimum",
        "is_active",
    )
    search_fields = ("code", "name", "barcode")
    list_filter = ("category", "supplier", "is_active", "unit_measure")
