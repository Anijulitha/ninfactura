from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import stripe

bp = Blueprint('pagos', __name__, url_prefix='/pagos')

@bp.route('/crear-sesion', methods=['POST'])
@login_required
def crear_sesion():
    try:
        checkout_session = stripe.checkout.sessions.create(
            payment_method_types=['card'],
            line_items=[{
                'price': current_app.config['STRIPE_PRICE_ID'],
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=current_user.email,
            success_url=url_for('pagos.exito', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('facturas.historial', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash('Error al procesar pago')
        return redirect(url_for('facturas.historial'))

@bp.route('/exito')
@login_required
def exito():
    current_user.plan = 'pro'
    db.session.commit()
    flash('¡Suscripción PRO activada! 79€/mes')
    return redirect(url_for('facturas.historial'))
