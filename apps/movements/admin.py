from django.contrib import admin
from .models import StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "movement_type", "quantity", "user", "created_at")
    search_fields = ("product__name", "product__code", "reference", "reason")
    list_filter = ("movement_type", "created_at")
    readonly_fields = ("product", "movement_type", "quantity", "reason", "reference", "user", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
