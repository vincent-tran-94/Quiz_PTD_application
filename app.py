from models import *
import uuid 
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager,login_required, logout_user, login_user
from sqlalchemy.orm.exc import NoResultFound
from vizualisation import *
from mail import *
from data_process import *


"""
CONSIGNES POUR LANCER l'APPLICATION:
1) Créer un environnement virtuel et lancer les dépendances
python3 -m venv env
source env/Scripts/activate
(venv) pip install -r requirements.txt 
2) Dans config.cfg: Configurer votre serveur SMTP en changeant votre MAIL_USERNAME et le MAIL_DEFAULT_SENDER
MAIL_SERVER='smtp.gmail.com'
MAIL_USERNAME='votreadresse@gmail.com'
MAIL_DEFAULT_SENDER = 'votreadresse@gmail.com'
MAIL_PASSWORD='Votre mot de passe'
3) Configurer l'addresse IP de l'hôte et de votre port dans le fichier app.py
3) Lancer le fichier run.sh
chmod +x run.sh
./run.sh
"""

#Host configuration and port 
host='0.0.0.0'
port=5000
mail_association = 'timeroyal@gmail.com'


# Créez une instance de LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


#Fonction de la première connexion
@app.route('/', methods=['GET', 'POST'])
def login():
    image_filename = 'images/logo_PTD.jpg'
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Recherche de l'utilisateur dans la base de données
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            session['user_id'] = user.id
            participant = Participant.query.filter_by(participant_id=user.id).first()
            if participant:
                return redirect(url_for('accueil'))  # Rediriger vers la page de catégorie
            else:
                return redirect(url_for('formulaire'))  # Rediriger vers le formulaire si l'utilisateur n'a pas rempli
        else:
            flash("Nom d'utilisateur ou mot de passe invalide", "error")  # Message flash pour l'erreur
        
    return render_template('login.html',image_filename=image_filename)

#Fonction de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash("Vous avez été déconnecté avec succès", "success")
    return redirect(url_for('login'))


#Fonction de changement de mot de passe en cas de problème 
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            user = User.query.filter_by(email=email).one()
            reset_password_email(user)
            return render_template('confirmation.html', message='Un lien de réinitialisation de mot de passe a été envoyé à votre adresse e-mail.')
        except NoResultFound:
            return render_template('confirmation.html', message='Adresse e-mail non trouvée.')
        
    return render_template('forgot_password.html')


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        email = request.form['email']
        try: 
            user = User.query.filter_by(email=email).one()
            delete_account_email(user)
            return render_template('confirmation.html', message='Un lien de suppresion de compte a été envoyé à votre adresse e-mail.')
        except NoResultFound:
            return render_template('confirmation.html', message='Adresse e-mail non trouvée.')
        
    return render_template("delete_account.html")


#Fonction de désinscription
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
    
        existing_email = User.query.filter_by(email=email).first()
        if not existing_email:
            # Générer un ID utilisateur unique
            user_id = str(uuid.uuid4())

            inscription_user = User(id=user_id,
                                    nom=nom, 
                                    prenom=prenom, 
                                    email=email)

            inscription_user.set_password(password,method='pbkdf2:sha256')
            db.session.add(inscription_user)
            db.session.commit()
            send_confirmation_email(user_id, email)
            return render_template('confirmation.html', message='Un e-mail de confirmation a été envoyé à votre adresse.')
        else:
            return render_template('confirmation.html', message='Vous êtes déjà inscrit.')


    return render_template('register.html')




#Fonction de formulaire de renseignement du participant pour connaitre les informations du participant
@app.route('/formulaire', methods=['GET', 'POST'])
@login_required
def formulaire():
    image_filename = 'images/logo_PTD.jpg'
    participant_id = session.get('user_id')
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        adresse = request.form['adresse']
        code_postal = request.form['code_postal']
        ville = request.form['ville']
        niveau_etude = request.form['niveau_etude']
        statut = request.form['statut']
        centre_interet = request.form['centre_interet']
        choix_categorie = request.form['choix_categorie']
        champs_requis = [nom, prenom, adresse,code_postal,ville, niveau_etude, statut, centre_interet, choix_categorie]

        if not champs_requis:
            return render_template('formulaire.html', message="Veuillez remplir tous les champs.")
        

        participant = Participant(participant_id=participant_id,
                                  nom=nom, 
                                  prenom=prenom, 
                                  adresse=adresse,
                                  code_postal=code_postal,
                                  ville=ville,
                                  niveau_etude=niveau_etude,
                                  statut=statut,
                                  centre_interet=centre_interet, 
                                  choix_categorie=choix_categorie)

        db.session.add(participant)
        db.session.commit()
        return redirect(url_for('accueil'))

    return render_template('formulaire.html', message=None,image_filename=image_filename)

