from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Exercice, Correction
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core import Repository

def index(request):

    if request.user.is_authenticated is not True:
        raise Http404('La page demandée n\'a pas pu etre trouvée')
    
    if request.user.profile.is_Student:
        all_exercices = Exercice.objects.filter(niveau_cible=request.user.profile.niveau_etudiant, parcours_cible=request.user.profile.parcours_etudiant).order_by("-created_at")

        exercices_faites = Exercice.objects.filter(reponse__etudiant=request.user.id)

        exercices = []

        for exercice in all_exercices:
            if exercice not in exercices_faites and exercice.no_correction is not True:
                exercices.append(exercice)

        return render(request,'exercice_app/index.html',{'exercices': exercices, 'exercices_faites': exercices_faites})
    
    elif request.user.profile.is_Teacher:

        exercices = Exercice.objects.filter(enseignant=request.user.id).order_by("-created_at")
        return render(request,'exercice_app/index.html',{'exercices': exercices})

@login_required
def search(request):
    if request.user.is_authenticated is not True:
        raise Http404('La page demandée n\'a pas pu etre trouvée')
    
    requested_search = request.GET['search']

    if requested_search != '':

        if request.user.profile.is_Student:
            all_exercices = Exercice.objects.filter( Q(niveau_cible=request.user.profile.niveau_etudiant) & Q(parcours_cible=request.user.profile.parcours_etudiant)).filter(Q(titre_exercice__icontains=requested_search) | Q(langage_exercice__icontains=requested_search) | Q(description_exercice__icontains=requested_search)).order_by("-created_at")
            
            exercices_faites = Exercice.objects.filter(reponse__etudiant=request.user.id)

            exercices = []

            for exercice in all_exercices:
                if exercice not in exercices_faites and exercice.no_correction is not True:
                    exercices.append(exercice)

            return render(request,'exercice_app/index.html',{'exercices': exercices, 'exercices_faites': exercices_faites})
                    
        elif request.user.profile.is_Teacher:

            exercices = Exercice.objects.filter(enseignant=request.user.id)&Exercice.objects.filter (niveau_cible__icontains=requested_search)|Exercice.objects.filter( parcours_cible__icontains=requested_search)|Exercice.objects.filter(titre_exercice__icontains=requested_search).order_by("-created_at")

            return render(request,'exercice_app/index.html',{'exercices': exercices})
            
    else:
        return redirect('exercices_index')
        
@login_required
def create(request):
    if request.user.is_authenticated is not True and request.user.profile.is_Teacher is not True:
        raise HttpResponseForbidden("Accès interdit : Vous n'avez pas l'autorisation d'accéder à cette ressource.")
    
    return render(request,'exercice_app/create.html')

@login_required
def store(request):
    # validation des roles

    if request.user.is_authenticated is not True and request.user.profile.is_Teacher is not True:
        raise HttpResponseForbidden("Accès interdit : Vous n'avez pas l'autorisation d'accéder à cette ressource.")        

    # validation formulaire

    if request.method == 'POST':
        # validation des donnees

        exercice = Exercice.objects.create(titre_exercice = request.POST['titre_exercice'], 
                            description_exercice = request.POST['description_exercice'], 
                            parcours_cible = request.POST['parcours_cible'], 
                            niveau_cible = request.POST['niveau_cible'], 
                            complexite_exercice = request.POST['complexite_exercice'], 
                            langage_exercice = request.POST['langage_exercice'],
                            enseignant = request.user)
        
        try:
            # Appelez la méthode clean pour effectuer la validation
            exercice.clean()

        except ValidationError as e:
            # La validation a échoué, affichez les erreurs
            return render(request, 'exercice_app/create.html', {'errors': e.messages, 'exercice': exercice})


        exercice.enseignant = request.user
        exercice.save()

        # section correction lier avec

        if request.FILES.get('correction_file') and request.POST['description_correction']:
            Correction.CreateService([request.FILES.get('correction_file'), 
                                      request.POST['description_correction'],
                                      exercice])

        message_ajout = 'L\'exercice '+ exercice.titre_exercice+ ' créé avec succès'

        messages.success(request, message_ajout)

        # Redirigez l'utilisateur vers une autre vue
        return redirect('exercices_index')  

@login_required         
def show(request, key):
    
    if request.user.is_authenticated is not True and request.user.profile.is_Teacher is not True:
        raise HttpResponseForbidden("Accès interdit : Vous n'avez pas l'autorisation d'accéder à cette ressource.")
    
    exercice = Exercice.objects.get(id=key)
    if exercice is None:
        raise Http404("Ressource Introuvable")
    
    return render(request,'exercice_app/show.html', {'exercice':exercice})

@login_required
def edit(request):
    if request.user.is_authenticated is not True and request.user.profile.is_Teacher is not True:
        raise HttpResponseForbidden("Accès interdit : Vous n'avez pas l'autorisation d'accéder à cette ressource.")
    exercice = Exercice.objects.get(id=request.GET['exercice'])

    if exercice is None:
        raise Http404("Ressource Introuvable")
    
    return render(request,'exercice_app/edit.html', {'exercice':exercice})

@login_required
def update(request):
    if request.user.is_authenticated is not True and request.user.profile.is_Teacher is not True:
        raise HttpResponseForbidden("Accès interdit : Vous n'avez pas l'autorisation d'accéder à cette ressource.")
    
    exercice = Exercice.objects.get(id=request.POST['exercice_id'])

    if exercice is None:
        raise Http404("Ressource Introuvable")    

    if request.method == 'POST':
        # validation des donnees

        exercice.titre_exercice = request.POST['titre_exercice'] 
        exercice.description_exercice = request.POST['description_exercice'] 
        exercice.parcours_cible = request.POST['parcours_cible'] 
        exercice.niveau_cible = request.POST['niveau_cible'] 
        exercice.complexite_exercice = request.POST['complexite_exercice'] 
        exercice.langage_exercice = request.POST['langage_exercice']

        if hasattr(exercice, 'correction') :
            exercice.correction.description_correction = request.POST['description_correction']
            #exercice.updated_at = str(timezone.now)

            if request.FILES.get('correction_file'):
                exercice.correction.contenu_correction = request.FILES.get('correction_file').read().decode('utf-8')

            
            try:
                # Appelez la méthode clean pour effectuer la validation
                exercice.clean()

            except ValidationError as e:
                # La validation a échoué, affichez les erreurs
                return render(request, 'exercice_app/show.html', {'errors': e.messages, 'exercice': exercice})

            exercice.save()
            exercice.correction.save()

        else:

            placeholder_desc = "Pas de Description"
            if request.POST['description_correction']:
                placeholder_desc = request.POST['description_correction']
            Correction.CreateService([request.FILES.get('correction_file'), 
                                      placeholder_desc,
                                      exercice])

        message_modification = 'L\'exercice '+ exercice.titre_exercice+ ' a été modifié avec succès'

        messages.success(request, message_modification)

        # Redirigez l'utilisateur vers une autre vue
        return redirect('exercices_index')


