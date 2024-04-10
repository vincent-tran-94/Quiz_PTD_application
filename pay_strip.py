from forms import *
import stripe
from flask import render_template, url_for, request, abort
from flask_login import login_required

public_key_strip = 'pk_test_51P3EsLG1dB5sn7JtabG0HewwbGUIktc5ViqOip7CUtHb14aZMWLvEQzfrp1Flkt9aXsH89LznAJjQC9yc7iLPawg00jQUmVWQW'
secret_key_strip = 'sk_test_51P3EsLG1dB5sn7JtBsuQQqpq0GKlCGqsdDjqyfgBfw0RoJtszhcToMDUTAClc6Ec0kytShyM6rjWSJzP6hg3Cu7h00ikI1xuSw'

app.config['STRIPE_PUBLIC_KEY'] = public_key_strip
app.config['STRIPE_SECRET_KEY'] = secret_key_strip
stripe.api_key = app.config['STRIPE_SECRET_KEY']

"""
COMMAND pour récupérer le nom du produit acheté par le client marche seulement en local
stripe listen --forward-connect-to http://127.0.0.1:5000/stripe_webhook
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
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])
    elif event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        print('Invoice paid:', invoice)
        # Handle the invoice being paid
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        print('Invoice payment failed:', invoice)
        # Handle the invoice payment failure
    return {}
