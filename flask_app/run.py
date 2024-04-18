from models import *
from routes import *

#Lancement de l'application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  #Création de la table dans la base de données si il n'existe pas
    app.run(debug=True,host=host,port=port)

