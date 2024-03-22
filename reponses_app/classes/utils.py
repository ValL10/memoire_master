from reponses_app.CodeBLEU import CodeBLEUMainFunction


def GetCodeBLEUScore(candidat_code, correction_code, hyperparameters, lang, tokens_weighted):

    score = CodeBLEUMainFunction(candidate_code=candidat_code, correction_code=correction_code, hyperparameters=hyperparameters, lang=lang, tokens_weighted=tokens_weighted)

    return score


def GetNote(score):
    note = score * 20

    return note