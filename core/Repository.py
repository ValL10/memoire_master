from django.db import connection

def getReponsesByExeciceRepository(ex_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM reponses_app_reponse WHERE exercice_id = '+str(ex_id)+'')
        results = cursor.fetchall()

    return results

def getAllResponsesByStudent(student_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM reponses_app_reponse WHERE etudiant_id = '+str(student_id)+'')
        results = cursor.fetchall()

    return results


