from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Product

from .models import PurchaseOrder, PurchaseOrderItem, Supplier


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
