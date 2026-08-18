from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Product
from apps.suppliers.models import Supplier

from .models import StockMovement


class StockMovementSaveTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")
        self.user = User.objects.create_user(username="mov_user", password="Mov12345!")
        self.product = Product.objects.create(
            code="MOV-001",
            name="Producto Movimiento",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=10,
            stock_minimum=2,
            unit_measure="unidad",
        )

    def test_entry_movement_increases_stock(self):
        StockMovement.objects.create(
            product=self.product,
            movement_type=StockMovement.ENTRY,
            quantity=5,
            reason="Ingreso de mercadería",
            user=self.user,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_current, 15)

    def test_exit_movement_decreases_stock(self):
        StockMovement.objects.create(
            product=self.product,
            movement_type=StockMovement.EXIT,
            quantity=4,
            reason="Venta",
            user=self.user,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_current, 6)

    def test_exit_movement_with_insufficient_stock_is_rejected(self):
        from django.core.exceptions import ValidationError

        movement = StockMovement(
            product=self.product,
            movement_type=StockMovement.EXIT,
            quantity=self.product.stock_current + 1,
            reason="Salida excesiva",
            user=self.user,
        )
        with self.assertRaises(ValidationError):
            movement.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_current, 10)

    def test_adjustment_movement_sets_absolute_stock(self):
        StockMovement.objects.create(
            product=self.product,
            movement_type=StockMovement.ADJUSTMENT,
            quantity=100,
            reason="Conteo físico",
            user=self.user,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_current, 100)


class StockMovementDetailViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Herramientas")
        self.supplier = Supplier.objects.create(name="Proveedor Test")
        self.user = User.objects.create_superuser(
            username="detail_user", password="Detail12345!", email="d@d.com"
        )
        self.product = Product.objects.create(
            code="DET-001",
            name="Producto Detalle",
            category=self.category,
            supplier=self.supplier,
            cost_price=Decimal("10.00"),
            sale_price=Decimal("20.00"),
            stock_current=10,
            stock_minimum=2,
            unit_measure="unidad",
        )
        self.movement = StockMovement.objects.create(
            product=self.product,
            movement_type=StockMovement.ENTRY,
            quantity=5,
            reason="Ingreso de mercadería",
            user=self.user,
        )

    def test_movement_detail_returns_200_and_shows_data(self):
        self.client.login(username="detail_user", password="Detail12345!")
        response = self.client.get(reverse("movements:movement_detail", kwargs={"pk": self.movement.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Producto Detalle")
        self.assertContains(response, "Ingreso de mercadería")
