from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

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
