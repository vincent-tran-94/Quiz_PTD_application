from models import *
from flask import render_template, request, redirect, url_for, session, flash, make_response
from flask_login import LoginManager,login_required, logout_user, login_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from vizualisation import *
from launch_stripe import * 
from mail import *
from data_process import *
from permission import * 
import csv
import io
from process_stripe import *
from functools import wraps


"""
CONSIGNES POUR LANCER l'APPLICATION:
1) Créer un environnement virtuel et lancer les dépendances
python3 -m venv env
source env/Scripts/activate
(venv) pip install -r requirements.txt 
2) Dans config.cfg et .env changer les paramètres désignés
3) Lancer la commande test.sh pour tester l'application et run.sh pour lancer le conteneur
"""

MAX_INACTIVITY_DURATION=30

# Créez une instance de LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@app.context_processor
def utility_processor():
    return dict(zip=zip)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Veuillez vous connecter pour accéder à cette fonctionnalité", "error")
            return redirect(url_for('accueil'))  # Rediriger vers la page de connexion
        return f(*args, **kwargs)
    return decorated_function

#Middleware pour vérifier l'inactivité de l'utilisateur
@app.before_request
def check_inactive_session():
    if current_user.is_authenticated:
        last_activity = session.get('last_activity')
        if last_activity is not None:
            last_activity_naive = last_activity.replace(tzinfo=None)
            # Calculer la durée depuis la dernière activité
            inactive_duration = datetime.now() - last_activity_naive
            if inactive_duration > timedelta(minutes=MAX_INACTIVITY_DURATION):
                # Déconnecter l'utilisateur
                logout_user()
                session.pop('user_id', None)
                flash("Votre session a expiré en raison d'une inactivité prolongée", "warning")
                return redirect(url_for('accueil'))
    # Mettre à jour le temps de la dernière activité à chaque requête
    session['last_activity'] = datetime.now()
    

#Fonction de la première connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    image_filename = 'images/logo_PTD.jpg'

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Recherche de l'utilisateur dans la base de données
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if current_user.is_authenticated:
                flash("Vous êtes déjà connecté", "info")
            else:
                login_user(user)
                session['last_activity'] = datetime.now()
                session['user_id'] = user.id
                participant = Participant.query.filter_by(participant_id=user.id).first()
                if participant:
                    return redirect(url_for('accueil'))  # Rediriger vers la page de catégorie
                else:
                    return redirect(url_for('formulaire'))  # Rediriger vers le formulaire si l'utilisateur n'a pas rempli
        else:
            flash("Nom d'utilisateur ou mot de passe invalide", "error")  # Message flash pour l'erreur
        
    return render_template('setup_user/login.html',image_filename=image_filename)


#Fonction de déconnexion
@app.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None)
    flash("Vous avez été déconnecté avec succès", "success")
    return redirect(url_for('accueil'))


#Fonction de changement de mot de passe en cas de problème 
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            user = User.query.filter_by(email=email).one()
            reset_password_email(user)
            return render_template('setup_user/confirmation.html', message='Un lien de réinitialisation de mot de passe a été envoyé à votre adresse e-mail.')
        except NoResultFound:
            return render_template('setup_user/confirmation.html', message='Adresse e-mail non trouvée.')
        
    return render_template('setup_user/forgot_password.html')


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        email = request.form['email']
        try: 
            user = User.query.filter_by(email=email).one()
            delete_account_email(user)
            return render_template('setup_user/confirmation.html', message='Un lien de suppresion de compte a été envoyé à votre adresse e-mail.')
        except NoResultFound:
            return render_template('setup_user/confirmation.html', message='Adresse e-mail non trouvée.')
        
    return render_template("setup_user/delete_account.html")


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
            send_confirmation_email(nom=nom,prenom=prenom,email=email,password=password)
                   
            return render_template('setup_user/confirmation.html', message='Un e-mail de confirmation a été envoyé à votre adresse.')
        else:
            return render_template('setup_user/confirmation.html', message='Vous êtes déjà inscrit.')


    return render_template('setup_user/register.html')



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
        pays = request.form['pays']
        niveau_etude = request.form['niveau_etude']
        statut = request.form['statut']
        centre_interet = request.form['centre_interet']
        choix_categorie = request.form['choix_categorie']
        champs_requis = [nom, prenom, adresse,code_postal,ville,pays, niveau_etude, statut, centre_interet, choix_categorie]

        if not champs_requis:
            return render_template('formulaire.html', message="Veuillez remplir tous les champs.")
        

        participant = Participant(participant_id=participant_id,
                                  nom=nom, 
                                  prenom=prenom, 
                                  adresse=adresse,
                                  code_postal=code_postal,
                                  ville=ville,
                                  pays=pays,
                                  niveau_etude=niveau_etude,
                                  statut=statut,
                                  centre_interet=centre_interet, 
                                  choix_categorie=choix_categorie)
        db.session.add(participant)
        db.session.commit()
        return redirect(url_for('accueil'))

    return render_template('formulaire.html', message=None,image_filename=image_filename)


