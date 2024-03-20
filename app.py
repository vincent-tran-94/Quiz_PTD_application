from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participants.db'
db = SQLAlchemy(app)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(100))
    niveau_etude = db.Column(db.String(100))
    centre_interet = db.Column(db.String(100))
    choix_categorie = db.Column(db.String(100))

@app.route('/', methods=['GET', 'POST'])
def formulaire():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        niveau_etude = request.form['niveau_etude']
        centre_interet = request.form['centre_interet']
        choix_categorie = request.form['choix_categorie']

        if not (nom and prenom and email and niveau_etude and centre_interet and choix_categorie):
            return render_template('formulaire.html', message="Veuillez remplir tous les champs.")

        participant = Participant(nom=nom, prenom=prenom, email=email, niveau_etude=niveau_etude,
                             centre_interet=centre_interet, choix_categorie=choix_categorie)
        db.session.add(participant)
        db.session.commit()

        return redirect(url_for('bienvenue'))

    return render_template('formulaire.html', message=None)

@app.route('/bienvenue')
def bienvenue():
    return "Bienvenue à la deuxième page !"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
