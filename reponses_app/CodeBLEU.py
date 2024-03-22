import math
from copy import deepcopy

# pour la partie AST
from tree_sitter_languages import get_language, get_parser

# pour la partie DATAFLOW
import re
from io import StringIO
import  tokenize


# In[33]:


"""  

BLEU : BILINGUAL EVALUATION UNDERSTUDY


BLEU= BP· exp (∑(n=1,N)wn log pn)

"""

# fonction qui formate le code
def formatCode(code):
    code = code.lower()
    
    return code

# fonction qui renvoie les ngrams du code (1 a 4)
def getNGrams(code, N):
    ngrams = []
    
    # formatage du code
    code = formatCode(code)
    
    code_to_array = code.split() 
    decount = 1
    for i in range (1,N+1):
        array = []
        for j in range (0,len(code_to_array)):
            sub = code_to_array[int(j):int(j+decount)]
            if len(sub) == decount:
                string = " ".join(sub)
                array.append(string)
        ngrams.append(array)
        decount = decount + 1
        
    return ngrams

# renvoie un grand tableau comportant tous les ngrams candidat / references
def getAllNGrams(candidat_code, references, N):
    
    ngrams_candidat = getNGrams(candidat_code, N)
    ngrams_references = []
    
    for reference in references:
        ngrams_references.append(getNGrams(reference, N))

    all_ngrams = [ngrams_candidat, ngrams_references]

    return all_ngrams


# fonction qui choisi le minimum entre le coeff_max_ref et le coeff_max_cand

def clippingCoeff(dictionnary):    
    for key, value in dictionnary.items():
        dictionnary[key] = min(value)
        
    return dictionnary


# fonction qui combine tous les coeff apres clipping

def getFullCoeff(dictionnary): 
    somme = 0
    for key, value in dictionnary.items():
        somme = somme + value
        
    return somme

# renvoie tous les precisions des n grams (1 a 4)
def getPrecisionPerGrams(ngrams_candidat, ngrams_references):
    precisions = []
    ngrams_coeff_ref_max = []
    dictionnary = {}
    
    # calcul le nombre d'occurence maximum d'un n-gram dans tous les references / et aussi le nombre d'occurence d'un n-gram dans le candidat
    
    for n in range (len(ngrams_candidat)):
        dic = dictionnary.copy()
        for item in ngrams_candidat[n]:
            coeff_max = 0
            for ref in ngrams_references:
                item_count = ref[n].count(item)
                if coeff_max < item_count:
                    coeff_max = item_count
                    
            candidat_count = ngrams_candidat[n].count(item)            
            dic[item] = [coeff_max, candidat_count]
        ngrams_coeff_ref_max.append(dic)
        
    #print("valeur max des mots dans les references et dans le candidat", ngrams_coeff_ref_max)
    
    # application du CLIPPING
    
    for item in ngrams_coeff_ref_max:
        item = clippingCoeff(item)
    
    #print("============================================================")
    #print("coeff apres Clipping ", ngrams_coeff_ref_max)
    
    
    # CALCULS DES PRECISIONS POUR CHAQUE N-GRAMS
    
    for length in range (len(ngrams_coeff_ref_max)):
        #print(len(ngrams_candidat[length]), ngrams_candidat[length])
        # on additionne les coefficient de chaque item des n-grammes, puis on le divise par le nombre total de item dans le n-gram
        if len(ngrams_candidat[length]) > 0:
            precisions.append(float(getFullCoeff(ngrams_coeff_ref_max[length]) / len(ngrams_candidat[length])))
        else:
             precisions.append(0.0)
        
    
    # renvoie des precisions
    
    return precisions


# fonction qui calcule la somme cumultative (MOYENNE GEOMETRIQUE) entre les precisions de chaque n-grams

"""

La moyenne Geometrique est egal a la formule (exp(sum{1,n}(wnlogPn))

    exp(sum{1,n}(wn*logPn)  = (prod{1,n}(Pn))**wn

"""


def getGeometryAvg(precisions,):
    prod = 1
    for i in range (len(precisions)):       
        prod = prod * precisions[i]
        
    geo_avg = pow(prod, (1/len(precisions)))
    
    return geo_avg

