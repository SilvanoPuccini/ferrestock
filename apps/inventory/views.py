import csv
from decimal import Decimal
from io import TextIOWrapper

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from apps.core.mixins import AppPermissionMixin
from apps.core.utils import log_audit_action
from apps.movements.models import StockMovement
from apps.suppliers.models import Supplier, ProductSupplier
from .forms import CategoryForm, ProductCreateForm, ProductUpdateForm, CSVImportForm
from .models import Category, Product


def parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí"}


def parse_decimal(value, default="0"):
    text = str(value).strip()
    return Decimal(text or default)


def parse_int(value, default=0):
    text = str(value).strip()
    return int(text or default)


class CategoryListView(AppPermissionMixin, ListView):
    permission_required = "inventory.view_category"
    model = Category
    template_name = "inventory/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(AppPermissionMixin, SuccessMessageMixin, CreateView):
    permission_required = "inventory.add_category"
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("inventory:category_list")
    success_message = "La categoría fue creada correctamente."


class CategoryUpdateView(AppPermissionMixin, SuccessMessageMixin, UpdateView):
    permission_required = "inventory.change_category"
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("inventory:category_list")
    success_message = "La categoría fue actualizada correctamente."


class CategoryDeleteView(AppPermissionMixin, DeleteView):
    permission_required = "inventory.delete_category"
    model = Category
    template_name = "inventory/category_confirm_delete.html"
    success_url = reverse_lazy("inventory:category_list")


class ProductListView(AppPermissionMixin, ListView):
    permission_required = "inventory.view_product"
    model = Product
    template_name = "inventory/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = Product.objects.select_related("category", "supplier").order_by("name")

        search = self.request.GET.get("q")
        category_id = self.request.GET.get("category")
        supplier_id = self.request.GET.get("supplier")
        low_stock = self.request.GET.get("low_stock")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(barcode__icontains=search)
            )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)

        if low_stock:
            queryset = queryset.filter(stock_current__lte=models.F("stock_minimum"))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_products = Product.objects.all()
        low_stock_products = Product.objects.filter(stock_current__lte=models.F("stock_minimum"))
        inactive_products = Product.objects.filter(is_active=False)

        context["categories"] = Category.objects.filter(is_active=True).order_by("name")
        context["suppliers"] = Supplier.objects.filter(is_active=True).order_by("name")
        context["selected_q"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_supplier"] = self.request.GET.get("supplier", "")
        context["selected_low_stock"] = self.request.GET.get("low_stock", "")

        context["total_products"] = all_products.count()
        context["total_low_stock"] = low_stock_products.count()
        context["total_active_products"] = all_products.filter(is_active=True).count()
        context["total_inactive_products"] = inactive_products.count()

        return context


class ProductDetailView(AppPermissionMixin, DetailView):
    permission_required = "inventory.view_product"
    model = Product
    template_name = "inventory/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category", "supplier").prefetch_related("supplier_links__supplier")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["supplier_links"] = self.object.supplier_links.select_related("supplier").order_by("-is_primary", "supplier__name")
        context["latest_movements"] = self.object.movements.select_related("user").all()[:8]
        return context


class ProductCreateView(AppPermissionMixin, SuccessMessageMixin, CreateView):
    permission_required = "inventory.add_product"
    model = Product
    form_class = ProductCreateForm
    template_name = "inventory/product_form.html"
    success_message = "El producto fue creado correctamente."

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit_action(
            user=self.request.user,
            module="inventory",
            action="create",
            object_type="Product",
            object_id=self.object.pk,
            object_repr=str(self.object),
            description="Producto creado desde frontend.",
        )
        return response

    def get_success_url(self):
        return reverse_lazy("inventory:product_detail", kwargs={"pk": self.object.pk})


