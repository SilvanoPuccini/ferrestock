from django import forms

from apps.inventory.models import Product
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "email",
            "phone",
            "address",
            "contact_person",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Aceros del Sur"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "proveedor@email.com"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+56 ..."}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección del proveedor"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del contacto"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["number", "supplier", "expected_date", "notes"]
        widgets = {
            "number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: OC-0001"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "expected_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Observaciones"}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ["product", "quantity", "unit_price"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

    def __init__(self, *args, purchase_order=None, **kwargs):
        super().__init__(*args, **kwargs)

        queryset = Product.objects.order_by("name")
        if purchase_order is not None:
            filtered = Product.objects.filter(
                supplier_links__supplier=purchase_order.supplier
            ).distinct().order_by("name")
            if filtered.exists():
                queryset = filtered

        self.fields["product"].queryset = queryset