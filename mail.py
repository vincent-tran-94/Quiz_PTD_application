from flask import render_template, redirect, url_for
from models import *
from flask_login import login_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app.config.from_pyfile('config.cfg')

# Initialiser Flask-Mail
mail = Mail(app)

# Clé secrète pour la création de tokens
SECRET_KEY = app.secret_key # Changez ceci par une clé réelle et sécurisée

# Serializer pour générer et vérifier les tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)
sender = 'timeroyal@gmail.com'


# Fonction pour envoyer l'e-mail de confirmation
def send_confirmation_email(user_id, email):
    token = serializer.dumps(user_id)  # Générer le token avec l'ID de l'utilisateur

    confirm_url = url_for('confirm_email', token=token, _external=True)  # URL de confirmation avec le token

    # Créer le message
    msg = Message('Confirmation d\'inscription',
                  sender=sender,  # Remplacez par votre adresse e-mail
                  recipients=[email])
    msg.body = f"Cliquez sur le lien suivant pour participer au quiz: {confirm_url}\n\nVous disposez d'une heure pour confirmer votre inscription\nAssociation Préserve ton droit"
    
    # Envoyer l'e-mail
    mail.send(msg)

    new_email_id = EmailID(email=email, user_id=user_id)
    db.session.add(new_email_id)
    db.session.commit()


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # Récupérer l'user_id associé au token 
        user_id = serializer.loads(token, max_age=3600)  

        # Récupérer l'email à partir de l'user_id
        user = Participant.query.get(user_id)
        email = user.email 

        if email:
            # Récupérer l'EmailID associé au token
            user_id = EmailID.query.filter_by(user_id=user_id).first()

            if user_id:
                login_user(user_id)  # Connecter l'utilisateur
                return redirect(url_for('accueil'))
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

