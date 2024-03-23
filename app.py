from models import *
import uuid 
from flask import render_template, request, redirect, url_for, session
from flask_login import LoginManager,login_required
import plotly
import plotly.graph_objs as go
import json
from mail import *

# Créez une instance de LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


def open_file_json(name_json):
    with open(f'questions/{name_json}.json', 'r',encoding='utf-8') as file:
        data_json = json.load(file)
        return data_json

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(EmailID, user_id)

@app.route('/', methods=['GET', 'POST'])
def formulaire():
    image_filename = 'images/logo_PTD.jpg'
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        niveau_etude = request.form['niveau_etude']
        statut = request.form['statut']
        centre_interet = request.form['centre_interet']
        choix_categorie = request.form['choix_categorie']
        champs_requis = [nom, prenom, email, niveau_etude, statut, centre_interet, choix_categorie]

        if not champs_requis:
            return render_template('formulaire.html', message="Veuillez remplir tous les champs.")
        
        # Générer un ID utilisateur unique
        user_id = str(uuid.uuid4())

        #Stockage dans une variable temporaire
        session['user_id'] = user_id

        participant = Participant(id=user_id,
                                  nom=nom, 
                                  prenom=prenom, 
                                  email=email, 
                                  niveau_etude=niveau_etude,
                                  statut=statut,
                                  centre_interet=centre_interet, 
                                  choix_categorie=choix_categorie)

        db.session.add(participant)
        db.session.commit()
        send_confirmation_email(user_id, email)

        return render_template('confirmation.html', message='Un e-mail de confirmation a été envoyé à votre adresse.')

    return render_template('formulaire.html', message=None,image_filename=image_filename)

@app.route('/accueil')
@login_required
def accueil():
    image_filename = 'images/logo_PTD.jpg'
    image_background = 'images/background_image.jpg'
    return render_template('home.html',image_filename=image_filename,image_background=image_background)
    

@app.route('/categorie/<categorie>', methods=['GET', 'POST'])
@login_required
def categorie_questions(categorie):
    if categorie == 'droit':
        message = "droit"
        data_json = open_file_json(categorie)

    elif categorie == 'humanitaire':
        message = "humanitaire"
        data_json = open_file_json(categorie)

    elif categorie == 'culturel':
        message = "culturel"
        data_json = open_file_json(categorie)
    
    elif categorie == 'resultats':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        traitement_reponses(data_json, categorie)
        return redirect(url_for('accueil'))
    
    return render_template('categorie.html', questions=data_json['questions'],message=message)


def traitement_reponses(data_json, categorie):
    participant_id = session.get('user_id')
    answers = request.form
    correct_answers = 0

    # Vérifiez les réponses
    for question in data_json['questions']:
        question_id = question['question']
        if answers.get(question_id) == question['reponse_correcte']:
            correct_answers += 1  # 1 point par bonne réponse

    # Calculez les statistiques
    total_questions = len(data_json['questions'])
    incorrect_answers = total_questions - correct_answers
    success_percentage = round((correct_answers / total_questions) * 100,2)

    # Créez une instance de ReponseParticipant et ajoutez-la à la base de données 
    reponse_participant = ReponseParticipant(participant_id=participant_id,
                                             correct_answers=correct_answers,
                                             incorrect_answers=incorrect_answers,
                                             success_percentage=success_percentage,
                                             categorie=categorie)
    db.session.add(reponse_participant)
    db.session.commit()


def get_participants_count_by_category():
    categories = []
    participants_counts = []

    # Récupérer le nombre de participants pour chaque catégorie
    categories_data = db.session.query(ReponseParticipant.categorie, db.func.count(ReponseParticipant.participant_id))\
                                 .group_by(ReponseParticipant.categorie).all()

    for _, (category, count) in enumerate(categories_data):
        categories.append(category)
        participants_counts.append(count)

    return categories, participants_counts


@app.route('/dashboard')
@login_required
def dashboard():
    # Graphique pour le taux de réussite par catégorie
    categories = []
    success_percentages = []

    # Récupérer les données de succès pour chaque catégorie
    categories_data = db.session.query(ReponseParticipant.categorie, db.func.avg(ReponseParticipant.success_percentage))\
                                 .group_by(ReponseParticipant.categorie).all()

    for _, (category, success_percentage) in enumerate(categories_data):
        categories.append(category)
        success_percentages.append(success_percentage)

    colors = {'droit': 'rgb(31, 119, 180)', 
              'humanitaire': 'rgb(44, 160, 44)', 
              'culturel': 'rgb(23, 190, 207)'}

    bar_chart_success = go.Bar(
        x=categories,
        y=success_percentages,
        text=success_percentages,
        textposition='auto',
        marker=dict(color=[colors[cat.lower()] for cat in categories]),
        opacity=0.6
    )

    layout_success = go.Layout(
        title="Graphique illustrant la moyenne des taux de réussite par catégorie pour tous les participants.",
        xaxis=dict(title='Catégorie'),
        yaxis=dict(title='Pourcentage de succès'),
    )

    fig_success = go.Figure(data=[bar_chart_success], layout=layout_success)
    graph_json_success = json.dumps(fig_success, cls=plotly.utils.PlotlyJSONEncoder)

    # Graphique pour le nombre de participants par catégorie (diagramme circulaire)
    categories_participants, participants_counts = get_participants_count_by_category()

    pie_chart_participants = go.Pie(
        labels=categories_participants,
        values=participants_counts,
        hole=0.3
    )

    layout_participants = go.Layout(
        title="Nombre de participants par catégorie",
    )

    fig_participants = go.Figure(data=[pie_chart_participants], layout=layout_participants)
    graph_json_participants = json.dumps(fig_participants, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html', graph_json_success=graph_json_success, graph_json_participants=graph_json_participants)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