#Fonction de l'affichage page d'accueil
@app.route('/accueil')
@login_required
def accueil():
    image_filename = 'images/logo_PTD.jpg'
    image_background = 'images/background_image.jpg'
    image_background_contact = 'images/contact_us_background.jpg'
    return render_template('home.html',image_filename=image_filename,image_background=image_background,image_background_contact=image_background_contact)

#Fonction de contact client avec l'association
@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    participant_id = session.get('user_id')
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        tel = request.form['tel']
        message = request.form['message']
        
        contact = Contact(participant_id=participant_id,
                          nom=nom,
                          email=email,
                          tel=tel,
                          message=message)             
        db.session.add(contact)
        db.session.commit()

        try: 
            msg = Message(f'Application PTDlegalQuiz - Nouveau message de la part de {nom}', recipients=[mail_association],body=f"Nom: {nom}\nEmail: {email}\nTel: {tel}\nMessage: {message}")
            mail.send(msg)
        except Exception as e:
            print('Une erreur s\'est produite lors de l\'envoi du message.')
            print(e)
            
    return redirect(url_for('accueil'))



#Fonction pour se diriger le choix du catégorie 
@app.route('/categorie/<categorie>', methods=['GET', 'POST'])
@login_required
def categorie_questions(categorie):

    participant_id = session.get('user_id')
    reponse_existe = ReponseParticipant.query.filter_by(participant_id=participant_id, categorie=categorie).first()

    categories_directories = {
        'droit': 'questions/droit',
        'humanitaire': 'questions/humanitaire',
        'culturel': 'questions/culturel',
        'sociologie': 'questions/sociologie'
    }

    if categorie in categories_directories:
        directory = categories_directories[categorie]
        data_json = open_file_json_from_directory(directory)
    
    if reponse_existe:
        last_response_date = reponse_existe.date_creation
        # Si une semaine s'est écoulée, permettre de retenter
        if is_two_week_passed(last_response_date):
            reponse_existe.date_creation = get_current_date()
        else:
            # Sinon, rediriger vers la page d'accueil
            flash("Vous avez déjà soumis les réponses pour cette catégorie.", "info")
            return redirect(url_for('accueil'))

    elif categorie == 'resultats':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        traitement_reponses(data_json, categorie)
        return redirect(url_for('resultats'))
    
    return render_template('categorie.html', questions=data_json['questions'],categorie=categorie)

#Fonction des résultats obtenus après le remplissage des questionnaires
@app.route('/resultats')
@login_required
def resultats():
    participant_id = session.get('user_id')
    
    # Récupérer les résultats du participant depuis la base de données
    participant_results = ReponseParticipant.query.filter_by(participant_id=participant_id).all()
    
    # Vous pouvez également récupérer d'autres informations pertinentes ici, par exemple, le nom du participant, etc.
    participant_info = Participant.query.filter_by(participant_id=participant_id).first()
    
    return render_template('resultats.html', participant_results=participant_results, participant_info=participant_info)


#Fonction d'affichage des résultats et de visualisation avec un classement donné
@app.route('/dashboard',methods=['GET', 'POST'])
@login_required
def dashboard():
    image_filename = 'images/logo_PTD.jpg'

    ReponsesParticipant = ReponseParticipant.query.all()
    if ReponsesParticipant:
        graph_json_success = get_participants_success_percentage()
        graph_json_participants = get_participants_count_by_category()
        graph_json_participants_month = get_participants_by_month()
        top_participants = get_top_50_participants()
        indexed_top_participants = list(enumerate(top_participants, start=1))
    
        if request.method == 'POST':
            # Récupérer les données du formulaire de filtrage
            year = int(request.form.get('year'))  # Convertir le mois en entier
            month = int(request.form.get('month'))  # Convertir le mois en entier
            
            # Effectuer les opérations de filtrage en fonction du mois sélectionné
            filtered_participants = filter_data_by_month_year(top_participants, month,year)
            indexed_filtered_participants = list(enumerate(filtered_participants, start=1))

            
            return render_template('dashboard.html', graph_json_success=graph_json_success, 
                            graph_json_participants=graph_json_participants, 
                            graph_json_participants_month= graph_json_participants_month,
                            top_participants=indexed_filtered_participants, 
                            selected_month=month,
                            selected_year=year,
                            image_filename=image_filename)


        return render_template('dashboard.html', graph_json_success=graph_json_success, 
                            graph_json_participants=graph_json_participants, 
                            graph_json_participants_month= graph_json_participants_month,
                            top_participants=indexed_top_participants, 
                            image_filename=image_filename)
    else: 
        return redirect(url_for('accueil'))
    


#Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True,host=host,port=port)
