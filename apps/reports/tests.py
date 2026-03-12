from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Product
from apps.movements.models import StockMovement
from apps.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem


class StockReportTests(TestCase):
    def setUp(self):
        call_command("setup_roles")

        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")

        Product.objects.create(
            code="P001",
            name="Martillo",
            category=self.category,
            supplier=self.supplier,
            cost_price=10,
            sale_price=20,
            stock_current=5,
            stock_minimum=10,
            unit_measure="unidad",
            is_active=True,
        )

        self.user = User.objects.create_user(
            username="report_user",
            password="Test12345!"
        )

        group = Group.objects.get(name="Consulta")
        self.user.groups.add(group)

    def test_stock_report_requires_login(self):
        response = self.client.get(reverse("reports:stock_report"))
        self.assertEqual(response.status_code, 302)

    def test_stock_report_page_for_authorized_user(self):
        self.client.login(username="report_user", password="Test12345!")
        response = self.client.get(reverse("reports:stock_report"))
        self.assertEqual(response.status_code, 200)

    def test_stock_report_csv_export(self):
        self.client.login(username="report_user", password="Test12345!")
        response = self.client.get(reverse("reports:stock_report_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("ferrestock_stock_report.csv", response["Content-Disposition"])

    def test_stock_report_filter_low_stock(self):
        self.client.login(username="report_user", password="Test12345!")
        response = self.client.get(reverse("reports:stock_report"), {"low_stock": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Martillo")

    def test_stock_report_xlsx_export(self):
        self.client.login(username="report_user", password="Test12345!")
        response = self.client.get(reverse("reports:stock_report_xlsx"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            response["Content-Type"],
        )

    def test_stock_report_pdf_export(self):
        self.client.login(username="report_user", password="Test12345!")
        response = self.client.get(reverse("reports:stock_report_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response["Content-Type"])


class MovementReportTests(TestCase):
    def setUp(self):
        call_command("setup_roles")

        self.category = Category.objects.create(name="Electricidad")
        self.supplier = Supplier.objects.create(name="Proveedor Mov")
        self.product = Product.objects.create(
            code="E001",
            name="Cable",
            category=self.category,
            supplier=self.supplier,
            cost_price=100,
            sale_price=150,
            stock_current=20,
            stock_minimum=5,
            unit_measure="metro",
            is_active=True,
        )

        self.user = User.objects.create_user(
            username="movement_user",
            password="Test12345!"
        )

        group = Group.objects.get(name="Consulta")
        self.user.groups.add(group)

        StockMovement.objects.create(
            product=self.product,
            movement_type=StockMovement.ENTRY,
            quantity=10,
            reason="Ingreso inicial",
            reference="INI-001",
            user=self.user,
        )

    def test_movement_report_requires_login(self):
        response = self.client.get(reverse("reports:movement_report"))
        self.assertEqual(response.status_code, 302)

    def test_movement_report_page_for_authorized_user(self):
        self.client.login(username="movement_user", password="Test12345!")
        response = self.client.get(reverse("reports:movement_report"))
        self.assertEqual(response.status_code, 200)

    def test_movement_report_csv_export(self):
        self.client.login(username="movement_user", password="Test12345!")
        response = self.client.get(reverse("reports:movement_report_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_movement_report_filter_by_type(self):
        self.client.login(username="movement_user", password="Test12345!")
        response = self.client.get(reverse("reports:movement_report"), {"movement_type": "entrada"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cable")

    def test_movement_report_xlsx_export(self):
        self.client.login(username="movement_user", password="Test12345!")
        response = self.client.get(reverse("reports:movement_report_xlsx"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            response["Content-Type"],
        )

    def test_movement_report_pdf_export(self):
        self.client.login(username="movement_user", password="Test12345!")
        response = self.client.get(reverse("reports:movement_report_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response["Content-Type"])


class PurchaseReportTests(TestCase):
    def setUp(self):
        call_command("setup_roles")

        self.category = Category.objects.create(name="Pinturas")
        self.supplier = Supplier.objects.create(name="Proveedor Compra")
        self.product = Product.objects.create(
            code="PINT-01",
            name="Pintura Blanca",
            category=self.category,
            supplier=self.supplier,
            cost_price=50,
            sale_price=80,
            stock_current=12,
            stock_minimum=4,
            unit_measure="litro",
            is_active=True,
        )

        self.user = User.objects.create_user(
            username="purchase_user",
            password="Test12345!"
        )

        group = Group.objects.get(name="Consulta")
        self.user.groups.add(group)

        self.order = PurchaseOrder.objects.create(
            number="OC-TEST-001",
            supplier=self.supplier,
            status=PurchaseOrder.DRAFT,
            created_by=self.user,
        )

        PurchaseOrderItem.objects.create(
            purchase_order=self.order,
            product=self.product,
            quantity=3,
            unit_price=55,
        )

    def test_purchase_report_requires_login(self):
        response = self.client.get(reverse("reports:purchase_report"))
        self.assertEqual(response.status_code, 302)

    def test_purchase_report_page_for_authorized_user(self):
        self.client.login(username="purchase_user", password="Test12345!")
        response = self.client.get(reverse("reports:purchase_report"))
        self.assertEqual(response.status_code, 200)

    def test_purchase_report_csv_export(self):
        self.client.login(username="purchase_user", password="Test12345!")
        response = self.client.get(reverse("reports:purchase_report_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_purchase_report_filter_by_status(self):
        self.client.login(username="purchase_user", password="Test12345!")
        response = self.client.get(reverse("reports:purchase_report"), {"status": "draft"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OC-TEST-001")

    def test_purchase_report_xlsx_export(self):
        self.client.login(username="purchase_user", password="Test12345!")
        response = self.client.get(reverse("reports:purchase_report_xlsx"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            response["Content-Type"],
        )

    def test_purchase_report_pdf_export(self):
        self.client.login(username="purchase_user", password="Test12345!")
        response = self.client.get(reverse("reports:purchase_report_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response["Content-Type"])
