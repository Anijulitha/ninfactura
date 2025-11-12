from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from ninfactura import db
from ninfactura.models import User

# ✅ CORREGIR ESTA LÍNEA - son dos guiones bajos
bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    return render_template('auth/login.html')

@bp.route('/register')
def register():
    return render_template('auth/register.html')