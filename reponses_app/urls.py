from django.urls import path
from . import views

# liste des routes URLs pour le module app

urlpatterns = [
    path("index", views.index, name="responses_index"),
    path("search", views.search, name="search_response"),
    path("submit/<int:pk>", views.create, name="submit_response"),
    path("store", views.store, name="store_response"),
    path("read/<int:pk>", views.show, name="show_response"),
    path("export_xlsx/<int:exercice_id>",views.exportXLSX,name="export_responses"),
    path("liste_exercice_responses/<int:exercice_id>", views.liste_exercice_responses,name="liste_exercice_responses"),
    path("getResponseValue/<int:pk>",views.getResponseValue,name="getResponseValue")
]

