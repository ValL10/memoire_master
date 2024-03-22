from django.shortcuts import render
from exercice_app.models import Exercice, Correction
from django.contrib.auth.models import User
from core.models import Profile
from reponses_app.models import Reponse, Note
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Count
from django.utils import timezone



# Create your views here.
@login_required
def index(request):
    if request.user.profile.is_Admin:
        dic = AdminDashBoard(request)
    
        return render(request,'scoreboard/index.html', dic)
    
    elif request.user.profile.is_Teacher:

        dic = TeacherDashBoard(request)
        return render(request,'scoreboard/index.html', dic)
    
    else:
        dic = StudentDashBoard(request)

        return render(request,'scoreboard/index.html', dic)



def StudentDashBoard(request):
    annee = datetime.now().strftime("%Y")
    all_reponses = Reponse.objects.filter(etudiant=request.user.id)

    exercice_realises = len(all_reponses)
    note_min_max = [0,0]
    notes = []
    moyenne_reponses = 0
    date = []
    for reponse in all_reponses:
        notes.append(reponse.note.note_numerique)
        date.append(reponse.exercice.titre_exercice[:10])

    if len(notes) > 0:
        note_min_max[0] = min(notes)
        note_min_max[1] = max(notes)
        moyenne_reponses = sum(notes) / len(notes)
    
    reponses_soumises = len(all_reponses)
    reponses_soumises_annee = len(all_reponses.filter(created_at__year=annee))

    return {
        'annee': annee,
        'all_reponses': all_reponses,
        'exercice_realises': exercice_realises,
        'note_min_max': note_min_max,
        'moyenne_reponses': moyenne_reponses,
        'reponses_soumises': reponses_soumises,
        'reponses_soumises_annee': reponses_soumises_annee,
        'notes_dates': [notes, date]

        }

def AdminDashBoard(request):

    annee = datetime.now().strftime("%Y")

    count_exercices_annee = len(Exercice.objects.filter(created_at__year=annee))
    count_reponses_annee = len(Reponse.objects.filter(created_at__year=annee))
    count_notes_annee= len(Note.objects.filter(created_at__year=annee))
    count_corrections_annee = len(Correction.objects.filter(created_at__year=annee))

    count_total = {}
    count_total['exercices'] = len(Exercice.objects.all())
    count_total['reponses'] = len(Reponse.objects.all())
    count_total['notes']= len(Note.objects.all())
    count_total['corrections'] = len(Correction.objects.all())

    count_total['users'] = len(User.objects.all())
    count_total['users_students'] = len(Profile.objects.filter(role_user=1))
    count_total['users_teachers'] = len(Profile.objects.filter(role_user=2))
    count_total['users_admins'] = len(Profile.objects.filter(role_user=3))


    number_by_langage = Exercice.objects.values('langage_exercice').annotate(exe_count=Count('id')).order_by('langage_exercice')

    un_mois = timezone.now() - timezone.timedelta(days=30)
    users_non_actifs_since_1month = User.objects.filter(last_login__lt=un_mois)
    users_recents_1month = User.objects.filter(date_joined__gte=un_mois)

    number_by_langage_list = []
    for langage in number_by_langage:
        number_by_langage_list.append(langage)
    


    return {
                      'annee': annee,
                      'autres_annees': [int(annee)-1, int(annee)+1],
                      'count_exercices_annee': count_exercices_annee,
                      'count_reponses_annee': count_reponses_annee,
                      'count_notes_annee': count_notes_annee,
                      'count_corrections_annee': count_corrections_annee,
                      'count_total': count_total,
                      'number_by_langage': number_by_langage_list,
                      'users_non_actifs': users_non_actifs_since_1month,
                      'users_recents': users_recents_1month
                  }

def TeacherDashBoard(request):
    annee = datetime.now().strftime("%Y")

    count_total = {}
    count_total['exercices_ens'] = len(Exercice.objects.filter(enseignant=request.user.id))

    count_exercices_annee_ens = len(Exercice.objects.filter(created_at__year=annee, enseignant=request.user.id))

    derniere_exercice = Exercice.objects.filter(enseignant=request.user.id).order_by('-created_at').first()


    # notes derniers exercice

    notes = [[],[]]

    for reponse in Reponse.objects.filter(exercice=derniere_exercice.id):
        notes[0].append(reponse.etudiant.profile.ni_etudiant)
        notes[1].append(reponse.note.note_numerique)

    langage_pref = Exercice.objects.values('langage_exercice').filter(enseignant=request.user.id).annotate(exe_count=Count('id')).order_by('langage_exercice')


    notes_profs = []
    participants_exs = []
    for exercice in Exercice.objects.filter(enseignant=request.user.id):
        participants_exs.append(len(Reponse.objects.filter(exercice=exercice.id)))
        for reponse in Reponse.objects.filter(exercice=exercice.id):
            notes_profs.append(reponse.note.note_numerique)

    minimum = 0
    maximum = 0

    if len(notes_profs) != 0:
        minimum = min(notes_profs)
        maximum = max(notes_profs)

    note_moyenne = sum(notes_profs) / len(notes_profs) if len(notes_profs) > 0 else 0 
    notes_min_max= [minimum , maximum]
    participant_moyenne = sum(participants_exs) / len(Exercice.objects.filter(enseignant=request.user.id)) if len(Exercice.objects.filter(enseignant=request.user.id)) > 0 else 0 

    exercices_recents = Exercice.objects.filter(enseignant=request.user.id).order_by('-created_at')[0:5]
    
    return {
                      'annee': annee,
                      'autres_annees': [int(annee)-1, int(annee)+1],
                      'count_total': count_total,
                      'count_exercices_annee_ens':count_exercices_annee_ens,
                      'langage_pref': langage_pref,
                      'dernier_exercice': derniere_exercice,
                      'note_dernier_exercice': notes,
                      'note_moyenne': note_moyenne,
                      'notes_min_max': notes_min_max,
                      'participant_moyenne': participant_moyenne,
                      'exercices_recents': exercices_recents
                      
            }