from django.urls import path
from . import views

app_name = "suppliers"

urlpatterns = [
    path("", views.SupplierListView.as_view(), name="supplier_list"),
    path("create/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("<int:pk>/update/", views.SupplierUpdateView.as_view(), name="supplier_update"),
    path("<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),
]
