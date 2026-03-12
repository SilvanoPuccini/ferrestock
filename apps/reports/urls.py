from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("stock/", views.StockReportView.as_view(), name="stock_report"),
    path("stock/export/csv/", views.export_stock_csv, name="stock_report_csv"),
    path("stock/export/xlsx/", views.export_stock_xlsx, name="stock_report_xlsx"),
    path("stock/export/pdf/", views.export_stock_pdf, name="stock_report_pdf"),
]
