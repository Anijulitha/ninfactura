from flask import Blueprint, request, jsonify
from flask_login import current_user
import stripe
from ninfacturanuevo_app import db
from models.user import User

bp = Blueprint('webhook', __name__)

@bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session['customer_details']['email']
        user = User.query.filter_by(email=email).first()
        if user:
            user.plan = 'pro'
            user.stripe_customer_id = session['customer']
            db.session.commit()

    return jsonify(success=True)
