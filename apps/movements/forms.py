from django import forms

from .models import StockMovement


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "product",
            "movement_type",
            "quantity",
            "reason",
            "reference",
        ]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "movement_type": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "reason": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Compra a proveedor / Venta mostrador / Ajuste por conteo"}),
            "reference": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: OC-001 / FAC-100 / AJUSTE-01"}),
        }
