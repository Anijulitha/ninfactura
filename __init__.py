import os
import sys

# Añadir el directorio actual al path (opcional, quítalo si da problemas)
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# === EXTENSIONES GLOBALES ===
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirige a login si no estás logueado

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

    # === INICIALIZAR EXTENSIONES ===
    db.init_app(app)
    login_manager.init_app(app)

    # === USER LOADER (OBLIGATORIO PARA FLASK-LOGIN) ===
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
