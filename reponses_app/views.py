from django.shortcuts import render, redirect
from .models import Reponse, Note
from django.contrib.auth.decorators import login_required
from exercice_app.models import Exercice
from django.http import Http404, HttpResponseForbidden
from .classes.utils import GetCodeBLEUScore, GetNote
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from openpyxl import Workbook
import keyword
from datetime import datetime


# Create your views here.
@login_required
def index(request):
    if request.user.profile.is_Student:
        reponses = Reponse.objects.filter(etudiant=request.user.id).order_by('-created_at')

        return render(request, 'reponses_app/index.html', {'reponses': reponses})
    
    return HttpResponseForbidden()

@login_required
def search(request):
    if request.user.profile.is_Student:
        searched_key = request.GET['search']
        reponses = Reponse.objects.filter(etudiant=request.user.id).filter(
            Q(contenu_reponse=searched_key) | Q(feedback_reponse=searched_key)
        ).order_by('-created_at')

        return render(request, 'reponses_app/index.html', {'reponses': reponses})
    
    return HttpResponseForbidden()

@login_required    
def create(request, pk):
    
    if request.user.profile.is_Student:
        exercice = Exercice.objects.get(id=pk)
    
        if exercice.check_student_validity(request.user) is not True:
            return HttpResponseForbidden()

        return render(request, 'reponses_app/create.html', {'exercice': exercice})
    else:
        return HttpResponseForbidden() 

@login_required
def store(request):
    if request.user.profile.is_Student and request.method == "POST":
        exercice = Exercice.objects.get(id=request.POST["exercice"])

        if exercice is None:
            raise Http404('La page ou la ressource demandée n\'a pas pu etre trouvée')

        if exercice.check_student_validity(request.user) is not True:
            return HttpResponseForbidden()
        
        response = Reponse.objects.create(
            contenu_reponse = request.POST['codeValue'],
            feedback_reponse = "HIIIIII",
            etudiant = request.user,
            exercice = exercice

        )
        
        note_attribuee = calculateNote([response.contenu_reponse, response.exercice.correction.contenu_correction])
        note = Note.objects.create(
            note_numerique=note_attribuee, 
            reponse = response
        )

        response.save()
        note.save()

        return redirect('show_response', pk=response.id)
    else:
        return HttpResponseForbidden()

@login_required
def show(request, pk):

    if request.user.is_authenticated and request.user.profile.is_Admin is not True:
        reponse = Reponse.objects.get(pk=pk)

        if reponse is None:
            raise Http404(" La ressource demandée est introuvable ")

        return render(request, 'reponses_app/show.html',{'reponse':reponse})

def countResponse(ex_id):
    responses = Reponse.objects.filter(exercice=ex_id)

    return responses

def calculateNote(arguments):

    hyperparameters = [0.10, 0.10, 0.40, 0.40]
    lang = "python"
    tokens_weighted = keyword.kwlist

    noteCodeBLEU = GetCodeBLEUScore(arguments[0], 
                                    arguments[1], 
                                    hyperparameters, 
                                    lang, 
                                    tokens_weighted)

    note = GetNote(noteCodeBLEU)

    return note

@login_required
def liste_exercice_responses(request, exercice_id):
    if request.user.profile.is_Teacher is not True:
        return HttpResponseForbidden()

    responses = Reponse.objects.filter(exercice=exercice_id)
    exercice = Exercice.objects.get(id=exercice_id)

    count = len(responses)

    responses_dic = {}
    for item, response in enumerate(responses):
        responses_dic[item] = response

    notes = []
    etudiants_numero = []

    for item in responses:
        notes.append(item.note.note_numerique)
        etudiants_numero.append(item.etudiant.profile.ni_etudiant)

    return render(request, 'reponses_app/list_responses.html', {'responses': responses_dic, 'exercice': exercice, 'count': count, 'NotesEtudiants': [etudiants_numero, notes]})

@login_required
def exportXLSX(request, exercice_id):
    if request.user.profile.is_Teacher is not True:
        return HttpResponseForbidden()

    responses = Reponse.objects.filter(exercice=exercice_id).order_by('-note')

    classeur = Workbook()

    feuille = classeur.active

    feuille.append(['Exercice du: ','', '','',responses[0].exercice.created_at.strftime("%d-%m-%Y")])
    feuille.append(['Exporter le:','', '','',datetime.now().strftime("%d-%m-%Y")])
    feuille.append(['','', '','',''])
    feuille.append(['Titre:', '','','',responses[0].exercice.titre_exercice])
    feuille.append(['','', '','',''])
    feuille.append(['','', '','',''])
    feuille.append([' ', 'Numéro Etudiant', 'Nom', 'Prénom','Note'])

    for index, reponse in enumerate(responses):
        feuille.append([index+1, 
                        reponse.etudiant.profile.ni_etudiant, 
                        reponse.etudiant.last_name,
                        reponse.etudiant.first_name,
                        reponse.note.note_numerique
                        ])

    http_response_to_return = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    http_response_to_return['Content-Disposition'] = 'attachment; filename="'+responses[0].exercice.titre_exercice+'.xlsx"'

    classeur.save(http_response_to_return)

    return http_response_to_return

def getResponseValue(request, pk):    
    response = Reponse.objects.get(id=pk)
    data = [{'contenu_reponse': response.contenu_reponse}]

    json_response = JsonResponse(data, safe=False)

    return json_response
