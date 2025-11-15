import os
import sys

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# === EXTENSIONES GLOBALES ===
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, 
                template_folder='factura_templates',
                static_folder='static')

    # === CONFIGURACIÓN (PRIMERO!) ===
    try:
        from config import Config
        app.config.from_object(Config)
    except ImportError:
        class Config:
            SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-super-segura-cambia-esto-en-produccion'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///ninfatura.db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            UPLOAD_FOLDER = 'uploads'
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        app.config.from_object(Config)

    # === STRIPE CONFIG (DESPUÉS DE CONFIG!) ===
    import stripe
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    app.config['STRIPE_PUBLIC_KEY'] = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    app.config['STRIPE_PRICE_ID'] = os.environ.get('STRIPE_PRICE_ID')
    app.config['STRIPE_WEBHOOK_SECRET'] = os.environ.get('STRIPE_WEBHOOK_SECRET')

    # === INICIALIZAR EXTENSIONES ===
    db.init_app(app)
    login_manager.init_app(app)

    # === USER LOADER ===
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # === REGISTRAR BLUEPRINTS ===
    try:
        from routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError as e:
        print(f"⚠️ No se pudo importar auth: {e}")

    try:
        from routes.facturas import bp as facturas_bp
        app.register_blueprint(facturas_bp, url_prefix='/facturas')
    except ImportError as e:
        print(f"⚠️ Error importando facturas: {e}")

    try:
        from routes.pagos import bp as pagos_bp
        app.register_blueprint(pagos_bp, url_prefix='/pagos')
    except ImportError as e:
        print(f"⚠️ Error importando pagos: {e}")

    try:
        from routes.webhook import bp as webhook_bp
        app.register_blueprint(webhook_bp)
    except ImportError as e:
        print(f"⚠️ Error importando webhook: {e}")

    # === RUTA PRINCIPAL ===
    @app.route('/')
    def home():
        return '''
        <h1>🚀 NINFATURA ONLINE!</h1>
        <p>
            <a href="/facturas/generar">Generar factura</a> | 
            <a href="/facturas/historial">Historial</a> | 
            <a href="/auth/login">Login</a> | 
            <a href="/auth/register">Registrarse</a>
        </p>
        '''

    return app