class ProductUpdateView(AppPermissionMixin, SuccessMessageMixin, UpdateView):
    permission_required = "inventory.change_product"
    model = Product
    form_class = ProductUpdateForm
    template_name = "inventory/product_form.html"
    success_message = "El producto fue actualizado correctamente."

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit_action(
            user=self.request.user,
            module="inventory",
            action="update",
            object_type="Product",
            object_id=self.object.pk,
            object_repr=str(self.object),
            description="Producto actualizado desde frontend.",
        )
        return response

    def get_success_url(self):
        return reverse_lazy("inventory:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(AppPermissionMixin, DeleteView):
    permission_required = "inventory.delete_product"
    model = Product
    template_name = "inventory/product_confirm_delete.html"
    success_url = reverse_lazy("inventory:product_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_id = self.object.pk
        object_repr = str(self.object)
        response = super().delete(request, *args, **kwargs)
        log_audit_action(
            user=request.user,
            module="inventory",
            action="delete",
            object_type="Product",
            object_id=object_id,
            object_repr=object_repr,
            description="Producto eliminado desde frontend.",
        )
        return response


@login_required
def import_products_csv(request):
    if not request.user.has_perms(["inventory.add_product", "inventory.change_product"]):
        raise PermissionDenied

    required_columns = [
        "code",
        "name",
        "category",
        "supplier",
        "cost_price",
        "sale_price",
        "stock_current",
        "stock_minimum",
        "unit_measure",
        "barcode",
        "description",
        "is_active",
    ]

    if request.method == "POST":
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["file"]

            if not csv_file.name.lower().endswith(".csv"):
                messages.error(request, "Debes subir un archivo con extensión .csv")
                return redirect("inventory:product_import")

            decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
            reader = csv.DictReader(decoded_file)

            if reader.fieldnames is None:
                messages.error(request, "El archivo CSV no tiene encabezados válidos.")
                return redirect("inventory:product_import")

            missing = [col for col in required_columns if col not in reader.fieldnames]
            if missing:
                messages.error(request, f"Faltan columnas obligatorias: {', '.join(missing)}")
                return redirect("inventory:product_import")

            created_count = 0
            updated_count = 0
            error_rows = []

            for row_number, row in enumerate(reader, start=2):
                try:
                    code = row["code"].strip()
                    name = row["name"].strip()
                    category_name = row["category"].strip()
                    supplier_name = row["supplier"].strip()

                    if not code or not name or not category_name or not supplier_name:
                        raise ValueError("code, name, category y supplier son obligatorios.")

                    category, _ = Category.objects.get_or_create(
                        name=category_name,
                        defaults={"is_active": True},
                    )

                    supplier, _ = Supplier.objects.get_or_create(
                        name=supplier_name,
                        defaults={"is_active": True},
                    )

                    barcode = row.get("barcode", "").strip() or None
                    description = row.get("description", "").strip()
                    cost_price = parse_decimal(row.get("cost_price", "0"))
                    sale_price = parse_decimal(row.get("sale_price", "0"))
                    stock_current = parse_int(row.get("stock_current", "0"))
                    stock_minimum = parse_int(row.get("stock_minimum", "0"))
                    unit_measure = row.get("unit_measure", "unidad").strip().lower() or "unidad"
                    is_active = parse_bool(row.get("is_active", "true"))

                    valid_units = dict(Product.UNIT_CHOICES).keys()
                    if unit_measure not in valid_units:
                        unit_measure = "unidad"

                    product = Product.objects.filter(code=code).first()

                    if product:
                        product.name = name
                        product.description = description
                        product.category = category
                        product.supplier = supplier
                        product.cost_price = cost_price
                        product.sale_price = sale_price
                        product.stock_minimum = stock_minimum
                        product.unit_measure = unit_measure
                        product.is_active = is_active
                        if barcode:
                            product.barcode = barcode
                        product.save()
                        updated_count += 1
                    else:
                        product = Product.objects.create(
                            code=code,
                            barcode=barcode,
                            name=name,
                            description=description,
                            category=category,
                            supplier=supplier,
                            cost_price=cost_price,
                            sale_price=sale_price,
                            stock_current=stock_current,
                            stock_minimum=stock_minimum,
                            unit_measure=unit_measure,
                            is_active=is_active,
                        )
                        created_count += 1

                    ProductSupplier.objects.update_or_create(
                        product=product,
                        supplier=supplier,
                        defaults={
                            "purchase_price": cost_price,
                            "is_primary": supplier == product.supplier,
                        },
                    )

                except Exception as exc:
                    error_rows.append(f"Fila {row_number}: {exc}")

            log_audit_action(
                user=request.user,
                module="inventory",
                action="import",
                object_type="ProductCSV",
                object_repr="Importación masiva de productos",
                description="Importación CSV ejecutada.",
                metadata={
                    "created": created_count,
                    "updated": updated_count,
                    "errors": error_rows[:10],
                },
            )

            if created_count or updated_count:
                messages.success(
                    request,
                    f"Importación finalizada. Creados: {created_count}. Actualizados: {updated_count}."
                )

            if error_rows:
                preview = " | ".join(error_rows[:5])
                messages.warning(request, f"Se encontraron errores: {preview}")

            return redirect("inventory:product_list")
    else:
        form = CSVImportForm()

    return render(
        request,
        "inventory/product_import.html",
        {
            "form": form,
            "required_columns": required_columns,
        },
    )
