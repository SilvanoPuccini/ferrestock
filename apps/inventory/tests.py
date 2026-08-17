from decimal import Decimal
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.movements.models import StockMovement
from apps.suppliers.models import ProductSupplier, Supplier

from .forms import ProductCreateForm
from .models import Category, Product


class ProductStockValidatorsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")

    def _build_product(self, **overrides):
        data = dict(
            code="INV-001",
            name="Producto Test",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=5,
            stock_minimum=2,
            unit_measure="unidad",
        )
        data.update(overrides)
        return Product(**data)

    def test_negative_stock_current_is_rejected(self):
        product = self._build_product(stock_current=-1)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_negative_stock_minimum_is_rejected(self):
        product = self._build_product(stock_minimum=-1)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_zero_stock_is_allowed(self):
        product = self._build_product(stock_current=0, stock_minimum=0)
        product.full_clean()


class ProductPriceFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")

    def _form_data(self, **overrides):
        data = dict(
            code="INV-002",
            barcode="",
            name="Producto Test",
            description="",
            category=self.category.pk,
            supplier=self.supplier.pk,
            cost_price="20.00",
            sale_price="10.00",
            stock_current="5",
            stock_minimum="2",
            unit_measure="unidad",
            is_active=True,
        )
        data.update(overrides)
        return data

    def test_cost_price_above_sale_price_is_rejected(self):
        form = ProductCreateForm(data=self._form_data(cost_price="20.00", sale_price="10.00"))
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_cost_price_below_sale_price_is_valid(self):
        form = ProductCreateForm(data=self._form_data(cost_price="5.00", sale_price="10.00"))
        self.assertTrue(form.is_valid(), form.errors)


class ProductProtectedDeleteTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User

        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")
        self.user = User.objects.create_superuser(
            username="admin_protected", password="Admin12345!", email="a@a.com"
        )
        self.product = Product.objects.create(
            code="INV-003",
            name="Producto Protegido",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=10,
            stock_minimum=2,
            unit_measure="unidad",
        )
        StockMovement.objects.create(
            product=self.product,
            movement_type=StockMovement.ENTRY,
            quantity=5,
            reason="Carga inicial",
            user=self.user,
        )

    def test_deleting_category_with_products_shows_friendly_error(self):
        self.client.login(username="admin_protected", password="Admin12345!")
        url = reverse("inventory:category_delete", kwargs={"pk": self.category.pk})
        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 500)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_deleting_product_with_movements_shows_friendly_error(self):
        self.client.login(username="admin_protected", password="Admin12345!")
        url = reverse("inventory:product_delete", kwargs={"pk": self.product.pk})
        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 500)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())


class ProductCSVImportTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User

        self.user = User.objects.create_superuser(
            username="admin_csv", password="Admin12345!", email="a@a.com"
        )
        self.client.login(username="admin_csv", password="Admin12345!")

    def _csv_file(self, content):
        return SimpleUploadedFile(
            "productos.csv", content.encode("utf-8"), content_type="text/csv"
        )

    def test_negative_stock_row_is_rejected_and_not_created(self):
        content = (
            "code,name,category,supplier,cost_price,sale_price,stock_current,"
            "stock_minimum,unit_measure,barcode,description,is_active\n"
            "NEG-001,Producto Negativo,Herramientas,Proveedor CSV,5,10,-3,1,unidad,,,\n"
        )
        response = self.client.post(
            reverse("inventory:product_import"), {"file": self._csv_file(content)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(code="NEG-001").exists())

    def test_row_failure_after_product_save_rolls_back_completely(self):
        content = (
            "code,name,category,supplier,cost_price,sale_price,stock_current,"
            "stock_minimum,unit_measure,barcode,description,is_active\n"
            "OK-001,Producto Ok,Herramientas,Proveedor CSV,5,10,3,1,unidad,,,\n"
            "FAIL-001,Producto Falla,Herramientas,Proveedor CSV,5,10,3,1,unidad,,,\n"
        )

        original = ProductSupplier.objects.update_or_create

        def side_effect(*args, **kwargs):
            product = kwargs.get("product")
            if product is not None and product.code == "FAIL-001":
                raise RuntimeError("fallo simulado")
            return original(*args, **kwargs)

        with mock.patch(
            "apps.inventory.views.ProductSupplier.objects.update_or_create",
            side_effect=side_effect,
        ):
            response = self.client.post(
                reverse("inventory:product_import"), {"file": self._csv_file(content)}
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(code="OK-001").exists())
        self.assertFalse(Product.objects.filter(code="FAIL-001").exists())
