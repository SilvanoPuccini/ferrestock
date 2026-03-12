from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("stock/", views.StockReportView.as_view(), name="stock_report"),
    path("stock/export/csv/", views.export_stock_csv, name="stock_report_csv"),
    path("stock/export/xlsx/", views.export_stock_xlsx, name="stock_report_xlsx"),
    path("stock/export/pdf/", views.export_stock_pdf, name="stock_report_pdf"),

    path("movements/", views.MovementReportView.as_view(), name="movement_report"),
    path("movements/export/csv/", views.export_movements_csv, name="movement_report_csv"),
    path("movements/export/xlsx/", views.export_movements_xlsx, name="movement_report_xlsx"),
    path("movements/export/pdf/", views.export_movements_pdf, name="movement_report_pdf"),

    path("purchases/", views.PurchaseOrderReportView.as_view(), name="purchase_report"),
    path("purchases/export/csv/", views.export_purchase_orders_csv, name="purchase_report_csv"),
    path("purchases/export/xlsx/", views.export_purchase_orders_xlsx, name="purchase_report_xlsx"),
    path("purchases/export/pdf/", views.export_purchase_orders_pdf, name="purchase_report_pdf"),
]
