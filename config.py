import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'tu-clave-secreta-muy-segura-aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'ninfatura.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, '../uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024