#Fonction de l'affichage page d'accueil
@app.route('/')
def accueil():
    session.pop('selected_questions', None)
    session.pop('answers', None)
    image_filename = 'images/logo_PTD.jpg'
    image_background = 'images/background_image.jpg'
    image_background_contact = 'images/contact_us_background.jpg'
    return render_template('sidebar/home.html',image_filename=image_filename,image_background=image_background,image_background_contact=image_background_contact)


@app.route('/profil')
def profil():
    participant_id = session.get('user_id')
    user = Participant.query.get(participant_id)
    return render_template('sidebar/profil.html', user=user)


#Fonction de contact client avec l'association
@app.route('/contact', methods=['GET', 'POST'])
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

def get_all_options(questions):
    all_options = []
    for question in questions:
        if 'options' in question:
            all_options.append(question['options'])
        elif 'multi_options' in question:
            all_options.append(question['multi_options'])

    return all_options

def get_all_explications(questions): 
    all_explications = [] 
    for question in questions: 
        all_explications.append(question['explication'])
    return all_explications


# Chemin de base où se trouvent les dossiers des catégories

@app.route('/choice_categories/<choice_categorie>', methods=['GET', 'POST'])
@login_required
def choice_categories(choice_categorie):
    BASE_DIR = 'questions'  # Remplacez par le chemin réel où se trouvent vos dossiers de catégories
    # Initialiser la liste des sujets
    list_subjects = [] 

    # Construire le chemin vers le dossier de la catégorie choisie
    category_path = os.path.join(BASE_DIR, choice_categorie)
    
    if os.path.exists(category_path) and os.path.isdir(category_path):
        # Récupérer la liste des fichiers JSON dans le dossier et enlever l'extension .json
        list_subjects = [
            os.path.splitext(subject)[0] for subject in os.listdir(category_path)
            if os.path.isfile(os.path.join(category_path, subject)) and subject.endswith('.json')
        ]

    if request.method == 'POST':
        selected_subject = request.form.get('selected_subject')
        return redirect(url_for('categorie_questions', categorie=choice_categorie, sujet=selected_subject))

    # Renvoyer le template avec les sujets
    return render_template('choice_subject.html', choice_categorie=choice_categorie, list_subjects=list_subjects)



