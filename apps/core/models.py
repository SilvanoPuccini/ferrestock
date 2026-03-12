from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Creación"),
        ("update", "Actualización"),
        ("delete", "Eliminación"),
        ("send", "Envío"),
        ("receive", "Recepción"),
        ("cancel", "Cancelación"),
        ("import", "Importación"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="usuario",
    )
    module = models.CharField("módulo", max_length=50)
    action = models.CharField("acción", max_length=20, choices=ACTION_CHOICES)
    object_type = models.CharField("tipo de objeto", max_length=100)
    object_id = models.CharField("ID de objeto", max_length=50, blank=True)
    object_repr = models.CharField("representación", max_length=255, blank=True)
    description = models.TextField("descripción", blank=True)
    metadata = models.JSONField("metadata", default=dict, blank=True)
    created_at = models.DateTimeField("creado el", auto_now_add=True)

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_display()} - {self.object_type} - {self.created_at:%d/%m/%Y %H:%M}"
