from django.db import models


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
