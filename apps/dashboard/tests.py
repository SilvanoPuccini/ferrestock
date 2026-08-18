from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.inventory.models import Category, Product
from apps.movements.models import StockMovement
from apps.suppliers.models import Supplier


class DashboardRoleContextTests(TestCase):
    def setUp(self):
        call_command("setup_roles")

        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")

        self.product = Product.objects.create(
            code="DASH-001",
            name="Producto Crítico",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=1,
            stock_minimum=5,
            unit_measure="unidad",
        )

        self.operator = User.objects.create_user(username="dash_operator", password="Operator12345!")
        self.operator.groups.add(Group.objects.get(name="Operador"))

        self.consult = User.objects.create_user(username="dash_consult", password="Consult12345!")
        self.consult.groups.add(Group.objects.get(name="Consulta"))

    def test_operator_sees_critical_products(self):
        self.client.login(username="dash_operator", password="Operator12345!")
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product, list(response.context["critical_products"]))

    def test_consult_role_does_not_see_operational_widgets(self):
        self.client.login(username="dash_consult", password="Consult12345!")
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["critical_products"]), [])
        self.assertEqual(list(response.context["pending_receipt_orders"]), [])
        self.assertEqual(list(response.context["draft_purchase_orders"]), [])
        self.assertEqual(list(response.context["overdue_purchase_orders"]), [])
        self.assertEqual(list(response.context["latest_movements"]), [])
        self.assertEqual(list(response.context["latest_purchase_orders"]), [])

    def test_consult_role_still_sees_read_metrics(self):
        self.client.login(username="dash_consult", password="Consult12345!")
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.context["total_products"], 1)
        self.assertEqual(response.context["low_stock_count"], 1)


class DashboardStaleProductsTests(TestCase):
    def setUp(self):
        call_command("setup_roles")

        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")
        self.operator_user = User.objects.create_user(username="dash_op_stale", password="Operator12345!")
        self.operator_user.groups.add(Group.objects.get(name="Operador"))

        self.stale_product = Product.objects.create(
            code="DASH-STALE-001",
            name="Producto Sin Movimientos",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=5,
            stock_minimum=1,
            unit_measure="unidad",
        )

    def test_dashboard_includes_stale_products(self):
        self.client.login(username="dash_op_stale", password="Operator12345!")
        response = self.client.get(reverse("dashboard:home"))
        self.assertIn(self.stale_product, list(response.context["stale_products"]))
