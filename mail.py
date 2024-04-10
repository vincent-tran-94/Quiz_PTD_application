from flask import render_template, redirect, url_for, flash
from forms import *
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import request


"""
Fonctions de fonctionnalité de login et d'inscription via par mail (on peut changer de mot de passe):
-Confirmation d'envoi par mail pour chaque utilisateur
-Changement de mot de passe en cas d'oubli de mot de passe
"""


app.config.from_pyfile('config.cfg')

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

        user__confirmation_id = User.query.filter_by(id=user_id,email=email).first()

        if user__confirmation_id:
            return redirect(url_for('login'))
        else:
            return render_template('confirmation.html', message='Mail or User ID no detected')
        
    except SignatureExpired:
        # Le token a expiré
        return render_template('confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('confirmation.html', message='Lien de confirmation invalide.')


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
            # Supprimer le compte
            ReponseParticipant.query.filter_by(participant_id=user.id).delete()
            Contact.query.filter_by(participant_id=user.id).delete()
            Participant.query.filter_by(participant_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
        return render_template('confirmation.html', message='Votre compte a été bien supprimé.') 
    except SignatureExpired:
        # Le token a expiré
        return render_template('confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('confirmation.html', message='Lien de confirmation invalide.')


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
                return render_template('confirmation.html', message='Mot de passe mis à jour avec succès.')

        return render_template('reset_password.html',token=token)
    except SignatureExpired:
        # Le token a expiré
        return render_template('confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('confirmation.html', message='Lien de confirmation invalide.')
    

