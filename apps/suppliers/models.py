from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.urls import reverse


class Supplier(models.Model):
    name = models.CharField("nombre", max_length=150, unique=True)
    email = models.EmailField("email", blank=True)
    phone = models.CharField("teléfono", max_length=50, blank=True)
    address = models.CharField("dirección", max_length=255, blank=True)
    contact_person = models.CharField("persona de contacto", max_length=100, blank=True)
    is_active = models.BooleanField("activo", default=True)
    created_at = models.DateTimeField("creado el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado el", auto_now=True)

    class Meta:
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductSupplier(models.Model):
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.CASCADE,
        related_name="supplier_links",
        verbose_name="producto",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="product_links",
        verbose_name="proveedor",
    )
    supplier_product_code = models.CharField("código del proveedor", max_length=100, blank=True)
    purchase_price = models.DecimalField(
        "precio de compra",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    is_primary = models.BooleanField("proveedor principal", default=False)
    lead_time_days = models.PositiveIntegerField("lead time (días)", default=0)
    notes = models.CharField("notas", max_length=255, blank=True)
    created_at = models.DateTimeField("creado el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado el", auto_now=True)

    class Meta:
        verbose_name = "relación producto-proveedor"
        verbose_name_plural = "relaciones producto-proveedor"
        ordering = ["product__name", "supplier__name"]
        unique_together = ("product", "supplier")

    def __str__(self):
        return f"{self.product.name} - {self.supplier.name}"


class PurchaseOrder(models.Model):
    DRAFT = "draft"
    SENT = "sent"
    RECEIVED = "received"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (DRAFT, "Borrador"),
        (SENT, "Enviada"),
        (RECEIVED, "Recibida"),
        (CANCELLED, "Cancelada"),
    ]

    number = models.CharField("número", max_length=30, unique=True)
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        verbose_name="proveedor",
    )
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    expected_date = models.DateField("fecha estimada", blank=True, null=True)
    notes = models.TextField("notas", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_purchase_orders",
        verbose_name="creado por",
    )
    created_at = models.DateTimeField("creado el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado el", auto_now=True)

    class Meta:
        verbose_name = "orden de compra"
        verbose_name_plural = "órdenes de compra"
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.all())

    def get_absolute_url(self):
        return reverse("suppliers:purchase_order_detail", kwargs={"pk": self.pk})

    def receive(self, user):
        if self.status == self.RECEIVED:
            raise ValidationError("La orden ya fue recibida.")
        if self.status == self.CANCELLED:
            raise ValidationError("No se puede recibir una orden cancelada.")
        if not self.items.exists():
            raise ValidationError("La orden no tiene ítems para recibir.")

        from apps.movements.models import StockMovement

        with transaction.atomic():
            for item in self.items.select_related("product"):
                StockMovement.objects.create(
                    product=item.product,
                    movement_type=StockMovement.ENTRY,
                    quantity=item.quantity,
                    reason=f"Recepción de orden de compra {self.number}",
                    reference=self.number,
                    user=user,
                )

            self.status = self.RECEIVED
            self.save(update_fields=["status", "updated_at"])


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        "suppliers.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="orden de compra",
    )
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="purchase_order_items",
        verbose_name="producto",
    )
    quantity = models.PositiveIntegerField("cantidad", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        "precio unitario",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "ítem de orden de compra"
        verbose_name_plural = "ítems de orden de compra"
        ordering = ["id"]

    def __str__(self):
        return f"{self.purchase_order.number} - {self.product.name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price