@app.route('/categorie/<categorie>/<sujet>', methods=['GET', 'POST'])
@login_required
def categorie_questions(categorie,sujet):
    participant_id = session.get('user_id')
    reponse_existe = ReponseParticipant.query.filter_by(participant_id=participant_id, categorie=categorie,sujet=sujet).first()

    if reponse_existe:
        nb_essais_restant = reponse_existe.nb_essais
        if nb_essais_restant == 0:
            flash("Vous avez déjà soumis les réponses pour cette catégorie.", "info")
            return redirect(url_for('accueil'))
        else:
            reponse_existe.nb_essais -= 1

    categories_directories = {
        'droit': 'questions/droit',
        'humanitaire': 'questions/humanitaire',
        'culturel': 'questions/culturel',
        'sociologie': 'questions/sociologie'
    }

    directory = os.path.join(categories_directories[categorie], f"{sujet}.json")

    #Récupérer les 15 premiers questions pour chaque utilisateur
    if 'selected_questions' not in session:
        session['selected_questions'] = save_questions(directory)

    selected_questions = session['selected_questions']
    total_questions = len(selected_questions['questions'])
    all_options = get_all_options(selected_questions['questions'])
    all_explications = get_all_explications(selected_questions['questions'])

    #Stocker tout les réponses pour chaque question répondu
    if 'answers' not in session:
        session['answers'] = {}

    if request.method == 'POST':
        current_question_index = int(request.form['current_question_index'])

        action = request.form.get('action', 'submit')  # Valeur par défaut à 'submit' si le temps s'écoule pour chaque action effectué
        answer = request.form.getlist('answer')  #Valeur de réponse stockée dans une liste temporaire

        question_text = selected_questions['questions'][current_question_index]['question']
        session['answers'][question_text] = answer
 
        if action == 'next' and current_question_index < total_questions - 1:
            current_question_index += 1
        elif action == 'previous' and current_question_index > 0:
            current_question_index -= 1
        elif action == 'submit'or current_question_index >= total_questions - 1:
            traitement_reponses(selected_questions,all_options,categorie,sujet,all_explications)
            return redirect(url_for('progression'))

        current_question = selected_questions['questions'][current_question_index]
    else:
        current_question_index = 0
        current_question = selected_questions['questions'][current_question_index]

    # Récupérer les réponses enregistrées pour la question actuelle
    saved_answers = session['answers'].get(current_question['question'], [])

    return render_template('categorie.html', 
                           current_question=current_question, 
                           current_question_index=current_question_index,
                           total_questions=total_questions,
                           saved_answers=saved_answers,
                           categorie=categorie,
                           sujet=sujet,
                           participant_id=participant_id)

@app.route('/details/<categorie>/<sujet>', methods=['GET'])
@login_required
def details(categorie,sujet):
    participant_id = session.get('user_id')

    # Récupérer les réponses du participant pour cette catégorie
    responses = ReponseParticipant.query.filter_by(participant_id=participant_id, categorie=categorie,sujet=sujet).first()

    # Si pas de réponse pour cette catégorie
    if not responses:
        flash("Aucune réponse trouvée pour cette catégorie.", "warning")
        return redirect(url_for('progression'))
    else:
        selected_questions = responses.selected_questions
        participant_answers = responses.answers
        options_dict = responses.options
        explication = responses.explication
        correct_responses_dict = responses.correct_responses_dict


    return render_template('details.html', 
                           questions=selected_questions,
                           correct_responses_dict=correct_responses_dict,
                           options_dict=options_dict,
                           participant_answers=participant_answers,
                           explication=explication,
                           categorie=categorie,
                           sujet=sujet
                           )


#Fonction des résultats obtenus après le remplissage des questionnaires
@app.route('/progression')
@login_required
def progression():
    participant_id = session.get('user_id')
    
    # Récupérer les résultats du participant depuis la base de données
    participant_results = ReponseParticipant.query.filter_by(participant_id=participant_id).all()

    # Vous pouvez également récupérer d'autres informations pertinentes ici, par exemple, le nom du participant, etc.
    participant_info = Participant.query.filter_by(participant_id=participant_id).first()
    
    return render_template('progression.html', participant_results=participant_results, participant_info=participant_info)

@app.route('/download_csv')
@login_required
def download_csv():
    participant_id = session.get('user_id')
    
    # Récupérer les résultats du participant depuis la base de données
    participant_results = ReponseParticipant.query.filter_by(participant_id=participant_id).all()

    # Créer un fichier CSV en mémoire
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Écrire l'en-tête du fichier CSV
    writer.writerow(['Catégorie', 'Sujets','Réponses correctes', 'Réponses incorrectes', 'Succès pourcentage'])

    # Écrire les données de chaque résultat dans le fichier CSV
    for result in participant_results:
        writer.writerow([
            result.categorie,
            result.sujet,
            result.correct_answers,
            result.incorrect_answers,
            result.success_percentage
        ])

    # Préparer le contenu du fichier CSV pour le téléchargement
    output.seek(0)
    response = make_response(output.getvalue().encode('utf-8-sig'))
    response.headers['Content-Disposition'] = 'attachment; filename=donnees_participant.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    
    return response


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

            
            return render_template('sidebar/dashboard.html', graph_json_success=graph_json_success, 
                            graph_json_participants=graph_json_participants, 
                            graph_json_participants_month= graph_json_participants_month,
                            top_participants=indexed_filtered_participants, 
                            selected_month=month,
                            selected_year=year,
                            image_filename=image_filename)


        return render_template('sidebar/dashboard.html', graph_json_success=graph_json_success, 
                            graph_json_participants=graph_json_participants, 
                            graph_json_participants_month= graph_json_participants_month,
                            top_participants=indexed_top_participants, 
                            image_filename=image_filename)
    else: 
        return redirect(url_for('accueil'))
    
