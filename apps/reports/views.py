import csv
import io
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from apps.core.mixins import AppPermissionMixin
from apps.inventory.models import Product, Category
from apps.suppliers.models import Supplier


def get_filtered_products(request):
    queryset = Product.objects.select_related("category", "supplier").order_by("name")

    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    supplier_id = request.GET.get("supplier", "").strip()
    low_stock = request.GET.get("low_stock", "").strip()
    is_active = request.GET.get("is_active", "").strip()

    if q:
        queryset = queryset.filter(
            models.Q(name__icontains=q)
            | models.Q(code__icontains=q)
            | models.Q(barcode__icontains=q)
        )

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if supplier_id:
        queryset = queryset.filter(supplier_id=supplier_id)

    if low_stock:
        queryset = queryset.filter(stock_current__lte=models.F("stock_minimum"))

    if is_active == "1":
        queryset = queryset.filter(is_active=True)
    elif is_active == "0":
        queryset = queryset.filter(is_active=False)

    return queryset


# Django ORM helpers
from django.db import models  # se deja aquí para evitar mezclar imports si ya vienes tocando mucho el proyecto


class StockReportView(AppPermissionMixin, TemplateView):
    permission_required = "inventory.view_product"
    template_name = "reports/stock_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = get_filtered_products(self.request)

        params = self.request.GET.copy()
        export_querystring = params.urlencode()

        context["products"] = products
        context["categories"] = Category.objects.filter(is_active=True).order_by("name")
        context["suppliers"] = Supplier.objects.filter(is_active=True).order_by("name")

        context["selected_q"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_supplier"] = self.request.GET.get("supplier", "")
        context["selected_low_stock"] = self.request.GET.get("low_stock", "")
        context["selected_is_active"] = self.request.GET.get("is_active", "")

        context["total_products"] = products.count()
        context["total_low_stock"] = products.filter(stock_current__lte=models.F("stock_minimum")).count()
        context["export_querystring"] = export_querystring

        return context


@login_required
def export_stock_csv(request):
    if not request.user.has_perm("inventory.view_product"):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    products = get_filtered_products(request)

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="ferrestock_stock_report.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow([
        "Codigo",
        "Nombre",
        "Categoria",
        "Proveedor",
        "Stock actual",
        "Stock minimo",
        "Unidad",
        "Estado",
        "Stock bajo",
    ])

    for product in products:
        writer.writerow([
            product.code,
            product.name,
            product.category.name,
            product.supplier.name,
            product.stock_current,
            product.stock_minimum,
            product.get_unit_measure_display(),
            "Activo" if product.is_active else "Inactivo",
            "Si" if product.is_low_stock else "No",
        ])

    return response


@login_required
def export_stock_xlsx(request):
    if not request.user.has_perm("inventory.view_product"):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    products = get_filtered_products(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Stock"

    headers = [
        "Código",
        "Nombre",
        "Categoría",
        "Proveedor",
        "Stock actual",
        "Stock mínimo",
        "Unidad",
        "Estado",
        "Stock bajo",
    ]
    ws.append(headers)

    header_fill = PatternFill(fill_type="solid", fgColor="1F2937")
    header_font = Font(color="FFFFFF", bold=True)

    for col_num, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font

    for product in products:
        ws.append([
            product.code,
            product.name,
            product.category.name,
            product.supplier.name,
            product.stock_current,
            product.stock_minimum,
            product.get_unit_measure_display(),
            "Activo" if product.is_active else "Inactivo",
            "Sí" if product.is_low_stock else "No",
        ])

    widths = {
        "A": 18,
        "B": 28,
        "C": 20,
        "D": 24,
        "E": 14,
        "F": 14,
        "G": 14,
        "H": 14,
        "I": 12,
    }

    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return FileResponse(
        output,
        as_attachment=True,
        filename="ferrestock_stock_report.xlsx",
    )


@login_required
def export_stock_pdf(request):
    if not request.user.has_perm("inventory.view_product"):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    products = get_filtered_products(request)

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("FerreStock - Reporte de Stock", styles["Title"])
    subtitle = Paragraph(
        f"Generado: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"],
    )

    elements.append(title)
    elements.append(Spacer(1, 6))
    elements.append(subtitle)
    elements.append(Spacer(1, 12))

    data = [[
        "Código",
        "Nombre",
        "Categoría",
        "Proveedor",
        "Stock",
        "Mínimo",
        "Unidad",
        "Estado",
        "Bajo",
    ]]

    for product in products:
        data.append([
            product.code,
            product.name,
            product.category.name,
            product.supplier.name,
            str(product.stock_current),
            str(product.stock_minimum),
            product.get_unit_measure_display(),
            "Activo" if product.is_active else "Inactivo",
            "Sí" if product.is_low_stock else "No",
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[22 * mm, 50 * mm, 32 * mm, 40 * mm, 18 * mm, 18 * mm, 22 * mm, 20 * mm, 16 * mm],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename="ferrestock_stock_report.pdf",
    )
