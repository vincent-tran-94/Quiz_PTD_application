from models import *
import uuid 
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager,login_required, logout_user, login_user
from sqlalchemy.orm.exc import NoResultFound
from vizualisation import *
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
    return db.session.get(User,user_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash("Vous avez été déconnecté avec succès", "success")
    return redirect(url_for('login'))

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

@app.route('/accueil')
@login_required
def accueil():
    image_filename = 'images/logo_PTD.jpg'
    image_background = 'images/background_image.jpg'
    image_background_contact = 'images/contact_us_background.jpg'
    return render_template('home.html',image_filename=image_filename,image_background=image_background,image_background_contact=image_background_contact)
    

@app.route('/categorie/<categorie>', methods=['GET', 'POST'])
@login_required
def categorie_questions(categorie):
    participant_id = session.get('user_id')
    reponse_existe = ReponseParticipant.query.filter_by(participant_id=participant_id, categorie=categorie).first()

    if categorie in ['droit', 'humanitaire', 'culturel', 'sociologie']:
        data_json = open_file_json(categorie)

    if reponse_existe:
        flash("Vous avez déjà soumis les réponses pour cette catégorie.", "info")
        return redirect(url_for('accueil'))

    elif categorie == 'resultats':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        traitement_reponses(data_json, categorie)
        return redirect(url_for('accueil'))
    
    return render_template('categorie.html', questions=data_json['questions'],categorie=categorie)


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


@app.route('/dashboard')
@login_required
def dashboard():
    image_filename = 'images/logo_PTD.jpg'

    ReponsesParticipant = ReponseParticipant.query.all()
    if ReponsesParticipant:
        graph_json_success = get_participants_success_percentage()
        graph_json_participants = get_participants_count_by_category()
        graph_json_participants_month = get_participants_by_month()
        graph_json_top_participants = get_top_participants()

        return render_template('dashboard.html', graph_json_success=graph_json_success, 
                            graph_json_participants=graph_json_participants, 
                            graph_json_participants_month= graph_json_participants_month,
                            graph_json_top_participants=graph_json_top_participants,
                            image_filename=image_filename)
    else: 
        return redirect(url_for('accueil'))

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
            msg = Message(f'Nouveau message du contact de la part de {nom}',sender=sender, recipients=['timeroyal@gmail.com'],body=f"Nom: {nom}\nEmail: {email}\n Tel: {tel}, Message: {message}")
            mail.send(msg)
        except Exception as e:
            print('Une erreur s\'est produite lors de l\'envoi du message.')
            print(e)
            
    return redirect(url_for('accueil'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='192.168.0.44',port=9400)