# fonction qui calcule la penalite de longueur
def getBrevityPenalty(candidat, references):
    cand_len = len(candidat)
    ref_moy_len = 0
    bp = 1

    for i in range (len(references)):
        ref_moy_len = ref_moy_len + len(references[i])
    
    ref_moy_len = ref_moy_len / (len(references))
   
    """
    si len cand < len ref_moyenne , BP = e(1 - r/c)
    sinon 1
    """
    
    if cand_len <= ref_moy_len:
        bp = math.exp((1 - ref_moy_len / cand_len))
    
    return bp
    
# fonction qui retourne le score BLEU final avec penalite de longueur
"""
bleu_score = bp *  exp (∑(n=1,N)wn log pn) = bp * moyenne_geometrique_des_ngrams

"""
def getBleuScore(geo_avg, bp):
    return bp * geo_avg


# In[34]:


"""


WEIGHTED N-GRAMS

dans le papier de Shuo Ren, ils affirment que N = 1, et wn aussi = 1
mais le poids des tokens des unigrammes doit etre defini avant

"""

# fonction qui calcule la precision des unigrammes avec des poids 

def weightedPrecisionsNgrams(tokens_weight, cand_ngram, references_ngram):
    precisions = []
        
    #allant de 0 a 3 (1 a 4)
    for n in range (len(cand_ngram)):
        dic = {}
        cand_count = {}
        
       # on parcours chaque mots dans l'unigramme
        for word in cand_ngram[n]:
            # on initialise le poids a 1 pour les mots sans poids
            w = 1
            # coefficient max du mot dans les references
            coeff_max = 0

            # on boucle les poids , si present , on assigne une nouvelle poids:
            if word in tokens_weight:
                    w = 5

            # on prend le max d'occurence du mot 
            for ref in references_ngram:
                item_count = ref[n].count(word)
                if coeff_max < item_count:
                    coeff_max = item_count
            # on count le nombre de fois que le mot revient dans le candidat
            candidat_count = cand_ngram[n].count(word)
            cand_count[word] = candidat_count
            dic[word] = [[coeff_max, candidat_count], w]

        
        #print(dic, cand_count)

        # countclip (redifinit parce que les dicos ne sont pas les memes)
        for key, value in dic.items():
            dic[key] = min(value[0]) * value[-1]
            cand_count[key] = cand_count[key] * value[-1] 

        #print(dic, cand_count)

        # SOMME DES NUMERATEURS DE LA FORMULE : 
        somme_count_clip = getFullCoeff(dic)
        # SOMME DENOMINATEUR DE LA FORMULE 
        somme_count = getFullCoeff(cand_count)

        # precision des unigrammes
        if somme_count > 0:
            precision = somme_count_clip / somme_count
        else:
            precision = 0
            
        precisions.append(precision)
    
    return precisions
    


# In[35]:


"""   

AST    (ABSTRACT SYNTAX TREE)  

COMPARAISON SYNTAXIQUE DES 2 codes. 

MATCHast = COUNTclip(Tcand) / COUNT(Tref)

    COUNTclip(Tcand) = Le nombre de sous-arbres candidats qui correspondent à la référence.
    COUNT(Tref) = Le nombre total de sous-arbres de la reference

"""

# fonction qui retourne l' AST du code
def getASTTree(code, lang):
    parser = get_parser(lang)

    tree = parser.parse(bytes(code, "utf8"))
    
    return tree

# fonction qui retourne tous les sous arbres dans l'AST
def getAllSubTrees(root_node):
    nodes = []
    subtrees = []
    dep = 1
    nodes.append([root_node, dep])
    
    while len(nodes) != 0:
        cur_node, cur_dep = nodes.pop()
        subtrees.append([cur_node.sexp(), cur_dep])
        
        for child_node in cur_node.children:
            if len(child_node.children) != 0:
                dep = cur_dep + 1
                nodes.append([child_node, dep])
                
    return subtrees

# fonction qui retourne le score AST
def getASTScore(candidat_sub_trees, reference_sub_trees):
    refs = []
    matchcount = 0

    for refe in reference_sub_trees:
        refs.append(refe[0])

    for cand_subtree in candidat_sub_trees:
        if cand_subtree[0] in refs:
            matchcount = matchcount + 1


    if len(reference_sub_trees) > 0:
        score = matchcount / len(reference_sub_trees)
    else:
        return 0.0
    
    return score


# In[36]:


"""  PARTIE DATAFLOW  """


