from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from apps.suppliers.models import Supplier
from .forms import CategoryForm, ProductCreateForm, ProductUpdateForm
from .models import Category, Product


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "inventory/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("inventory:category_list")
    success_message = "La categoría fue creada correctamente."


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("inventory:category_list")
    success_message = "La categoría fue actualizada correctamente."


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "inventory/category_confirm_delete.html"
    success_url = reverse_lazy("inventory:category_list")


class ProductListView(LoginRequiredMixin, ListView):
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
        context["categories"] = Category.objects.filter(is_active=True).order_by("name")
        context["suppliers"] = Supplier.objects.filter(is_active=True).order_by("name")
        context["selected_q"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_supplier"] = self.request.GET.get("supplier", "")
        context["selected_low_stock"] = self.request.GET.get("low_stock", "")
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "inventory/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category", "supplier")


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductCreateForm
    template_name = "inventory/product_form.html"
    success_message = "El producto fue creado correctamente."

    def get_success_url(self):
        return reverse_lazy("inventory:product_detail", kwargs={"pk": self.object.pk})


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = "inventory/product_form.html"
    success_message = "El producto fue actualizado correctamente."

    def get_success_url(self):
        return reverse_lazy("inventory:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "inventory/product_confirm_delete.html"
    success_url = reverse_lazy("inventory:product_list")
