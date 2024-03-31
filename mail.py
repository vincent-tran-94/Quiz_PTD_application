from flask import render_template, redirect, url_for, flash
from models import *
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import request

app.config.from_pyfile('config.cfg')

# Initialiser Flask-Mail
mail = Mail(app)

# Clé secrète pour la création de tokens
SECRET_KEY = app.secret_key # Changez ceci par une clé réelle et sécurisée

# Serializer pour générer et vérifier les tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)


# Fonction pour envoyer l'e-mail de confirmation
def send_confirmation_email(user_id, email):

    token = serializer.dumps(user_id)  # Générer le token avec l'ID de l'utilisateur
    confirm_url = url_for('confirm_email', token=token, _external=True)  # URL de confirmation avec le token

    # Créer le message
    msg = Message('Confirmation d\'inscription', # Remplacez par votre adresse e-mail
                recipients=[email])
    
    # Corps du message au format HTML avec une image
    msg.html = f"<p>Cliquez sur le lien suivant pour participer au quiz: <a href='{confirm_url}'>{confirm_url}</a></p>" \
            f"<p>Vous avez moins d'une heure pour confirmer votre lien</p>"\
            f"<p>Association Préserve ton droit.</p>"
    
    # Envoyer l'e-mail
    mail.send(msg)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # Récupérer l'user_id associé au token 
        user_id_token = serializer.loads(token,max_age=3600)

        # Récupérer l'email à partir de l'user_id
        user = User.query.get(user_id_token)
        email = user.email

        if email:
            # Récupérer l'EmailID associé au token
            user__confirmation_id = User.query.filter_by(id=user_id_token).first()

            if user__confirmation_id:
                #login_user(user)  # Connecter l'utilisateur
                return redirect(url_for('login'))
            else:
                return render_template('confirmation.html', message='User ID no detected')
        else:
            return render_template('confirmation.html', message='Mail no detected')
        
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
    msg.html =  f"<p>Pour réinitialiser votre mot de passe, veuillez cliquer sur le lien suivant: <a href='{reset_link}'> {reset_link} </a></p>"\
                f"<p>Vous avez moins d'une heure pour confirmer votre lien</p>"\
                f"<p>Association Préserve ton droit.</p>"
    mail.send(msg)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email= serializer.loads(token, max_age=3600)
        user = User.query.filter_by(email=email).first()

        if request.method == 'POST':
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            if user.check_password(old_password):
                user.set_password(new_password,method='pbkdf2:sha256')
                db.session.commit()
                return render_template('confirmation.html', message='Mot de passe mis à jour avec succès.') 
            else:
                flash('Mot de passe actuel incorrect.','error')
        return render_template('reset_password.html',token=token)
    except SignatureExpired:
        # Le token a expiré
        return render_template('confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('confirmation.html', message='Lien de confirmation invalide.')
    

