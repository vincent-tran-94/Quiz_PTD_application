from flask import redirect, render_template
from setup import *
from flask_login import login_required, current_user

# Fonction utilitaire pour vérifier le rôle de l'utilisateur
def check_role(user_id, role):
    stripe_customer = StripeCustomer.query.filter_by(participant_id=user_id).first()
    if stripe_customer and stripe_customer.name_product == role:
        return True
    return False

# Route protégée par le rôle "bronze"
@app.route('/bronze_route_dashboard')
@login_required
def bronze_route_dashboard():
    if check_role(current_user.get_id(), 'Bronze'):
        return redirect('dashboard')
    else:
        return render_template("no_authorization.html",message="Il faut opter pour un abonnement minimum.")

@app.route('/bronze_route_resultats')
@login_required
def bronze_route_resultats():
    if check_role(current_user.get_id(), 'Bronze'):
        return redirect('resultats')
    else:
        return render_template("no_authorization.html",message="Il faut opter pour un abonnement minimum.")



