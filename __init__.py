import os
import sys

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
     app = Flask(_name_, 
            template_folder='factura_templates',  # ¡Quita el '../'!
            static_folder='static')

    # === CONFIG ===
    try:
        from config import Config
        app.config.from_object(Config)
    except ImportError:
        class Config:
            SECRET_KEY = 'dev-key-segura-aqui'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///ninfatura.db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            UPLOAD_FOLDER = 'uploads'
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        app.config.from_object(Config)

    # === INIT EXTENSIONS ===
    db.init_app(app)
    login_manager.init_app(app)

    # === BLUEPRINTS ===
    # Auth
    try:
        from routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError:
        print("⚠️ No se pudo importar routes.auth")

    # Facturas (¡CON PREFIX!)
    try:
        from routes.facturas import bp as facturas_bp
        app.register_blueprint(facturas_bp, url_prefix='/facturas')
    except ImportError as e:
        print(f"⚠️ Error importando facturas: {e}")

    # === RUTA RAÍZ ===
    @app.route('/')
    def home():
        return '<h1>🚀 NINFATURA ONLINE!</h1><p><a href="/facturas/generar">Generar factura</a></p>'

    return app
