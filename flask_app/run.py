from routes import *
from dotenv import load_dotenv

# Lancement des variables virtuels
load_dotenv()

if __name__ == '__main__':
    # scheduler.start()
    # scheduler.print_jobs()
    # with app.app_context():
    #     db.create_all()  #Création de la table dans la base de données si il n'existe pas
    app.run(debug=True, host=app.config['HOST'], port=app.config['PORT'])

