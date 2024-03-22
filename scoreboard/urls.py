from django.urls import path
from . import views

# liste des routes URLs pour le module exercice_app

urlpatterns = [
    path("index", views.index, name="scoreboard_index"),
]