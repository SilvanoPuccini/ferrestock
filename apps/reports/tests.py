from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Product
from apps.suppliers.models import Supplier


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
