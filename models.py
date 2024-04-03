from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, extract, distinct
from datetime import datetime, timedelta

id_database = "vincenttran"
password_database = "associationptd"
adresse_ip = "localhost"
name_database = "participants"

app = Flask(__name__,template_folder='template')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participants.db' 
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{id_database}:{password_database}@{adresse_ip}/{name_database}'
db = SQLAlchemy(app)

"""
Liste des tables constitués dans notre base de données 
"""

class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom =  db.Column(db.String(255))
    prenom = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255)) 
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

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
    niveau_etude = db.Column(db.String(255))
    statut = db.Column(db.String(255))
    centre_interet = db.Column(db.String(255))
    choix_categorie = db.Column(db.String(255))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)


class ReponseParticipant(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('participant.participant_id'),unique=False)
    correct_answers = db.Column(db.Integer)
    incorrect_answers = db.Column(db.Integer)
    success_percentage = db.Column(db.Float)
    categorie = db.Column(db.String(255))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    
class Contact(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('participant.participant_id'),unique=False)
    nom =  db.Column(db.String(100))
    email = db.Column(db.String(100))
    tel = db.Column(db.String(100))
    message = db.Column(db.String(1000))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)


def get_participant_name(participant_id):
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if participant:
        return f"{participant.nom} {participant.prenom}"
    else:
        return "Participant introuvable"

def get_success_percentage_by_category(participant_id):
    categories = ['droit', 'humanitaire', 'culturel', 'sociologie']
    success_percentages = {}
    for category in categories:
        participant_results = ReponseParticipant.query.filter_by(participant_id=participant_id, categorie=category).first()
        if participant_results:
            success_percentages[category] = participant_results.success_percentage
        else:
            success_percentages[category] = 0.0
    return success_percentages

def get_month_year(participant_id):
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if participant:
        month = participant.date_creation.strftime('%B')
        year = participant.date_creation.year
        return month, year
    else:
        return None, None

def get_top_10_participants():
    top_participants = db.session.query(ReponseParticipant.participant_id,
                                        extract('year', ReponseParticipant.date_creation).label('response_year'),
                                        extract('month', ReponseParticipant.date_creation).label('response_month'),
                                        func.avg(ReponseParticipant.success_percentage).label('total_success_percentage')) \
                                 .group_by(ReponseParticipant.participant_id, 
                                           extract('year', ReponseParticipant.date_creation),
                                           extract('month', ReponseParticipant.date_creation)) \
                                 .having(func.count(distinct(ReponseParticipant.categorie)) == 4) \
                                 .order_by(func.avg(ReponseParticipant.success_percentage).desc()) \
                                 .limit(50) \
                                 .all()
    
    top_participants_info = []
    for participant_id, response_year, response_month, total_success_percentage in top_participants:
        participant_name = get_participant_name(participant_id)
        top_participants_info.append((participant_name, response_year, response_month, total_success_percentage))
    
    return top_participants_info


# Fonction pour obtenir la date actuelle
def get_current_date():
    return datetime.utcnow()

# Fonction pour vérifier si une mois s'est écoulée depuis la dernière réponse
def is_two_week_passed(last_response_date):
    return get_current_date() - last_response_date >= timedelta(weeks=2)