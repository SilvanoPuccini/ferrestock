from django import forms
from .models import Supplier


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
