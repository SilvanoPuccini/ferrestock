from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from apps.inventory.models import Product, Category
from apps.movements.models import StockMovement
from apps.suppliers.models import Supplier, PurchaseOrder


@login_required
def dashboard_home(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    total_purchase_orders = PurchaseOrder.objects.count()
    low_stock_count = Product.objects.filter(stock_current__lte=F("stock_minimum")).count()
    latest_movements = StockMovement.objects.select_related("product", "user")[:5]
    latest_purchase_orders = PurchaseOrder.objects.select_related("supplier")[:5]
    low_stock_products = Product.objects.filter(
        stock_current__lte=F("stock_minimum")
    ).select_related("category")[:5]

    movement_type_rows = (
        StockMovement.objects.values("movement_type")
        .annotate(total=Count("id"))
        .order_by("movement_type")
    )
    movement_labels_map = dict(StockMovement.MOVEMENT_TYPES)
    movement_type_labels = [movement_labels_map[row["movement_type"]] for row in movement_type_rows]
    movement_type_counts = [row["total"] for row in movement_type_rows]

    start_date = timezone.now() - timedelta(days=30)
    daily_rows = (
        StockMovement.objects.filter(created_at__gte=start_date)
        .annotate(day=TruncDate("created_at"))
        .values("day", "movement_type")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    days = sorted({row["day"] for row in daily_rows})
    movement_daily_labels = [day.strftime("%d/%m") for day in days]
    day_index = {day: index for index, day in enumerate(days)}

    entry_series = [0] * len(days)
    exit_series = [0] * len(days)
    adjustment_series = [0] * len(days)

    for row in daily_rows:
        index = day_index[row["day"]]
        if row["movement_type"] == StockMovement.ENTRY:
            entry_series[index] = row["total"]
        elif row["movement_type"] == StockMovement.EXIT:
            exit_series[index] = row["total"]
        elif row["movement_type"] == StockMovement.ADJUSTMENT:
            adjustment_series[index] = row["total"]

    context = {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_suppliers": total_suppliers,
        "total_purchase_orders": total_purchase_orders,
        "low_stock_count": low_stock_count,
        "latest_movements": latest_movements,
        "latest_purchase_orders": latest_purchase_orders,
        "low_stock_products": low_stock_products,
        "movement_type_labels": movement_type_labels,
        "movement_type_counts": movement_type_counts,
        "movement_daily_labels": movement_daily_labels,
        "entry_series": entry_series,
        "exit_series": exit_series,
        "adjustment_series": adjustment_series,
    }
    return render(request, "dashboard/home.html", context)
