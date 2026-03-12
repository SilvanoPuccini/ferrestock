from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("nombre", max_length=100, unique=True)
    description = models.TextField("descripción", blank=True)
    is_active = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField("creada el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizada el", auto_now=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ("unidad", "Unidad"),
        ("caja", "Caja"),
        ("bolsa", "Bolsa"),
        ("metro", "Metro"),
        ("kg", "Kilogramo"),
        ("litro", "Litro"),
    ]

    code = models.CharField("código interno", max_length=50, unique=True)
    barcode = models.CharField("código de barras", max_length=100, blank=True, unique=True, null=True)
    name = models.CharField("nombre", max_length=150)
    description = models.TextField("descripción", blank=True)
    category = models.ForeignKey(
        "inventory.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="categoría",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="proveedor principal",
    )
    cost_price = models.DecimalField(
        "precio de costo",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    sale_price = models.DecimalField(
        "precio de venta",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock_current = models.IntegerField("stock actual", default=0)
    stock_minimum = models.IntegerField("stock mínimo", default=0)
    unit_measure = models.CharField("unidad de medida", max_length=20, choices=UNIT_CHOICES, default="unidad")
    image = models.ImageField("imagen", upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField("activo", default=True)
    created_at = models.DateTimeField("creado el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado el", auto_now=True)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_low_stock(self):
        return self.stock_current <= self.stock_minimum

    def get_absolute_url(self):
        return reverse("inventory:product_detail", kwargs={"pk": self.pk})
