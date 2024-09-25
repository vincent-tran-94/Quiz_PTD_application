from datetime import datetime
from models import *
from config import *
from app import *

#Fonction pour la création des abonnements stockés sur une base de données
def create_stripe_customer(new_product_customer,email_customer,id_customer,id_subscription):
    
    user = User.query.filter_by(email=email_customer).first() #Si il est inscrit dans l'application 
    if user:
        existing_response = StripeCustomer.query.filter_by(email=email_customer).first()
        if not existing_response: 
            new_entry = StripeCustomer(
                participant_id=user.id,  
                name_product=new_product_customer,
                email=email_customer,
                id_customer = id_customer,
                id_subscription=id_subscription
            )
            db.session.add(new_entry)
            db.session.commit()
    else:
        return None 
    

def update_participant_essais(new_product_customer=None, email=None):
    with app.app_context():
        # Rechercher le client Stripe avec l'email donné
        customer = StripeCustomer.query.filter_by(email=email).first()
        if customer:
            # Vérifier si le client a un abonnement Bronze
            if customer.name_product == new_product_customer:
                # Rechercher toutes les réponses du participant correspondant dans ReponseParticipant
                participant_responses = NbEssaisParticipant.query.filter_by(participant_id=customer.participant_id).all()
                for participant_response in participant_responses:
                    # Vérifier si la réponse du participant existe
                    if participant_response is not None:
                        participant_response.nb_essais += 3
                        # Mettre à jour la date de création pour refléter la mise à jour
                        participant_response.date_creation = datetime.now().strftime('%d %B %Y %H:%M:%S')

                        #Sauvegarder sur un fichier log à répertoire nommé log_essais
                        log_data = f"Client à jour: {customer.email} - {datetime.now().strftime('%d %B %Y %H:%M:%S')} - Nombre d'essais: {participant_response.nb_essais} - Catégorie: {participant_response.categorie}  \n"
                        log_directory = "log_essais"
                        log_filename = os.path.join(log_directory,f"log_essais.txt")
                        with open(log_filename, "a",encoding="utf-8-sig") as file:
                            file.write(log_data)
                        print(f"Add data log_data {datetime.now().strftime('%d %B %Y %H:%M:%S')}")

                # Commit des changements à la base de données une fois pour toutes les réponses traitées
                db.session.commit()






