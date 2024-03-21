from models import *
import uuid 
from flask import render_template, request, redirect, url_for
import json

@app.route('/', methods=['GET', 'POST'])
def formulaire():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        niveau_etude = request.form['niveau_etude']
        centre_interet = request.form['centre_interet']
        choix_categorie = request.form['choix_categorie']

        if not (nom and prenom and email and niveau_etude and centre_interet and choix_categorie):
            return render_template('formulaire.html', message="Veuillez remplir tous les champs.")
        
        # Générer un ID utilisateur unique
        user_id = str(uuid.uuid4())

        participant = Participant(id=user_id,nom=nom, prenom=prenom, email=email, niveau_etude=niveau_etude,
                             centre_interet=centre_interet, choix_categorie=choix_categorie)
        db.session.add(participant)
        db.session.commit()

        return redirect(url_for('accueil'))

    return render_template('formulaire.html', message=None)

@app.route('/accueil')
def accueil():
    return render_template('home.html')

@app.route('/categorie/<categorie>')
def categorie(categorie):
    if categorie == 'droit':
        message = "Voici la troisième page pour le droit"
    elif categorie == 'humaniste':
        message = "Voici la troisième page pour le humaniste"
    elif categorie == 'juridique':
        message = "Voici la troisième page pour le juridique"
    else:
        message = "Catégorie non reconnue"

    return render_template('categorie.html', message=message)

# Chargez le fichier JSON
with open('questions/droit.json', 'r',encoding='utf-8') as file:
    droit_data = json.load(file)

@app.route('/categorie/droit', methods=['GET', 'POST'])
def droit():
    if request.method == 'POST':
        # Logique de traitement des réponses
        participant_id  = request.form['participant_id']
        answers = request.form
        correct_answers = 0

        # Vérifiez les réponses
        for question in droit_data['questions']:
            question_id = question['question']
            if answers.get(question_id) == question['reponse_correcte']:
                correct_answers += 1

        # Calculez les statistiques
        total_questions = len(droit_data['questions'])
        incorrect_answers = total_questions - correct_answers
        success_percentage = (correct_answers / total_questions) * 100

        # Créez une instance de ReponseParticipant et ajoutez-la à la base de données 
        reponse_participant = ReponseParticipant(participant_id=participant_id,
                                                 correct_answers=correct_answers,
                                                 incorrect_answers=incorrect_answers,
                                                 success_percentage=success_percentage)

        db.session.add(reponse_participant)
        db.session.commit()

        reponse_participant.correct_answers = correct_answers
        reponse_participant.incorrect_answers = incorrect_answers
        reponse_participant.success_percentage = success_percentage

        db.session.commit()

        return redirect(url_for('accueil'))

    # Affichez les questions dans le modèle HTML
    return render_template('categorie.html', questions=droit_data['questions'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
