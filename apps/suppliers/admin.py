from django.contrib import admin

from .models import Supplier, ProductSupplier, PurchaseOrder, PurchaseOrderItem


class ProductSupplierInline(admin.TabularInline):
    model = ProductSupplier
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "is_active")
    search_fields = ("name", "email", "phone")
    list_filter = ("is_active",)
    inlines = [ProductSupplierInline]


@admin.register(ProductSupplier)
class ProductSupplierAdmin(admin.ModelAdmin):
    list_display = ("product", "supplier", "purchase_price", "is_primary", "lead_time_days")
    search_fields = ("product__name", "product__code", "supplier__name", "supplier_product_code")
    list_filter = ("is_primary", "supplier")


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "status", "expected_date", "created_by", "created_at")
    search_fields = ("number", "supplier__name")
    list_filter = ("status", "supplier", "created_at")
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ("purchase_order", "product", "quantity", "unit_price", "line_total")
    search_fields = ("purchase_order__number", "product__name", "product__code")
