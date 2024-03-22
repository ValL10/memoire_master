from django.db import models
from django.contrib.auth.models import User
from exercice_app.models import Exercice
from django.utils import timezone

class Reponse(models.Model):

    contenu_reponse = models.TextField(max_length=10000)
    feedback_reponse = models.TextField(max_length=10000)
    etudiant = models.ForeignKey(to=User, on_delete=models.CASCADE)
    exercice = models.ForeignKey(to=Exercice, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self) -> str:
        return self.contenu_reponse    

class Note(models.Model):
    
    note_numerique = models.IntegerField()
    reponse = models.OneToOneField(to=Reponse, on_delete=models.CASCADE)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return str(self.note_numerique)