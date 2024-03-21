from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,template_folder='template')
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

class ReponseParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(36), db.ForeignKey('participant.id'), nullable=False)
    correct_answers = db.Column(db.Integer)
    incorrect_answers = db.Column(db.Integer)
    success_percentage = db.Column(db.Float)
    reponses = db.relationship('Participant', backref='reponse_participant', lazy=True)