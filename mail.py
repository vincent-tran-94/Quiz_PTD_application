from flask import render_template, redirect, url_for
from models import *
from flask_login import login_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app.config.from_pyfile('config.cfg')
# Initialiser Flask-Mail
mail = Mail(app)

# Clé secrète pour la création de tokens
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/' # Changez ceci par une clé réelle et sécurisée

# Serializer pour générer et vérifier les tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)


# Fonction pour envoyer l'e-mail de confirmation
def send_confirmation_email(user_id, email):
    token = serializer.dumps(user_id)  # Générer le token avec l'ID de l'utilisateur
    confirm_url = url_for('confirm_email', token=token, _external=True)  # URL de confirmation avec le token

    # Créer le message
    msg = Message('Confirmation d\'inscription',
                  sender='timeroyal@gmail.com',  # Remplacez par votre adresse e-mail
                  recipients=[email])
    msg.body = f'Cliquez sur le lien suivant pour confirmer votre inscription : {confirm_url}'
    
    # Envoyer l'e-mail
    mail.send(msg)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # Vérifier et récupérer l'ID de l'utilisateur 1H de vérification
        id_email = serializer.loads(token, max_age=3600)  
        
        # Récupérer le dernier participant
        last_participant = Participant.query.order_by(Participant.date_creation.desc()).first()
        
        # Créer un nouvel enregistrement EmailID avec les données du dernier participant
        new_email_id = EmailID(email=last_participant.email, mail_id=id_email)
        db.session.add(new_email_id)
        db.session.commit()

        # Effectuer des opérations de confirmation (par exemple, activer le compte dans la base de données)
        # Rediriger vers la page d'accueil avec un message de confirmation
        user = EmailID.query.filter_by(mail_id=id_email).first()
        if user:
            login_user(user)  # Connecter l'utilisateur
            return redirect(url_for('accueil'))
    
    except SignatureExpired:
        # Le token a expiré
        return render_template('confirmation.html', message='Le lien de confirmation a expiré.')
    except BadSignature:
        # Token invalide
        return render_template('confirmation.html', message='Lien de confirmation invalide.')

