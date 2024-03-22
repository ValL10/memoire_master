# Generated by Django 4.2.5 on 2023-10-17 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Exercice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titre_exercice", models.CharField(max_length=255)),
                ("description_exercice", models.CharField(max_length=1000)),
                ("parcours_cible", models.CharField(max_length=100)),
                ("niveau_cible", models.CharField(max_length=2)),
                ("complexite_exercice", models.IntegerField(max_length=1)),
                ("langage_exercice", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "enseignant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Correction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("contenu_correction", models.TextField(max_length=10000)),
                ("description_correction", models.TextField(max_length=1000)),
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "exercice", models.OneToOneField(to="exercice_app.exercice", on_delete=models.CASCADE)
                ),
            ],
        ),
    ]