"""  FONCTIONS POUR LE CALCUL DU DATAFLOW MATCH  (extrait de l'implementation de Shuo Ren et al., 2022)"""


def remove_comments_and_docstrings(source,lang):
    if lang in ['python']:
        """
        Returns 'source' minus comments and docstrings.
        """
        io_obj = StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            ltext = tok[4]
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))
            # Remove comments:
            if token_type == tokenize.COMMENT:
                pass
            # This series of conditionals removes docstrings:
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
            # This is likely a docstring; double-check we're not inside an operator:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        temp=[]
        for x in out.split('\n'):
            if x.strip()!="":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['ruby']:
        return source
    else:
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " " # note: a space and not an empty string
            else:
                return s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp=[]
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip()!="":
                temp.append(x)
        return '\n'.join(temp)

def tree_to_token_index(root_node):
    if (len(root_node.children)==0 or root_node.type in ['string_literal','string','character_literal']) and root_node.type!='comment':
        return [(root_node.start_point,root_node.end_point)]
    else:
        code_tokens=[]
        for child in root_node.children:
            code_tokens+=tree_to_token_index(child)
        return code_tokens
    
def tree_to_variable_index(root_node,index_to_code):
    if (len(root_node.children)==0 or root_node.type in ['string_literal','string','character_literal']) and root_node.type!='comment':
        index=(root_node.start_point,root_node.end_point)
        _,code=index_to_code[index]
        if root_node.type!=code:
            return [(root_node.start_point,root_node.end_point)]
        else:
            return []
    else:
        code_tokens=[]
        for child in root_node.children:
            code_tokens+=tree_to_variable_index(child,index_to_code)
        return code_tokens    

def index_to_code_token(index,code):
    start_point=index[0]
    end_point=index[1]
    if start_point[0]==end_point[0]:
        s=code[start_point[0]][start_point[1]:end_point[1]]
    else:
        s=""
        s+=code[start_point[0]][start_point[1]:]
        for i in range(start_point[0]+1,end_point[0]):
            s+=code[i]
        s+=code[end_point[0]][:end_point[1]]   
    return s
   
