from models import *
import stripe
from flask import render_template, url_for, request, abort
from flask_login import login_required
from mail import send_invoice_email
from process_stripe import create_stripe_customer, update_participant_essais

app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = app.config['STRIPE_SECRET_KEY']

id_product_bronze =  os.getenv('ID_PRODUCT_BRONZE')
id_product_silver = os.getenv('ID_PRODUCT_SILVER')
id_product_gold = os.getenv('ID_PRODUCT_GOLD')
taxe_rate = os.getenv('ID_TAXE_RATE')
secret_endpoint_webhook = os.getenv('STRIPE_SECRET_ENDPOINT')
coupon_id = os.getenv('ID_COUPON')

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
            'price': id_product_bronze,
            'quantity': 1,
        }],
        subscription_data={
            'default_tax_rates': [taxe_rate],
        },
        mode='subscription',
        allow_promotion_codes=True,
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('souscription', _external=True),
    )
    return session


@app.route('/souscription')
@login_required
def souscription():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': id_product_bronze,
            'quantity': 1,
        }],
        subscription_data={
            'default_tax_rates': [taxe_rate],
        },
        mode='subscription',
        allow_promotion_codes=True,
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('souscription', _external=True),
    )
    return render_template('sidebar/souscription.html', checkout_session_id=session['id'], checkout_public_key=app.config['STRIPE_PUBLIC_KEY'])
        
    
@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': id_product_bronze,
            'quantity': 1,
        }],
        subscription_data={
            'default_tax_rates': [taxe_rate],
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
        product_description = stripe.checkout.Session.list_line_items(session, limit=1)['data'][0]['description']
        #print("product_description",product_description)
        email_customer = stripe.checkout.Session.list(limit=3)["data"][0]["customer_details"]["email"]
        id_customer = stripe.checkout.Session.list(limit=3)["data"][0]["customer"]
        id_subscription= stripe.checkout.Session.list(limit=3)["data"][0]["subscription"]
        print("Successful payment and creation database StripeCustomer")
        create_stripe_customer(product_description,email_customer,id_customer,id_subscription)
        #scheduler.add_job(update_participant_essais, 'interval', month=1,args=[product_description, email_customer])

    if event['type'] == 'invoice.created':
        invoice_id = event['data']['object']['id']
        print(f"Creation invoice {invoice_id}.")
        send_invoice_email(invoice_id)
       
    return '', 200


