from django.urls import path
from . import views

app_name = "suppliers"

urlpatterns = [
    path("", views.SupplierListView.as_view(), name="supplier_list"),
    path("create/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("<int:pk>/update/", views.SupplierUpdateView.as_view(), name="supplier_update"),
    path("<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),

    path("purchase-orders/", views.PurchaseOrderListView.as_view(), name="purchase_order_list"),
    path("purchase-orders/create/", views.PurchaseOrderCreateView.as_view(), name="purchase_order_create"),
    path("purchase-orders/<int:pk>/", views.PurchaseOrderDetailView.as_view(), name="purchase_order_detail"),
    path("purchase-orders/<int:pk>/update/", views.PurchaseOrderUpdateView.as_view(), name="purchase_order_update"),
    path("purchase-orders/<int:pk>/items/add/", views.purchase_order_add_item, name="purchase_order_add_item"),
    path("purchase-orders/<int:pk>/send/", views.purchase_order_mark_sent, name="purchase_order_send"),
    path("purchase-orders/<int:pk>/receive/", views.purchase_order_receive, name="purchase_order_receive"),
    path("purchase-orders/<int:pk>/cancel/", views.purchase_order_cancel, name="purchase_order_cancel"),
    path(
        "purchase-orders/<int:order_pk>/items/<int:item_pk>/delete/",
        views.purchase_order_delete_item,
        name="purchase_order_item_delete",
    ),
]