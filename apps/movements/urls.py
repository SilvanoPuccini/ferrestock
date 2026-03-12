from django.urls import path
from . import views

app_name = "movements"

urlpatterns = [
    path("", views.StockMovementListView.as_view(), name="movement_list"),
    path("create/", views.StockMovementCreateView.as_view(), name="movement_create"),
]
