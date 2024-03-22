from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from core import Repository

# Create your models here.
class Exercice(models.Model):

    titre_exercice = models.CharField(max_length=255)
    description_exercice = models.CharField(max_length=1000)
    parcours_cible = models.CharField(max_length=100)
    niveau_cible = models.CharField(max_length=2)
    complexite_exercice = models.IntegerField()
    langage_exercice = models.CharField(max_length=100)
    enseignant = models.ForeignKey(to=User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    

    # validation des donnees

    def clean(self):
        cleaned_data = super().clean()

        titre_exercice = self.titre_exercice
        description_exercice = self.description_exercice
        parcours_cible = self.parcours_cible
        niveau_cible = self.niveau_cible
        complexite_exercice = self.complexite_exercice
        langage_exercice = self.langage_exercice

        if titre_exercice == '' or len(titre_exercice) < 20:
            raise ValidationError("Le champ Titre doit avoir au moins 20 caractères")
        
        if description_exercice == '' or len(description_exercice) < 50:
            raise ValidationError("Le champ Description doit avoir au moins 50 caractères")
        
        if parcours_cible == '':
            raise ValidationError("Le champ Parcours est obligatoire")
        
        if niveau_cible == '':
            raise ValidationError("Le champ Niveau est obligatoire")
        
        if int(complexite_exercice) > 5 or int(complexite_exercice) < 1:
            raise ValidationError("Le champ Complexité doit etre compris entre 1 et 5")
        
        if langage_exercice == '':
            raise ValidationError("Le champ Langage est obligatoire")
        
        return True

    def __str__(self) -> str:
        return self.titre_exercice

    @property
    def no_correction(self):
        if hasattr(self, 'correction'): 

            if len(self.correction.contenu_correction) == 0:
                return True 
        else:
            correction = Correction.objects.filter(exercice=self.id)
 
            if len(correction) == 0:
                return True    
        return False

    @property
    def no_reponse(self):
        reponse = Repository.getReponsesByExeciceRepository(self.id)

        if len(reponse) == 0:
            return True
        
        return False

    def check_student_validity(self, user):
        if user.profile.is_Student and user.profile.niveau_etudiant == self.niveau_cible and user.profile.parcours_etudiant == self.parcours_cible:
            return True
        
        return False

class Correction(models.Model):
    
    contenu_correction = models.TextField(max_length=10000)
    description_correction = models.TextField(max_length=1000)

    exercice = models.OneToOneField(to=Exercice, on_delete=models.CASCADE)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def clean(self):
        cleaned_data = super().clean()

        contenu_correction = cleaned_data.get('contenu_correction')
        description_correction = cleaned_data.get('description_correction')

        if contenu_correction == '':
            raise ValidationError("Le Contenu de la correction est obligatoire")
        
        if description_correction == '':
            raise ValidationError("La description de la correction est obligatoire")
        

        return cleaned_data
    
    def __str__(self) -> str:
        return self.description_correction
    

    def CreateService(post_args):
        file_content = ""

        if post_args[0] is not None:
            file_content = post_args[0].read().decode('utf-8')

        correction = Correction.objects.create(
            contenu_correction = file_content,
            description_correction = post_args[1],
            exercice = post_args[2],
        )

        correction.save()

        return True
    