from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Product

from .forms import PurchaseOrderItemForm
from .models import PurchaseOrder, PurchaseOrderItem, ProductSupplier, Supplier


class PurchaseOrderReceiveTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")
        self.user = User.objects.create_user(username="po_user", password="Po12345!")
        self.product = Product.objects.create(
            code="PO-001",
            name="Producto Orden",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=5,
            stock_minimum=1,
            unit_measure="unidad",
        )
        self.order = PurchaseOrder.objects.create(
            number="OC-001",
            supplier=self.supplier,
            created_by=self.user,
        )
        PurchaseOrderItem.objects.create(
            purchase_order=self.order,
            product=self.product,
            quantity=8,
            unit_price=Decimal("10.00"),
        )

    def test_receive_updates_stock_and_status(self):
        self.order.receive(self.user)
        self.product.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.product.stock_current, 13)
        self.assertEqual(self.order.status, PurchaseOrder.RECEIVED)

    def test_reverse_receive_restores_stock_and_status(self):
        self.order.receive(self.user)
        self.order.reverse_receive(self.user)
        self.product.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.product.stock_current, 5)
        self.assertEqual(self.order.status, PurchaseOrder.SENT)

    def test_reverse_receive_requires_received_status(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            self.order.reverse_receive(self.user)


class SupplierProtectedDeleteTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Protegido")
        self.admin = User.objects.create_superuser(
            username="admin_supplier", password="Admin12345!", email="a@a.com"
        )
        Product.objects.create(
            code="SUP-001",
            name="Producto Con Proveedor",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=5,
            stock_minimum=1,
            unit_measure="unidad",
        )

    def test_deleting_supplier_with_products_shows_friendly_error(self):
        self.client.login(username="admin_supplier", password="Admin12345!")
        url = reverse("suppliers:supplier_delete", kwargs={"pk": self.supplier.pk})
        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 500)
        self.assertTrue(Supplier.objects.filter(pk=self.supplier.pk).exists())


class PurchaseOrderItemFormProductQuerysetTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")
        self.admin = User.objects.create_superuser(
            username="admin_form", password="Admin12345!", email="a@a.com"
        )
        self.order = PurchaseOrder.objects.create(
            number="OC-FORM-001",
            supplier=self.supplier,
            created_by=self.admin,
        )
        self.linked_product = Product.objects.create(
            code="FORM-001",
            name="Producto Vinculado",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=5,
            stock_minimum=1,
            unit_measure="unidad",
        )

    def test_help_text_warns_when_no_supplier_links_exist(self):
        form = PurchaseOrderItemForm(purchase_order=self.order)
        self.assertTrue(form.fields["product"].help_text)

    def test_help_text_is_empty_when_supplier_links_exist(self):
        ProductSupplier.objects.create(
            product=self.linked_product,
            supplier=self.supplier,
            purchase_price=Decimal("8.00"),
        )
        form = PurchaseOrderItemForm(purchase_order=self.order)
        self.assertFalse(form.fields["product"].help_text)


class SupplierCSVImportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin_supplier_csv", password="Admin12345!", email="a@a.com"
        )
        self.client.login(username="admin_supplier_csv", password="Admin12345!")

    def _csv_file(self, content):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(
            "proveedores.csv", content.encode("utf-8"), content_type="text/csv"
        )

    def test_supplier_import_creates_and_updates(self):
        Supplier.objects.create(name="Existente", email="old@x.com")
        content = (
            "name,email,phone,address,contact_person,is_active\n"
            "Existente,new@x.com,123,Calle 1,Juan,true\n"
            "Nuevo Proveedor,nuevo@x.com,456,Calle 2,Ana,true\n"
        )
        response = self.client.post(
            reverse("suppliers:supplier_import"), {"file": self._csv_file(content)}
        )
        self.assertEqual(response.status_code, 302)
        existente = Supplier.objects.get(name="Existente")
        self.assertEqual(existente.email, "new@x.com")
        self.assertTrue(Supplier.objects.filter(name="Nuevo Proveedor").exists())

    def test_supplier_import_reports_row_error_without_crashing(self):
        content = "name,email,phone,address,contact_person,is_active\n,x@x.com,1,dir,juan,true\n"
        response = self.client.post(
            reverse("suppliers:supplier_import"), {"file": self._csv_file(content)}
        )
        self.assertEqual(response.status_code, 302)


class PurchaseOrderActionGetRequestTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")
        self.admin = User.objects.create_superuser(
            username="admin_action", password="Admin12345!", email="a@a.com"
        )
        self.client.login(username="admin_action", password="Admin12345!")
        self.order = PurchaseOrder.objects.create(
            number="OC-GET-001",
            supplier=self.supplier,
            created_by=self.admin,
        )

    def test_get_to_mark_sent_does_not_change_status_silently(self):
        response = self.client.get(
            reverse("suppliers:purchase_order_send", kwargs={"pk": self.order.pk})
        )
        self.assertEqual(response.status_code, 405)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, PurchaseOrder.DRAFT)

    def test_get_to_receive_returns_405(self):
        response = self.client.get(
            reverse("suppliers:purchase_order_receive", kwargs={"pk": self.order.pk})
        )
        self.assertEqual(response.status_code, 405)

    def test_get_to_cancel_returns_405(self):
        response = self.client.get(
            reverse("suppliers:purchase_order_cancel", kwargs={"pk": self.order.pk})
        )
        self.assertEqual(response.status_code, 405)

    def test_get_to_reverse_receive_returns_405(self):
        response = self.client.get(
            reverse("suppliers:purchase_order_reverse_receive", kwargs={"pk": self.order.pk})
        )
        self.assertEqual(response.status_code, 405)
