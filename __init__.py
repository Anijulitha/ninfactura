import os
import sys

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Importar Config directamente
try:
    from config import Config
except ImportError:
    # Configuración por defecto si no encuentra config.py
    class Config:
        SECRET_KEY = 'dev-key-segura-aqui'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///ninfatura.db'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        UPLOAD_FOLDER = 'uploads'
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, 
                template_folder='../factura_templates',
                static_folder='../static')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # === BLUEPRINTS ===
    # Auth (si existe)
    try:
        from routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError:
        print("⚠️  No se pudo importar routes.auth - continuando sin autenticación")

    # Facturas (NUEVO)
    try:
        from routes.facturas import bp as facturas_bp
        app.register_blueprint(facturas_bp)
    except ImportError as e:
        print(f"⚠️  No se pudo importar routes.facturas: {e}")

    return app