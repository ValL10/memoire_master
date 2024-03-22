from django.urls import path
from . import views

# liste des routes URLs pour le module app

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_user, name="login_user"),
    path("logout", views.logout_user, name="logout_user"),

    # enseignants

    path("teachers/index", views.teacher_index, name="teachers_index"),
    path("teachers/search", views.search_teacher, name="search_teacher"),
    path("teachers/add", views.create_teacher, name="create_teacher"),
    path("teachers/check_storing", views.store_teacher, name="store_teacher"),

    # etudiants

    path("students/index", views.students_index, name="students_index"),
    path("students/search", views.search_student, name="search_student"),
    path("students/add", views.create_student, name="create_student"),
    path("students/storing", views.store_students, name="store_student"),


]
  