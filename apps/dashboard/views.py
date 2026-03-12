from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render

from apps.inventory.models import Product, Category
from apps.movements.models import StockMovement
from apps.suppliers.models import Supplier


@login_required
def dashboard_home(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    low_stock_count = Product.objects.filter(stock_current__lte=F("stock_minimum")).count()
    latest_movements = StockMovement.objects.select_related("product", "user")[:5]
    low_stock_products = Product.objects.filter(stock_current__lte=F("stock_minimum")).select_related("category")[:5]

    context = {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_suppliers": total_suppliers,
        "low_stock_count": low_stock_count,
        "latest_movements": latest_movements,
        "low_stock_products": low_stock_products,
    }
    return render(request, "dashboard/home.html", context)
