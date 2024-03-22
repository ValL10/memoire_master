from django.urls import path
from . import views

# liste des routes URLs pour le module exercice_app

urlpatterns = [
    path("index", views.index, name="exercices_index"),
    path("search", views.search, name="search_exercice"),
    path("create", views.create, name="create_exercice"),
    path("store", views.store, name="store_exercice"),
    path("show/<int:key>", views.show, name="show_exercice"),
    path("edit", views.edit, name="edit_exercice"),
    path("update", views.update, name="update_exercice"),
]