def DFG_python(root_node,index_to_code,states):
    assignment=['assignment','augmented_assignment','for_in_clause']
    if_statement=['if_statement']
    for_statement=['for_statement']
    while_statement=['while_statement']
    do_first_statement=['for_in_clause'] 
    def_statement=['default_parameter']
    states=states.copy() 
    if (len(root_node.children)==0 or root_node.type in ['string_literal','string','character_literal']) and root_node.type!='comment':        
        idx,code=index_to_code[(root_node.start_point,root_node.end_point)]
        if root_node.type==code:
            return [],states
        elif code in states:
            return [(code,idx,'comesFrom',[code],states[code].copy())],states
        else:
            if root_node.type=='identifier':
                states[code]=[idx]
            return [(code,idx,'comesFrom',[],[])],states
    elif root_node.type in def_statement:
        name=root_node.child_by_field_name('name')
        value=root_node.child_by_field_name('value')
        DFG=[]
        if value is None:
            indexs=tree_to_variable_index(name,index_to_code)
            for index in indexs:
                idx,code=index_to_code[index]
                DFG.append((code,idx,'comesFrom',[],[]))
                states[code]=[idx]
            return sorted(DFG,key=lambda x:x[1]),states
        else:
            name_indexs=tree_to_variable_index(name,index_to_code)
            value_indexs=tree_to_variable_index(value,index_to_code)
            temp,states=DFG_python(value,index_to_code,states)
            DFG+=temp            
            for index1 in name_indexs:
                idx1,code1=index_to_code[index1]
                for index2 in value_indexs:
                    idx2,code2=index_to_code[index2]
                    DFG.append((code1,idx1,'comesFrom',[code2],[idx2]))
                states[code1]=[idx1]   
            return sorted(DFG,key=lambda x:x[1]),states        
    elif root_node.type in assignment:
        if root_node.type=='for_in_clause':
            right_nodes=[root_node.children[-1]]
            left_nodes=[root_node.child_by_field_name('left')]
        else:
            if root_node.child_by_field_name('right') is None:
                return [],states
            left_nodes=[x for x in root_node.child_by_field_name('left').children if x.type!=',']
            right_nodes=[x for x in root_node.child_by_field_name('right').children if x.type!=',']
            if len(right_nodes)!=len(left_nodes):
                left_nodes=[root_node.child_by_field_name('left')]
                right_nodes=[root_node.child_by_field_name('right')]
            if len(left_nodes)==0:
                left_nodes=[root_node.child_by_field_name('left')]
            if len(right_nodes)==0:
                right_nodes=[root_node.child_by_field_name('right')]
        DFG=[]
        for node in right_nodes:
            temp,states=DFG_python(node,index_to_code,states)
            DFG+=temp
            
        for left_node,right_node in zip(left_nodes,right_nodes):
            left_tokens_index=tree_to_variable_index(left_node,index_to_code)
            right_tokens_index=tree_to_variable_index(right_node,index_to_code)
            temp=[]
            for token1_index in left_tokens_index:
                idx1,code1=index_to_code[token1_index]
                temp.append((code1,idx1,'computedFrom',[index_to_code[x][1] for x in right_tokens_index],
                             [index_to_code[x][0] for x in right_tokens_index]))
                states[code1]=[idx1]
            DFG+=temp        
        return sorted(DFG,key=lambda x:x[1]),states
    elif root_node.type in if_statement:
        DFG=[]
        current_states=states.copy()
        others_states=[]
        tag=False
        if 'else' in root_node.type:
            tag=True
        for child in root_node.children:
            if 'else' in child.type:
                tag=True
            if child.type not in ['elif_clause','else_clause']:
                temp,current_states=DFG_python(child,index_to_code,current_states)
                DFG+=temp
            else:
                temp,new_states=DFG_python(child,index_to_code,states)
                DFG+=temp
                others_states.append(new_states)
        others_states.append(current_states)
        if tag is False:
            others_states.append(states)
        new_states={}
        for dic in others_states:
            for key in dic:
                if key not in new_states:
                    new_states[key]=dic[key].copy()
                else:
                    new_states[key]+=dic[key]
        for key in new_states:
            new_states[key]=sorted(list(set(new_states[key])))
        return sorted(DFG,key=lambda x:x[1]),new_states
    elif root_node.type in for_statement:
        DFG=[]
        for i in range(2):
            right_nodes=[x for x in root_node.child_by_field_name('right').children if x.type!=',']
            left_nodes=[x for x in root_node.child_by_field_name('left').children if x.type!=',']
            if len(right_nodes)!=len(left_nodes):
                left_nodes=[root_node.child_by_field_name('left')]
                right_nodes=[root_node.child_by_field_name('right')]
            if len(left_nodes)==0:
                left_nodes=[root_node.child_by_field_name('left')]
            if len(right_nodes)==0:
                right_nodes=[root_node.child_by_field_name('right')]
            for node in right_nodes:
                temp,states=DFG_python(node,index_to_code,states)
                DFG+=temp
            for left_node,right_node in zip(left_nodes,right_nodes):
                left_tokens_index=tree_to_variable_index(left_node,index_to_code)
                right_tokens_index=tree_to_variable_index(right_node,index_to_code)
                temp=[]
                for token1_index in left_tokens_index:
                    idx1,code1=index_to_code[token1_index]
                    temp.append((code1,idx1,'computedFrom',[index_to_code[x][1] for x in right_tokens_index],
                                 [index_to_code[x][0] for x in right_tokens_index]))
                    states[code1]=[idx1]
                DFG+=temp   
            if  root_node.children[-1].type=="block":
                temp,states=DFG_python(root_node.children[-1],index_to_code,states)
                DFG+=temp 
        dic={}
        for x in DFG:
            if (x[0],x[1],x[2]) not in dic:
                dic[(x[0],x[1],x[2])]=[x[3],x[4]]
            else:
                dic[(x[0],x[1],x[2])][0]=list(set(dic[(x[0],x[1],x[2])][0]+x[3]))
                dic[(x[0],x[1],x[2])][1]=sorted(list(set(dic[(x[0],x[1],x[2])][1]+x[4])))
        DFG=[(x[0],x[1],x[2],y[0],y[1]) for x,y in sorted(dic.items(),key=lambda t:t[0][1])]
        return sorted(DFG,key=lambda x:x[1]),states
    elif root_node.type in while_statement:  
        DFG=[]
        for i in range(2):
            for child in root_node.children:
                temp,states=DFG_python(child,index_to_code,states)
                DFG+=temp    
        dic={}
        for x in DFG:
            if (x[0],x[1],x[2]) not in dic:
                dic[(x[0],x[1],x[2])]=[x[3],x[4]]
            else:
                dic[(x[0],x[1],x[2])][0]=list(set(dic[(x[0],x[1],x[2])][0]+x[3]))
                dic[(x[0],x[1],x[2])][1]=sorted(list(set(dic[(x[0],x[1],x[2])][1]+x[4])))
        DFG=[(x[0],x[1],x[2],y[0],y[1]) for x,y in sorted(dic.items(),key=lambda t:t[0][1])]
        return sorted(DFG,key=lambda x:x[1]),states        
    else:
        DFG=[]
        for child in root_node.children:
            if child.type in do_first_statement:
                temp,states=DFG_python(child,index_to_code,states)
                DFG+=temp
        for child in root_node.children:
            if child.type not in do_first_statement:
                temp,states=DFG_python(child,index_to_code,states)
                DFG+=temp
        
        return sorted(DFG,key=lambda x:x[1]),states

