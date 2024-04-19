from flask import render_template, redirect, url_for, flash
from models import *
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import request
from launch_stripe import *
import requests

"""
Fonctions de fonctionnalité de login et d'inscription via par mail (on peut changer de mot de passe):
-Confirmation d'envoi par mail pour chaque utilisateur
-Changement de mot de passe en cas d'oubli de mot de passe
"""

# Initialiser Flask-Mail
mail = Mail(app)

# Clé secrète pour la création de tokens
SECRET_KEY = app.secret_key # Changez ceci par une clé réelle et sécurisée

# Serializer pour générer et vérifier les tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Fonction pour envoyer l'e-mail de confirmation
def send_confirmation_email(nom,prenom,email,password):

    user_data = {'nom': nom, 'prenom': prenom, 'email': email, 'password': password}

    token = serializer.dumps(user_data)  # Générer le token avec l'ID de l'utilisateur
    confirm_url = url_for('confirm_email', token=token,_external=True)  # URL de confirmation avec le token

    # Créer le message
    msg = Message('Confirmation d\'inscription', # Remplacez par votre adresse e-mail
                recipients=[email])
    
    # Corps du message au format HTML avec une image
    msg.html = f"<p>Cliquez sur le lien suivant pour participer au quiz: <a href='{confirm_url}' target='_blank'>{confirm_url}</a></p>" \
            f"<p>Vous avez moins d'une heure pour confirmer votre lien</p>"\
            f"<p>Association Préserve ton droit.</p>"
    
    # Envoyer l'e-mail
    mail.send(msg)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # Récupérer l'user_id associé au token 
        user_data = serializer.loads(token, max_age=3600)
        
        # Récupérer les données utilisateur depuis le token
        nom = user_data['nom']
        prenom = user_data['prenom']
        email = user_data['email']
        password = user_data['password']

        # Vérifier si l'utilisateur existe déjà dans la base de données
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('setup_user/confirmation.html', message='Vous avez déjà confirmé votre mail.')
        else:
            # Générer un nouvel ID utilisateur
            user_id = str(uuid.uuid4())

            # Créer un nouvel utilisateur confirmé dans la base de données
            new_user = User(id=user_id,
                            nom=nom, 
                            prenom=prenom, 
                            email=email)
            new_user.set_password(password, method='pbkdf2:sha256')        
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
           
    except SignatureExpired:
        # Le token a expiré
        return render_template('setup_user/confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('setup_user/confirmation.html', message='Lien de confirmation invalide.')


def reset_password_email(user):
    token = serializer.dumps(user.email)
    reset_link = url_for('reset_password', token=token, _external=True)
    msg = Message("Réinitialisation de mot de passe", recipients=[user.email])
    msg.html =  f"<p>Pour réinitialiser votre mot de passe, veuillez cliquer sur le lien suivant: <a href='{reset_link}' target='_blank'> {reset_link} </a></p>"\
                f"<p>Vous avez moins d'une heure pour confirmer votre lien</p>"\
                f"<p>Association Préserve ton droit.</p>"
    mail.send(msg)


def delete_account_email(user):
    token = serializer.dumps(user.email)
    reset_link = url_for('confirm_delete', token=token, _external=True)
    msg = Message("Suppression de votre compte", recipients=[user.email])
    msg.html =  f"<p>Pour supprimer votre compte, veuillez cliquer sur le lien suivant: <a href='{reset_link}' target='_blank'> {reset_link} </a></p>"\
                f"<p>Vous avez moins d'une heure pour confirmer votre lien</p>"\
                f"<p>Association Préserve ton droit.</p>"
    mail.send(msg)

@app.route('/confirm_delete/<token>', methods=['GET', 'POST'])
def confirm_delete(token):
    try:
        email= serializer.loads(token, max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            # Créez une liste des classes de modèles que vous souhaitez supprimer
            tables_to_delete = [ReponseParticipant, Contact, Participant, StripeCustomer, Parrainage]
            # Utilisez une boucle pour parcourir chaque classe de modèle et supprimer les entrées associées à l'utilisateur
            for table in tables_to_delete:
                table.query.filter_by(participant_id=user.id).delete()
            
            db.session.delete(user)
            db.session.commit()
        return render_template('setup_user/confirmation.html', message='Votre compte a été bien supprimé.') 
    except SignatureExpired:
        # Le token a expiré
        return render_template('setup_user/confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('setup_user/confirmation.html', message='Lien de confirmation invalide.')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email= serializer.loads(token, max_age=3600)
        user = User.query.filter_by(email=email).first()

        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password != confirm_password:
                flash('Les mots de passe ne correspondent pas.', 'error')
            elif user.check_password(new_password) or user.check_password(confirm_password):
                flash('Le nouveau mot de passe ne peut pas être identique à l\'ancien.', 'error')
            else:
                user.set_password(new_password, method='pbkdf2:sha256')
                db.session.commit()
                return render_template('setup_user/confirmation.html', message='Mot de passe mis à jour avec succès.')

        return render_template('setup_user/reset_password.html',token=token)
    except SignatureExpired:
        # Le token a expiré
        return render_template('setup_user/confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('setup_user/confirmation.html', message='Lien de confirmation invalide.')
    

# Fonction d'envoi d'e-mail
def send_invoice_email(invoice_id):
    invoice = stripe.Invoice.retrieve(invoice_id)
    customer_email = invoice.customer_email
    invoice_pdf_link = invoice.invoice_pdf
    name_product = invoice["lines"]["data"][0]["description"]
    # print("invoice",invoice)
    # print("customer_email",customer_email)

    msg = Message('Votre facture mensuelle', recipients=[customer_email])
    msg.body = f"Bonjour,\n\nVeuillez trouver ci-joint votre facture mensuelle pour le forfait d'abonnement: {name_product}.\n\nVeuillez vérifier vos spams ou dossier de courriers indésirables si vous ne trouvez pas ce message dans votre boîte de réception.\n\n Bien cordialement,\nAssociation Préserve ton droit"

    # Téléchargement du PDF de la facture
    pdf_content = requests.get(invoice_pdf_link).content

    msg.attach("invoice.pdf", "application/pdf", pdf_content)

    # Envoi de l'e-mail
    mail.send(msg)

def send_cancel_sub_email(message, customer_email):
    msg = Message("Annulation de l'abonnement", recipients=[customer_email])
    msg.body = message+"\nBien cordialement,\nAssociation Préserve ton droit"
    mail.send(msg)



