from setup import *
import stripe
from flask import render_template, url_for, request, abort
from flask_login import login_required
from mail import send_invoice_email
from process_stripe import create_stripe_customer


app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = app.config['STRIPE_SECRET_KEY']
id_product_bronze =  os.getenv('ID_PRODUCT_BRONZE')
id_product_silver = os.getenv('ID_PRODUCT_SILVER')
id_product_gold = os.getenv('ID_PRODUCT_GOLD')
taxe_rate = os.getenv('ID_TAXE_RATE')
"""
COMMAND pour récupérer le nom du produit acheté par le client marche seulement en local
stripe listen --forward-to http://127.0.0.1:5000/stripe_webhook
and enter your secret_endpoint_webhook
"""
secret_endpoint_webhook = os.getenv('STRIPE_SECRET_ENDPOINT')

@app.route('/souscription')
@login_required
def souscription():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': id_product_bronze ,
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
    
    return render_template(
        'sidebar/souscription.html', 
        checkout_session_id=session['id'], 
        checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
    )

@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': id_product_bronze ,
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
        #print(product_description)
        email_customer = stripe.checkout.Session.list(limit=3)["data"][0]["customer_details"]["email"]
        #print(email_customer)
        create_stripe_customer(product_description,email_customer)

    if event['type'] == 'invoice.created':
        invoice_id = event['data']['object']['id']
        #print(invoice_id)
        send_invoice_email(invoice_id)
       
    return '', 200