@app.route("/my_subscriptions")
@login_required  
def my_subscriptions():
    # check if a record exists for them in the StripeCustomer table
    subscriptions = StripeCustomer.query.filter_by(participant_id=current_user.id).all()
    # Récupérez les essais restants pour chaque catégorie
    essais_restants = ReponseParticipant.query.filter_by(participant_id=current_user.id).all()
    
    # Créez un dictionnaire pour stocker les essais restants par catégorie
    essais_restants_par_categorie = {}
    for essai_restant in essais_restants:
        essais_restants_par_categorie[essai_restant.categorie] = essai_restant.nb_essais 
    return render_template("sidebar/my_subscriptions.html", subscriptions=subscriptions, essais_restants_par_categorie=essais_restants_par_categorie)

@app.route("/parrainage",methods=['GET', 'POST'])
@login_required
def parrainage():
    message = None
    coupon_parrain = None
    participant_email = current_user.email

    if request.method == 'POST':
        parrain_email = request.form['parrain_email']

        # Vérifier si le parrain existe
        participant_own_parrain = Parrainage.query.filter_by(email=participant_email).first()
        participant_existe = Parrainage.query.filter_by(email=parrain_email).first()
        parrainage_existe = Parrainage.query.filter_by(parrain_email=parrain_email).first()
        parrain_inscrit =  User.query.filter_by(email=parrain_email).first()

        if participant_own_parrain:
            message = "Vous avez déjà été parrainé."
        elif participant_email  == parrain_email:
            message = "Vous ne pouvez pas utiliser la même adresse e-mail que votre parrain."
        elif not parrain_inscrit:
            message = "Votre mail du parrain n'a pas été inscrit"
        elif parrainage_existe or participant_existe:
            message = "Ce participant a déjà un parrain."
        else:
            # Créer un code de parrainage
            coupon_parrain = create_promotion_code(coupon_id)

            # Enregistrer le parrainage dans la base de données
            parrainage = Parrainage(participant_id=current_user.id, email=participant_email, 
                                    parrain_email=parrain_email, coupon_parrain=coupon_parrain)
            db.session.add(parrainage)
            db.session.commit()
            message = "Le parrainage a été créé avec succès"
        

    return render_template('parrain.html', message=message, coupon_parrain=coupon_parrain)


@app.route('/cancel_subscription',methods=['POST'])
@login_required
def cancel_subscription():
    if request.method == 'POST':
        return redirect('confirm_cancel_subscription')
    
@app.route('/confirm_cancel_subscription',methods=['GET', 'POST'])
@login_required
def confirm_cancel_subscription():
    message = None
    # Get subscription ID from request
    customer_email = StripeCustomer.query.filter_by(email=current_user.email).first()
    if customer_email:
        get_subscription_id = customer_email.id_subscription
        get_customer_email = customer_email.email
        if request.method == 'POST':
            # Cancel the subscription
            stripe.Subscription.cancel(get_subscription_id)

            scheduler.remove_job(str(current_user.id))
            # Delete StripeCustomer record
            db.session.delete(customer_email)
            db.session.commit()

            message = f"Votre abonnement a été résilié avec succès. Aucune facture ne sera générée pour les mois à venir."
            send_cancel_sub_email(message,get_customer_email)
            print(f"Subcription canceled by {customer_email}")

    return render_template("cancel_sub.html", message=message)


@app.route('/souscription')
@login_required
def souscription():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': id_product_bronze,
            'quantity': 1,
        }],
        subscription_data={
            'default_tax_rates': [taxe_rate],
        },
        mode='subscription',
        allow_promotion_codes=True,
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('souscription', _external=True),
    )
    return render_template('sidebar/souscription.html', checkout_session_id=session['id'], checkout_public_key=app.config['STRIPE_PUBLIC_KEY'])