def calc_dataflow_match(references, candidate, lang):
    return corpus_dataflow_match([references], [candidate], lang)

def corpus_dataflow_match(references, candidates, lang):   
    LANGUAGE = get_language(lang)
    parser = get_parser(lang)
    parser.set_language(LANGUAGE)
    parser = [parser]
    match_count = 0
    total_count = 0

    for i in range(len(candidates)):
        references_sample = references[i]
        candidate = candidates[i] 
        for reference in references_sample:
            try:
                candidate=remove_comments_and_docstrings(candidate,'python')
            except:
                pass    
            try:
                reference=remove_comments_and_docstrings(reference,'python')
            except:
                pass  

            cand_dfg = get_data_flow(candidate, parser)
            ref_dfg = get_data_flow(reference, parser)
            
            normalized_cand_dfg = normalize_dataflow(cand_dfg)
            normalized_ref_dfg = normalize_dataflow(ref_dfg)

            if len(normalized_ref_dfg) > 0:
                total_count += len(normalized_ref_dfg)
                for dataflow in normalized_ref_dfg:
                    if dataflow in normalized_cand_dfg:
                            match_count += 1
                            normalized_cand_dfg.remove(dataflow)  
    if total_count == 0:
        print("WARNING: There is no reference data-flows extracted from the whole corpus, and the data-flow match score degenerates to 0. Please consider ignoring this score.")
        return 0
    score = match_count / total_count
    return score

def get_data_flow(code, parser):
    try:
        tree = parser[0].parse(bytes(code,'utf8'))    
        root_node = tree.root_node  
        tokens_index=tree_to_token_index(root_node)     
        code=code.split('\n')
        code_tokens=[index_to_code_token(x,code) for x in tokens_index]  
        index_to_code={}
        for idx,(index,code) in enumerate(zip(tokens_index,code_tokens)):
            index_to_code[index]=(idx,code)  
        try:
            DFG,_= DFG_python(root_node,index_to_code,{}) 
        except:
            DFG=[]
        DFG=sorted(DFG,key=lambda x:x[1])
        indexs=set()
        for d in DFG:
            if len(d[-1])!=0:
                indexs.add(d[1])
            for x in d[-1]:
                indexs.add(x)
        new_DFG=[]
        for d in DFG:
            if d[1] in indexs:
                new_DFG.append(d)
        codes=code_tokens
        dfg=new_DFG
    except:
        codes=code.split()
        dfg=[]
    #merge nodes
    dic={}
    for d in dfg:
        if d[1] not in dic:
            dic[d[1]]=d
        else:
            dic[d[1]]=(d[0],d[1],d[2],list(set(dic[d[1]][3]+d[3])),list(set(dic[d[1]][4]+d[4])))
    DFG=[]
    for d in dic:
        DFG.append(dic[d])
    dfg=DFG
    return dfg

def normalize_dataflow_item(dataflow_item):
    var_name = dataflow_item[0]
    var_pos = dataflow_item[1]
    relationship = dataflow_item[2]
    par_vars_name_list = dataflow_item[3]
    par_vars_pos_list = dataflow_item[4]

    var_names = list(set(par_vars_name_list+[var_name]))
    norm_names = {}
    for i in range(len(var_names)):
        norm_names[var_names[i]] = 'var_'+str(i)

    norm_var_name = norm_names[var_name]
    relationship = dataflow_item[2]
    norm_par_vars_name_list = [norm_names[x] for x in par_vars_name_list]

    return (norm_var_name, relationship, norm_par_vars_name_list)

