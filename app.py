from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__, template_folder='template')

# Route pour afficher le formulaire
@app.route('/')
def index():
    return render_template('formulaire.html')

# Route pour traiter les données du formulaire
@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        niveau_etude = request.form['niveau_etude']
        centre_interet = request.form['centre_interet']
        choix_categorie = request.form['choix_categorie']

        # Vérification si tous les champs sont remplis
        if not (nom and prenom and email and niveau_etude and centre_interet and choix_categorie):
            return render_template('formulaire.html', message="Veuillez remplir tous les champs.")

        # Ajout des données à la base de données
        conn = sqlite3.connect('databases/participants.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                prenom TEXT,
                email TEXT,
                niveau_etude TEXT,
                centre_interet TEXT,
                choix_categorie TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO utilisateurs (nom, prenom, email, niveau_etude, centre_interet, choix_categorie)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nom, prenom, email, niveau_etude, centre_interet, choix_categorie))
        conn.commit()
        conn.close()

        return redirect(url_for('bienvenue'))

    return render_template('formulaire.html', message=None)

# Route pour afficher la page de bienvenue
@app.route('/bienvenue')
def bienvenue():
    return render_template('bienvenue.html')

if __name__ == '__main__':
    app.run(debug=True)
