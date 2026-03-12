from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "module", "action", "object_type", "object_repr", "user")
    list_filter = ("module", "action", "created_at")
    search_fields = ("object_type", "object_repr", "description", "user__username")
    readonly_fields = (
        "user",
        "module",
        "action",
        "object_type",
        "object_id",
        "object_repr",
        "description",
        "metadata",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
