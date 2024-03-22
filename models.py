from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__,template_folder='template')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participants.db'
db = SQLAlchemy(app)

class Participant(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(100))
    niveau_etude = db.Column(db.String(100))
    centre_interet = db.Column(db.String(100))
    choix_categorie = db.Column(db.String(100))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class ReponseParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(36), db.ForeignKey('participant.id'), nullable=False)
    correct_answers = db.Column(db.Integer)
    incorrect_answers = db.Column(db.Integer)
    success_percentage = db.Column(db.Float)
    categorie = db.Column(db.String(100))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class EmailID(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100)) 
    user_id = db.Column(db.String(36), db.ForeignKey('participant.id'), nullable=False)

    def is_authenticated(self):
        # Par défaut, tous les utilisateurs sont considérés comme actifs
        return True
    
    def get_id(self):
        return self.id

    def is_active(self):
        return True