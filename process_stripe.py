from datetime import datetime, timedelta
import schedule
from setup import *
import time


#Fonction pour la création des abonnements stockés sur une base de données
def create_stripe_customer(new_product_customer,email_customer):
    product_mapping = {
        "Bronze": 4,
        "Argent": 6,
        "Gold": 10
    }

    user = User.query.filter_by(email=email_customer).first()
    if user:
        existing_response = StripeCustomer.query.filter_by(email=email_customer).first()
        if not existing_response: 
            new_entry = StripeCustomer(
                participant_id=user.id,  
                name_product=new_product_customer,
                email=email_customer,
                price_euros = product_mapping[new_product_customer]
            )
            db.session.add(new_entry)
        else:
            existing_response.participant_id = user.id  
            existing_response.name_product = new_product_customer
            existing_response.email = email_customer
            existing_response.price_euros = product_mapping[new_product_customer]
        db.session.commit()
    else:
        return None 


def update_participant_essais(new_product_customer,email):
    with app.app_context():
        # Rechercher le client Stripe avec l'email donné
        customer = StripeCustomer.query.filter_by(email=email).first()
        if customer:
            # Vérifier si le client a un abonnement Bronze
            if customer.name_product == new_product_customer:
                # Rechercher toutes les réponses du participant correspondant dans ReponseParticipant
                participant_responses = ReponseParticipant.query.filter_by(participant_id=customer.participant_id).all()
                for participant_response in participant_responses:
                    # Vérifier si la réponse du participant existe
                    if participant_response is not None:
                        last_update = participant_response.date_creation
                        # Vérifier si la dernière mise à jour a eu lieu il y a plus d'un mois
                        if datetime.utcnow() - last_update > timedelta(seconds=1):  
                            # Mettre à jour le nombre d'essais
                            participant_response.nb_essais += 3
                            # Mettre à jour la date de création pour refléter la mise à jour
                            participant_response.date_creation = datetime.utcnow()
                # Commit des changements à la base de données une fois pour toutes les réponses traitées
                db.session.commit()


# Planification de la tâche
def schedule_task(new_product_customer, email):
    # Planifier la tâche pour s'exécuter tous les 30 jours
    schedule.every(30).seconds.do(lambda: update_participant_essais(new_product_customer, email))

# Démarrer le planificateur dans un thread séparé
def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Attendre une seconde avant de vérifier à nouveau les tâches planifiées



# def process_task(product_description,email):
#     with app.app_context():
#         # Planifier la tâche pour s'exécuter chaque mois
#         schedule.every(4).seconds.do(lambda: update_participant_essais(product_description, email))
#         # Boucle pour exécuter la planification de la tâche en continu
#         while True:
#             schedule.run_pending()


# def apply_process_task_to_existing_users():
#     with app.app_context():
#     # Récupérer tous les utilisateurs inscrits dans la base de données
#         existing_users = StripeCustomer.query.all()
#         for user in existing_users:
#             # Vérifier si l'utilisateur existe dans la base de données
#             if user:
#                 # Appeler process_task pour chaque utilisateur avec les informations nécessaires
#                 threading.Thread(target=process_task, args=(user.name_product, user.email)).start()

