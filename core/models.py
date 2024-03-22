from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
from django.utils import timezone
import random

# Create your models here.


class Profile(models.Model):

    class Role(models.IntegerChoices):
        STUDENT = 1
        TEACHER = 2
        ADMINISTRATOR = 3   

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role_user = models.IntegerField(choices=Role.choices)
    matiere_enseigne = models.CharField(max_length=100, null=True)
    ni_etudiant = models.CharField(max_length=20, null=True)
    niveau_etudiant = models.CharField(max_length=2, null=True)
    parcours_etudiant = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self) -> str:
        return self.user.first_name

    @property
    def is_Student(self):
        if self.role_user == 1:
            return True
    @property
    def is_Teacher(self):
        if self.role_user == 2:
            return True
    @property
    def is_Admin(self):
        if self.role_user == 3:
            return True


    def StoreManyTeacher(data_to_add):
        usernames = []
        passwords = []

        for teacherToadd in data_to_add:
            username = teacherToadd[2]
            usernames.append(username)

        for teacherToadd in data_to_add:
            password = teacherToadd[4]
            passwords.append(password)

        for i in range(len(usernames)):
            User.objects.create_user(username=usernames[i],password=passwords[i])

        emails = []
        last_names = []
        first_names = []
        matiere_enseignes = []

        for teacherToadd in data_to_add:
            first_name = teacherToadd[0]
            last_name = teacherToadd[1] 
            email = teacherToadd[3]
            matiere_enseigne = teacherToadd[5]

            first_names.append(first_name)
            last_names.append(last_name)
            emails.append(email)
            matiere_enseignes.append(matiere_enseigne)

        for i in range (len(usernames)):
            user_to_maj = User.objects.get(username=usernames[i])
            
            user_to_maj.first_name = first_names[i]

            user_to_maj.save()

        for i in range (len(usernames)):
            user_to_maj = User.objects.get(username=usernames[i])
            
            user_to_maj.last_name = last_names[i]

            user_to_maj.save()

        for i in range (len(usernames)):
            user_to_maj = User.objects.get(username=usernames[i])
            
            user_to_maj.email = emails[i]

            user_to_maj.save()

        for i in range (len(usernames)):
            user_to_link_profile = User.objects.get(username=usernames[i])

            Profile.objects.create(
                matiere_enseigne=matiere_enseignes[i],
                role_user=2,
                user = user_to_link_profile
            )

        return True         

        
    def StoreManyStudents(data_to_add):
        usernames = []
        passwords = []

        for teacherToadd in data_to_add:
            username = teacherToadd[3]
            usernames.append(username)

        for teacherToadd in data_to_add:
            password = teacherToadd[5]
            passwords.append(password)

        for i in range(len(usernames)):
            User.objects.create_user(username=usernames[i],password=passwords[i])

        emails = []
        last_names = []
        first_names = []
        numeros = []
        niveaux = []
        parcours = []

        for teacherToadd in data_to_add:
            first_name = teacherToadd[0]
            last_name = teacherToadd[1]
            numero = teacherToadd[2] 
            email = teacherToadd[4]
            niveau = teacherToadd[6]
            parcour = teacherToadd[7]

            first_names.append(first_name)
            last_names.append(last_name)
            emails.append(email)
            niveaux.append(niveau)
            parcours.append(parcour)
            numeros.append(numero)

        for i in range (len(usernames)):
            user_to_maj = User.objects.get(username=usernames[i])
            
            user_to_maj.first_name = first_names[i]

            user_to_maj.save()

        for i in range (len(usernames)):
            user_to_maj = User.objects.get(username=usernames[i])
            
            user_to_maj.last_name = last_names[i]

            user_to_maj.save()

        for i in range (len(usernames)):
            user_to_maj = User.objects.get(username=usernames[i])
            
            user_to_maj.email = emails[i]

            user_to_maj.save()

        for i in range (len(usernames)):
            user_to_link_profile = User.objects.get(username=usernames[i])

            Profile.objects.create(
                ni_etudiant=numeros[i],
                niveau_etudiant=niveaux[i],
                parcours_etudiant=parcours[i],
                role_user=1,
                user = user_to_link_profile
            )

        return True 