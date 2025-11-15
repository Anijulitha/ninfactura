import os
import sys

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, redirect, url_for
from flask_login import current_user
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

    # === CONFIGURACIÓN ===
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

    # === STRIPE CONFIG ===
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

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('facturas.historial'))
        return '''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ninfatura - Facturación Fácil</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
            <style> body { font-family: 'Inter', sans-serif; } </style>
        </head>
        <body class="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 min-h-screen flex items-center justify-center p-6">
            <div class="max-w-4xl mx-auto text-center">
                <div class="mb-10">
                    <h1 class="text-6xl md:text-7xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-pulse">
                        🚀 NINFATURA
                    </h1>
                    <p class="text-2xl md:text-3xl text-gray-700 mt-4">Facturación fácil, rápida y profesional</p>
                </div>

                <div class="grid md:grid-cols-3 gap-6 mb-12">
                    <div class="bg-white p-6 rounded-2xl shadow-xl hover:shadow-2xl transition-all">
                        <div class="text-4xl mb-3">📄</div>
                        <h3 class="text-xl font-bold text-indigo-600">Genera facturas</h3>
                        <p class="text-gray-600">En 30 segundos</p>
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-xl hover:shadow-2xl transition-all">
                        <div class="text-4xl mb-3">📱</div>
                        <h3 class="text-xl font-bold text-purple-600">Envía por WhatsApp</h3>
                        <p class="text-gray-600">PDF + XML listo</p>
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-xl hover:shadow-2xl transition-all">
                        <div class="text-4xl mb-3">💎</div>
                        <h3 class="text-xl font-bold text-pink-600">Plan PRO</h3>
                        <p class="text-gray-600">79€/mes ilimitado</p>
                    </div>
                </div>

                <div class="space-x-4">
                    <a href="/auth/register" class="inline-block bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all">
                        🚀 Empezar GRATIS
                    </a>
                    <a href="/auth/login" class="inline-block bg-white text-indigo-600 border-2 border-indigo-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-indigo-50 transform hover:scale-105 transition-all">
                        🔑 Ya tengo cuenta
                    </a>
                </div>

                <p class="text-sm text-gray-500 mt-10">
                    <strong>0€ para siempre</strong> en plan FREE • Facturas limitadas
                </p>
            </div>
        </body>
        </html>
        '''

    return app
