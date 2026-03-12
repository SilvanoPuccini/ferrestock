from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Product
from apps.suppliers.models import Supplier, PurchaseOrder


class RolePermissionTests(TestCase):
    def setUp(self):
        call_command("setup_roles")

        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Permisos")
        self.product = Product.objects.create(
            code="PX-001",
            name="Producto Permisos",
            category=self.category,
            supplier=self.supplier,
            cost_price=10,
            sale_price=20,
            stock_current=15,
            stock_minimum=5,
            unit_measure="unidad",
            is_active=True,
        )

        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="Admin12345!"
        )
        self.operator_user = User.objects.create_user(
            username="operator_test",
            password="Operator12345!"
        )
        self.consult_user = User.objects.create_user(
            username="consult_test",
            password="Consult12345!"
        )

        self.admin_user.groups.add(Group.objects.get(name="Administrador"))
        self.operator_user.groups.add(Group.objects.get(name="Operador"))
        self.consult_user.groups.add(Group.objects.get(name="Consulta"))

        self.purchase_order = PurchaseOrder.objects.create(
            number="OC-PERM-001",
            supplier=self.supplier,
            created_by=self.admin_user,
        )

    def test_anonymous_user_redirected_from_protected_view(self):
        response = self.client.get(reverse("inventory:product_list"))
        self.assertEqual(response.status_code, 302)

    def test_consult_can_view_stock(self):
        self.client.login(username="consult_test", password="Consult12345!")
        response = self.client.get(reverse("inventory:product_list"))
        self.assertEqual(response.status_code, 200)

    def test_consult_cannot_create_product(self):
        self.client.login(username="consult_test", password="Consult12345!")
        response = self.client.get(reverse("inventory:product_create"))
        self.assertEqual(response.status_code, 403)

    def test_consult_cannot_create_movement(self):
        self.client.login(username="consult_test", password="Consult12345!")
        response = self.client.get(reverse("movements:movement_create"))
        self.assertEqual(response.status_code, 403)

    def test_consult_cannot_create_purchase_order(self):
        self.client.login(username="consult_test", password="Consult12345!")
        response = self.client.get(reverse("suppliers:purchase_order_create"))
        self.assertEqual(response.status_code, 403)

    def test_operator_can_create_movement(self):
        self.client.login(username="operator_test", password="Operator12345!")
        response = self.client.get(reverse("movements:movement_create"))
        self.assertEqual(response.status_code, 200)

    def test_operator_can_create_purchase_order(self):
        self.client.login(username="operator_test", password="Operator12345!")
        response = self.client.get(reverse("suppliers:purchase_order_create"))
        self.assertEqual(response.status_code, 200)

    def test_operator_cannot_create_product(self):
        self.client.login(username="operator_test", password="Operator12345!")
        response = self.client.get(reverse("inventory:product_create"))
        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_send_purchase_order(self):
        self.client.login(username="operator_test", password="Operator12345!")
        response = self.client.post(reverse("suppliers:purchase_order_send", kwargs={"pk": self.purchase_order.pk}))
        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_receive_purchase_order(self):
        self.client.login(username="operator_test", password="Operator12345!")
        response = self.client.post(reverse("suppliers:purchase_order_receive", kwargs={"pk": self.purchase_order.pk}))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_product(self):
        self.client.login(username="admin_test", password="Admin12345!")
        response = self.client.get(reverse("inventory:product_create"))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_purchase_send_action(self):
        self.client.login(username="admin_test", password="Admin12345!")
        response = self.client.post(reverse("suppliers:purchase_order_send", kwargs={"pk": self.purchase_order.pk}))
        self.assertEqual(response.status_code, 302)
