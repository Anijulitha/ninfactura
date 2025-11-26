import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# === EXTENSIONES GLOBALES ===
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(*args, **kwargs):
    app = Flask(__name__, 
                template_folder='factura_templates',
                static_folder='static')

    # === CONFIGURACIÓN ===
    try:
        from config import Config
        app.config.from_object(Config)
    except ImportError:
        class Config:
            SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-super-segura-cambia-esto-en-produccion'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///ninfactura.db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
        app.config.from_object(Config)

    # === STRIPE ===
    import stripe
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')

    # === INICIALIZAR EXTENSIONES ===
    db.init_app(app)
    login_manager.init_app(app)

    # === USER LOADER ===
    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # === REGISTRAR BLUEPRINTS ===
    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from routes.facturas import bp as facturas_bp
    app.register_blueprint(facturas_bp, url_prefix='/facturas')

    from routes.pagos import bp as pagos_bp
    app.register_blueprint(pagos_bp, url_prefix='/pagos')

    from routes.webhook import bp as webhook_bp
    app.register_blueprint(webhook_bp)

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect('/facturas')
        return '''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ninfatura - Facturación Fácil</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 min-h-screen flex items-center justify-center p-6">
            <div class="text-center">
                <h1 class="text-7xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                    NINFACTURA
                </h1>
                <p class="text-3xl text-gray-700 mt-4">Facturación fácil y rápida</p>
                <div class="mt-10 space temperaturas-x-4">
                    <a href="/auth/register" class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-xl font-bold text-lg">
                        Empezar GRATIS
                    </a>
                    <a href="/auth/login" class="bg-white text-indigo-600 border-2 border-indigo-600 px-8 py-4 rounded-xl font-bold text-lg ml-4">
                        Ya tengo cuenta
                    </a>
                </div>
            </div>
        </body>
        </html>
        '''

    return app

app = create_app()
