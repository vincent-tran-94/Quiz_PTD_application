import os
import random
from models import *
from flask import request, session
import json
from sqlalchemy import func, extract, distinct

"""
Fonction de récupération de données et de procédure de données
-Les fichiers JSON sur l'ensemble des questionnaires
-Nom de participant
-Le pourcentage de réussite pour chaque catégorie
-Le mois et l'année répondu pour chaque participant
-Filtrage des données des participants en fonction du mois et de l'année sélectionné
-Traitement de réponse qui permet de calculer le nombre de réponses correctes et incorrectes pour chaque questionnaire dans une catégorie 
"""

selected_questions = []  

#Fonction pour récupérer tout les fichiers JSON sur l'ensemble des questionnaires
def open_file_json_from_directory(directory):
    json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
    if not json_files:
        return None
    all_questions = []

    for json_file in json_files:
        with open(os.path.join(directory, json_file), 'r', encoding='utf-8') as file:
            data_json = json.load(file)
            all_questions.extend(data_json['questions'])
    
    # Mélanger toutes les questions
    random.shuffle(all_questions)
    selected_questions = all_questions[:10]

    return selected_questions

def save_questions(directory):

    save_questions = open_file_json_from_directory(directory)
    
     # Ajouter des numérotations à chaque question
    for i, question in enumerate(save_questions, 1):
        question['number'] = i  # Ajouter un numéro à la questio
    
    # Créer un nouveau dictionnaire contenant les questions mélangées
    shuffled_data = {"questions": save_questions}
    #print("APRES",shuffled_data)

    return shuffled_data

#Fonction pour récupérer le nom du participant
def get_participant_name(participant_id):
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if participant:
        return f"{participant.nom} {participant.prenom}"
    else:
        return "Participant introuvable"

#Fonction pour récupérer le pourcentage de réussite pour chaque catégorie
def get_success_percentage_by_category(participant_id):
    categories = ['droit', 'humanitaire', 'culturel', 'sociologie']
    success_percentages = {}
    for category in categories:
        participant_results = ReponseParticipant.query.filter_by(participant_id=participant_id, categorie=category).first()
        if participant_results:
            success_percentages[category] = participant_results.success_percentage
        else:
            success_percentages[category] = 0.0
    return success_percentages

#Fonction pour récupérer le mois et l'année répondu pour chaque participant
def get_month_year(participant_id):
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if participant:
        month = participant.date_creation.strftime('%B')
        year = participant.date_creation.year
        return month, year
    else:
        return None, None
    
#Fonction pour récupérer les 10 premiers participants ayant répondu les questionnaires pour TOUT les catégories et seront affichés
#pour chaque mois et l'année
def get_top_50_participants():
    top_participants = db.session.query(ReponseParticipant.participant_id,
                                        extract('year', ReponseParticipant.date_creation).label('response_year'),
                                        extract('month', ReponseParticipant.date_creation).label('response_month'),
                                        func.avg(ReponseParticipant.success_percentage).label('total_success_percentage')) \
                                 .group_by(ReponseParticipant.participant_id, 
                                           extract('year', ReponseParticipant.date_creation),
                                           extract('month', ReponseParticipant.date_creation)) \
                                 .having(func.count(distinct(ReponseParticipant.categorie)) == 4) \
                                 .order_by(func.avg(ReponseParticipant.success_percentage).desc()) \
                                 .limit(50) \
                                 .all()
    
    top_participants_info = []
    for participant_id, response_year, response_month, total_success_percentage in top_participants:
        participant_name = get_participant_name(participant_id)
        top_participants_info.append((participant_name, response_year, response_month, total_success_percentage))
    
    return top_participants_info

#Fonction qui permet de filtrer les données des participants en fonction du mois et de l'année sélectionné
def filter_data_by_month_year(data, month, year):
    filtered_data = []
    for participant_name, response_year, response_month, total_success_percentage in data:
        if response_month == month and response_year == year:
            filtered_data.append((participant_name, response_year, response_month, total_success_percentage))
    return filtered_data

#Fonction de traitement de réponse qui permet de calculer le nombre de réponses correctes et incorrectes pour chaque questionnaire dans une catégorie 
def traitement_reponses(data_json, categorie):
    participant_id = session.get('user_id')
    answers = request.form
    correct_answers = 0

    # Initialiser un dictionnaire vide pour stocker les réponses
    result_dict_answers = {}

    # Parcourir les éléments de l'ImmutableMultiDict
    for key in answers.keys():
        # Vérifier si la clé est différente de 'participant_id'
        if key != 'participant_id':
            # Vérifier si la clé est déjà dans le dictionnaire résultant
            if key in result_dict_answers:
                # Si la clé existe déjà, ajouter la valeur à la liste existante
                result_dict_answers[key].append(answers.getlist(key))
            else:
                # Si la clé n'existe pas encore, créer une nouvelle liste avec la valeur
                result_dict_answers[key] = answers.getlist(key)

    # Créer un dictionnaire pour stocker les réponses correctes attendues pour chaque question
    correct_responses_dict = {question['question']: question['reponse_correcte'] if isinstance(question['reponse_correcte'], list) else [question['reponse_correcte']] for question in data_json['questions']}

    # Vérifiez les réponses
    for question_id, user_response in result_dict_answers.items():
        if question_id in correct_responses_dict:
            reponses_donnes =  correct_responses_dict[question_id]
            if isinstance(reponses_donnes, list):
                if set(reponses_donnes) == set(user_response):
                    correct_answers += 1
            elif isinstance(reponses_donnes, str):
                if reponses_donnes == user_response:
                    correct_answers  += 1

    # Calculez les statistiques
    total_questions = len(data_json['questions'])
    incorrect_answers = total_questions - correct_answers
    success_percentage = round((correct_answers / total_questions) * 100,2)
    default_essai = 1

    # Vérifiez si une réponse existe déjà pour ce participant dans cette catégorie
    existing_response = ReponseParticipant.query.filter_by(participant_id=participant_id, categorie=categorie).first()

    if existing_response:
        # Mettre à jour les données existantes
        existing_response.correct_answers = correct_answers
        existing_response.incorrect_answers = incorrect_answers
        existing_response.success_percentage = success_percentage
    else:
        # Ajouter un nouvel enregistrement pour ce participant et cette catégorie
        new_response = ReponseParticipant(participant_id=participant_id,
                                          correct_answers=correct_answers,
                                          incorrect_answers=incorrect_answers,
                                          success_percentage=success_percentage,
                                          categorie=categorie,
                                          nb_essais=default_essai)
        db.session.add(new_response)
    db.session.commit()



