from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Landing publica en "/". No se enlaza desde el navbar a proposito: una vez logueado,
    # el usuario navega siempre desde dashboard:home, que es lo que enlaza la marca del navbar.
    path("", views.home, name="home"),
]

