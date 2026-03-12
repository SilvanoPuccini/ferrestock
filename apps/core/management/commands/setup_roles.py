from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.core.models import AuditLog
from apps.inventory.models import Category, Product
from apps.movements.models import StockMovement
from apps.suppliers.models import Supplier, ProductSupplier, PurchaseOrder, PurchaseOrderItem


class Command(BaseCommand):
    help = "Crea o actualiza los grupos y permisos base de FerreStock."

    def get_perm(self, model, codename):
        content_type = ContentType.objects.get_for_model(model)
        return Permission.objects.get(content_type=content_type, codename=codename)

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="Administrador")
        operator_group, _ = Group.objects.get_or_create(name="Operador")
        consult_group, _ = Group.objects.get_or_create(name="Consulta")

        admin_perms = Permission.objects.filter(
            content_type__app_label__in=["core", "inventory", "suppliers", "movements"]
        )

        operator_perms = [
            self.get_perm(Product, "view_product"),
            self.get_perm(Category, "view_category"),
            self.get_perm(Supplier, "view_supplier"),
            self.get_perm(ProductSupplier, "view_productsupplier"),
            self.get_perm(PurchaseOrder, "view_purchaseorder"),
            self.get_perm(PurchaseOrder, "add_purchaseorder"),
            self.get_perm(PurchaseOrder, "change_purchaseorder"),
            self.get_perm(PurchaseOrderItem, "view_purchaseorderitem"),
            self.get_perm(PurchaseOrderItem, "add_purchaseorderitem"),
            self.get_perm(PurchaseOrderItem, "delete_purchaseorderitem"),
            self.get_perm(StockMovement, "view_stockmovement"),
            self.get_perm(StockMovement, "add_stockmovement"),
        ]

        consult_perms = [
            self.get_perm(Product, "view_product"),
            self.get_perm(Category, "view_category"),
            self.get_perm(Supplier, "view_supplier"),
            self.get_perm(ProductSupplier, "view_productsupplier"),
            self.get_perm(PurchaseOrder, "view_purchaseorder"),
            self.get_perm(PurchaseOrderItem, "view_purchaseorderitem"),
            self.get_perm(StockMovement, "view_stockmovement"),
        ]

        admin_group.permissions.set(admin_perms)
        operator_group.permissions.set(operator_perms)
        consult_group.permissions.set(consult_perms)

        self.stdout.write(self.style.SUCCESS("Roles creados/actualizados correctamente."))
        self.stdout.write("Grupos: Administrador, Operador, Consulta")
