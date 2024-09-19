from models import *
from app import *
from config import *
import stripe
from flask import render_template, url_for, request, abort
from mail import send_invoice_email
from process_stripe import create_stripe_customer, update_participant_essais

"""
COMMAND pour récupérer le nom du produit acheté par le client marche seulement en local
stripe listen --forward-to http://127.0.0.1:5000/stripe_webhook
and enter your secret_endpoint_webhook
"""


# Créer un code de réduction
def create_promotion_code(coupon_id):    
    try:
        # Créer le code de réduction
        promotion_code = stripe.PromotionCode.create(
            coupon=coupon_id,  # Utiliser l'ID du coupon créé
            max_redemptions=1  # Limiter à une seule utilisation
        )
        print("Code de réduction créé avec succès:")
        return promotion_code["code"]
    
    except stripe.error.StripeError as e:
        print(str(e))
        return None

# Fonction pour vérifier si le client existe sur Stripe
def verifier_client(email):
    try:
        client = stripe.Customer.list(email=email, limit=1)
        if client:
            return True, client.data[0].id
        else:
            return False, None
    except stripe.error.StripeError as e:
        print("Une erreur s'est produite:", e)
        return False, None

def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': app.config['ID_PRODUCT_BRONZE'], 
            'quantity': 1,
        }],
        subscription_data={
            'default_tax_rates': app.config['TAXE_RATE'],
        },
        mode='subscription',
        allow_promotion_codes=True,
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('souscription', _external=True),
    )
    return session


        
@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': app.config['ID_PRODUCT_BRONZE'],
            'quantity': 1,
        }],
        subscription_data={
            'default_tax_rates': app.config['TAXE_RATE'],
        },
        mode='subscription',
        allow_promotion_codes=True,
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('souscription', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    if request.content_length > 1024 * 1024:
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = app.config['STRIPE_SECRET_ENDPOINT']  
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
        session_checkout = event['data']['object'] 
        product_description = stripe.checkout.Session.list_line_items(session_checkout , limit=1)['data'][0]['description']
        #print("product_description",product_description)
        email_customer = stripe.checkout.Session.list(limit=3)["data"][0]["customer_details"]["email"]
        id_customer = stripe.checkout.Session.list(limit=3)["data"][0]["customer"]
        id_subscription= stripe.checkout.Session.list(limit=3)["data"][0]["subscription"]
        create_stripe_customer(product_description,email_customer,id_customer,id_subscription)
        print("Successful payment and creation database StripeCustomer")
        customer = StripeCustomer.query.filter_by(email=email_customer).first()
        if customer: 
            scheduler.add_job(update_participant_essais,'interval',days=30,args=[product_description, email_customer],id=str(customer.participant_id))
            print(f"Add job in database apscheduler {email_customer}")


    if event['type'] == 'invoice.created':
        invoice_id = event['data']['object']['id']
        send_invoice_email(invoice_id)
        print(f"Creation invoice {invoice_id}.")

       
    return '', 200


