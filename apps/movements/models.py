from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class StockMovement(models.Model):
    ENTRY = "entrada"
    EXIT = "salida"
    ADJUSTMENT = "ajuste"

    MOVEMENT_TYPES = [
        (ENTRY, "Entrada"),
        (EXIT, "Salida"),
        (ADJUSTMENT, "Ajuste"),
    ]

    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name="producto",
    )
    movement_type = models.CharField("tipo de movimiento", max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField("cantidad")
    reason = models.CharField("motivo", max_length=255)
    reference = models.CharField("referencia", max_length=100, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_movements",
        verbose_name="usuario",
    )
    created_at = models.DateTimeField("creado el", auto_now_add=True)

    class Meta:
        verbose_name = "movimiento de stock"
        verbose_name_plural = "movimientos de stock"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({"quantity": "La cantidad debe ser mayor a 0."})

        if self.movement_type == self.EXIT and self.product_id:
            if self.pk is None and self.product.stock_current < self.quantity:
                raise ValidationError({"quantity": "No hay stock suficiente para realizar la salida."})

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        with transaction.atomic():
            self.full_clean()

            if is_new:
                product = self.product

                if self.movement_type == self.ENTRY:
                    product.stock_current += self.quantity
                elif self.movement_type == self.EXIT:
                    if product.stock_current < self.quantity:
                        raise ValidationError("No hay stock suficiente para realizar la salida.")
                    product.stock_current -= self.quantity
                elif self.movement_type == self.ADJUSTMENT:
                    product.stock_current = self.quantity

                product.save(update_fields=["stock_current", "updated_at"])

            super().save(*args, **kwargs)
