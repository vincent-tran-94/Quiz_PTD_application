from forms import *
import stripe
from flask import render_template, url_for, request, abort
from flask_login import login_required
from datetime import datetime, timedelta
import schedule
import time


public_key_strip = 'pk_test_51P3EsLG1dB5sn7JtabG0HewwbGUIktc5ViqOip7CUtHb14aZMWLvEQzfrp1Flkt9aXsH89LznAJjQC9yc7iLPawg00jQUmVWQW'
secret_key_strip = 'sk_test_51P3EsLG1dB5sn7JtBsuQQqpq0GKlCGqsdDjqyfgBfw0RoJtszhcToMDUTAClc6Ec0kytShyM6rjWSJzP6hg3Cu7h00ikI1xuSw'

app.config['STRIPE_PUBLIC_KEY'] = public_key_strip
app.config['STRIPE_SECRET_KEY'] = secret_key_strip
stripe.api_key = app.config['STRIPE_SECRET_KEY']

"""
COMMAND pour récupérer le nom du produit acheté par le client marche seulement en local
stripe listen --forward-to http://127.0.0.1:5000/stripe_webhook
and enter your secret_endpoint_webhook
"""
secret_endpoint_webhook = 'whsec_3d75fb000c8f8f97b0b15706ab7792f17cf22882ab2de498c165bc2a86cba976'

@app.route('/souscription')
@login_required
def souscription():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P3FAhG1dB5sn7JthBzdmAA6',
            'quantity': 1,
        }],
        mode='subscription',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('souscription', _external=True),
    )
    
    return render_template(
        'souscription.html', 
        checkout_session_id=session['id'], 
        checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
    )

@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1P3FAhG1dB5sn7JthBzdmAA6',
            'quantity': 1,
        }],
        mode='subscription',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('souscription', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

@app.route('/thanks')
@login_required
def thanks():
    return render_template('thanks.html')

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    if request.content_length > 1024 * 1024:
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = secret_endpoint_webhook 
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('Error Payload')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        print('Error Signature')
        # Invalid signature
        return {}, 400
    
     # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        #print(session)
        product_description = stripe.checkout.Session.list_line_items(session['id'], limit=1)['data'][0]['description']
        #print(product_description)
        email_customer = stripe.checkout.Session.list(limit=3)["data"][0]["customer_details"]["email"]
        #print(email_customer)
        create_stripe_customer(product_description,email_customer)
        process_task(product_description,email_customer)

    return {}

#Fonction pour la création des abonnements stockés sur une base de données
def create_stripe_customer(new_product_customer,email_customer):
    product_mapping = {
        "Bronze": 3,
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


def update_participant_responses(new_product_customer,email):
     # Rechercher le client Stripe avec l'email donné
    with app.app_context():
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
                        if datetime.utcnow() - last_update > timedelta(days=30):  
                            # Mettre à jour le nombre d'essais
                            participant_response.nb_essais += 3
                            # Mettre à jour la date de création pour refléter la mise à jour
                            participant_response.date_creation = datetime.utcnow()
                # Commit des changements à la base de données une fois pour toutes les réponses traitées
                db.session.commit()

def process_task(product_description,email):
    # Planifier la tâche pour s'exécuter chaque mois
    schedule.every(4).weeks.do(lambda: update_participant_responses(product_description, email))
    # Boucle pour exécuter la planification de la tâche en continu
    while True:
        schedule.run_pending()
        time.sleep(1)
