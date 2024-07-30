from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import JSON


load_dotenv() #Importer les paramètres de l'identification
app = Flask(__name__,template_folder='template',static_url_path='/static')


# #Host configuration and port 
host = os.getenv("HOST")
port = os.getenv("PORT")
mail_association = os.getenv("MAIL_ASSOCIATION_CONTACT")

app.secret_key = os.getenv('SECRET_KEY')
db_uri = f"postgresql://{os.getenv('ID_DATABASE')}:{os.getenv('PASSWORD_DATABASE')}@{os.getenv('ADDRESS_IP')}:5432/{os.getenv('NAME_DATABASE')}"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db = SQLAlchemy(app)

app.config.from_pyfile('config.cfg')

jobstore = SQLAlchemyJobStore(url=db_uri)
jobstores = {
        'default': jobstore
    }

scheduler = BackgroundScheduler(jobstores=jobstores,job_defaults={'misfire_grace_time': None})

"""
Liste des tables constitués dans notre base de données 
"""

class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom =  db.Column(db.String(255))
    prenom = db.Column(db.String(255))
    email = db.Column(db.String(255),unique=True)
    password_hash = db.Column(db.String(255)) 
    date_creation = db.Column(db.DateTime, default=datetime.now().strftime('%d %B %Y %H:%M:%S'))

    def is_authenticated(self):
        # Par défaut, tous les utilisateurs sont considérés comme actifs
        return True
    
    def is_active(self):
        return True
    
    def get_id(self):
        return self.id
    
    def set_password(self, password,method):
        self.password_hash = generate_password_hash(password,method)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Participant(db.Model):
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'),primary_key=True)
    nom = db.Column(db.String(255))
    prenom = db.Column(db.String(255))
    adresse = db.Column(db.String(255))
    code_postal = db.Column(db.Integer)
    ville = db.Column(db.String(255))
    pays = db.Column(db.String(255))
    niveau_etude = db.Column(db.String(255))
    statut = db.Column(db.String(255))
    centre_interet = db.Column(db.String(255))
    choix_categorie = db.Column(db.String(255))
    date_creation = db.Column(db.DateTime, default=datetime.now().strftime('%d %B %Y %H:%M:%S'))


class ReponseParticipant(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('participant.participant_id'),unique=False)
    correct_answers = db.Column(db.Integer)
    incorrect_answers = db.Column(db.Integer)
    success_percentage = db.Column(db.Float)
    categorie = db.Column(db.String(255))
    selected_questions= db.Column(JSON)
    options = db.Column(JSON)
    answers = db.Column(JSON)
    correct_responses_dict = db.Column(JSON)
    nb_essais = db.Column(db.Integer)
    date_creation = db.Column(db.DateTime, default=datetime.now().strftime('%d %B %Y %H:%M:%S'))

class Contact(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('participant.participant_id'),unique=False)
    nom =  db.Column(db.String(100))
    email = db.Column(db.String(100))
    tel = db.Column(db.String(100))
    message = db.Column(db.String(1000))
    date_creation = db.Column(db.DateTime, default=datetime.now().strftime('%d %B %Y %H:%M:%S'))

class StripeCustomer(db.Model):
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'),primary_key=True)
    name_product = db.Column(db.String(100))
    email = db.Column(db.String(100))
    id_customer = db.Column(db.String(255))
    id_subscription = db.Column(db.String(255))
    date_creation = db.Column(db.DateTime, default=datetime.now().strftime('%d %B %Y %H:%M:%S'))

class Parrainage(db.Model): 
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'),primary_key=True)
    email = db.Column(db.String(100))
    parrain_email = db.Column(db.String(255))  
    coupon_parrain = db.Column(db.String(255))  
    date_creation = db.Column(db.DateTime, default=datetime.now().strftime('%d %B %Y %H:%M:%S'))
    