def normalize_dataflow(dataflow):
    var_dict = {}
    i = 0
    normalized_dataflow = []
    for item in dataflow:
        var_name = item[0]
        relationship = item[2]
        par_vars_name_list = item[3]
        for name in par_vars_name_list:
            if name not in var_dict:
                var_dict[name] = 'var_'+str(i)
                i += 1
        if var_name not in var_dict:
            var_dict[var_name] = 'var_'+str(i)
            i+= 1
        normalized_dataflow.append((var_dict[var_name], relationship, [var_dict[x] for x in par_vars_name_list]))
    
    return normalized_dataflow


# In[37]:


"""

FONCTION FINALE POUR CALCULER LE SCORE FINALE DE CODEBLEU


"""

def calculateCodeBleuScore(all_score, hyperparams):
    codeBleuScore = 0
    
    for i in range (len(hyperparams)):
        codeBleuScore = codeBleuScore + (float(all_score[i] * hyperparams[i]))
    
    return codeBleuScore




""" MAIN FUNCTION """


def CodeBLEUMainFunction(candidate_code, correction_code, hyperparameters, lang, tokens_weighted):
    
    N = 4
    candidat_code = candidate_code
    reference_code = correction_code
    hyperparameters =hyperparameters
    # langage de programmation utiliser
    lang = lang
    # les tokens ponderes pour le BLEU weighted
    tokens_weighted = tokens_weighted
    
    
    ngrams_candidat, ngrams_references = getAllNGrams(candidat_code, reference_code, N)

    # OBTIENT LA PENALITE 
    brevity_penalite = getBrevityPenalty(candidat_code, reference_code)
    
    """ PARTIE BLEU"""

    # OBTIENT TOUS LES PRECISIONS DES N_GRAMS (1 a 4)
    precisions = getPrecisionPerGrams(ngrams_candidat, ngrams_references)
    print("Precisions des n-grams => ", precisions)

    # OBTIENT LA MOYENNE GEOMETRIQUE DE CES DIFFERENTS PRECISIONS
    geo_avg = getGeometryAvg(precisions)

    print("Moyenne Geometrique => ", geo_avg)

    #OBTIENT LE SCORE BLEU FINAL (APRES PENALITE)

    bleu_score = getBleuScore(geo_avg, brevity_penalite)
    
    
    """ PARTIE BLEU WEIGHTED """

    # calcul des precisions des n-grams ponderees
    weightedprecisions = weightedPrecisionsNgrams(tokens_weighted,ngrams_candidat, ngrams_references)
    print("Precisions n-grams weighted => ", weightedprecisions)

    # OBTIENT LA MOYENNE GEOMETRIQUE DE CES DIFFERENTS PRECISIONS
    geo_avg_weighted = getGeometryAvg(weightedprecisions)

    print("Moyenne Geometrique weighted => ", geo_avg_weighted)

    #OBTIENT LE SCORE BLEU FINAL (APRES PENALITE)

    bleu_weighted_score = getBleuScore(geo_avg_weighted, brevity_penalite)
    
    
    """  PARTIE AST  """


    # AST du code du candidat et AST du code reference 
    cand_ast_tree = getASTTree(candidat_code, lang)
    ref_ast_tree = getASTTree(reference_code, lang)

    # obtention des sous-arbres du code candidat et du code reference
    candidat_subtrees = getAllSubTrees(cand_ast_tree.root_node)
    reference_subtrees = getAllSubTrees(ref_ast_tree.root_node)

    # comparaison des 2 sous-arbres et renvoie du score
    astscore = getASTScore(candidat_subtrees, reference_subtrees)
    
    print("AST SCORE => ", astscore)

    
    """  PARTIE DATAFLOW  """

    dataflow_score = calc_dataflow_match([reference_code],candidat_code,'python')
    
    print("DATAFLOW SCORE => ", dataflow_score)
    
    """   OBTENTION DU SCORE CODEBLEU   """

    codeBleuScore = calculateCodeBleuScore([bleu_score, bleu_weighted_score, astscore, dataflow_score], hyperparameters)
    
    return codeBleuScore


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




