from django import forms

from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Tornillería"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción de la categoría"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "code",
            "barcode",
            "name",
            "description",
            "category",
            "supplier",
            "cost_price",
            "sale_price",
            "stock_current",
            "stock_minimum",
            "unit_measure",
            "image",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: MART-001"}),
            "barcode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Opcional"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Martillo de acero"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción del producto"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "sale_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock_current": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "stock_minimum": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "unit_measure": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get("cost_price")
        sale_price = cleaned_data.get("sale_price")
        if cost_price is not None and sale_price is not None and cost_price > sale_price:
            raise forms.ValidationError(
                "El precio de costo no puede ser mayor al precio de venta."
            )
        return cleaned_data


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "code",
            "barcode",
            "name",
            "description",
            "category",
            "supplier",
            "cost_price",
            "sale_price",
            "stock_minimum",
            "unit_measure",
            "image",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: MART-001"}),
            "barcode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Opcional"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Martillo de acero"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción del producto"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "sale_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock_minimum": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "unit_measure": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get("cost_price")
        sale_price = cleaned_data.get("sale_price")
        if cost_price is not None and sale_price is not None and cost_price > sale_price:
            raise forms.ValidationError(
                "El precio de costo no puede ser mayor al precio de venta."
            )
        return cleaned_data


class CSVImportForm(forms.Form):
    file = forms.FileField(
        label="Archivo CSV",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".csv"})
    )
