from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# CREAR APP (TEMPLATE FOLDER CORRECTO)
app = Flask(__name__, 
            template_folder='factura_templates',  # ¡SIN '../'!
            static_folder='static')

# CONFIG
app.config['SECRET_KEY'] = 'clave-secreta-temporal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ninfatura.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

# MODELO
class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(200), nullable=False)
    referencia_hacienda = db.Column(db.String(100))
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='subido')
    empresa = db.Column(db.String(100), default='Anónima')

# EXTENSIONES
ALLOWED_EXTENSIONS = {'pdf', 'xml', 'json', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === RUTAS ===

@app.route('/')
def index():
    facturas = Factura.query.order_by(Factura.fecha_subida.desc()).limit(5).all()
    return render_template('upload.html', facturas=facturas)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect('/')
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect('/')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        referencia = 'HZ-' + datetime.now().strftime('%Y%m%d%H%M%S')
        nueva_factura = Factura(
            nombre_archivo=filename,
            referencia_hacienda=referencia,
            empresa=request.form.get('empresa', 'Anónima')
        )
        db.session.add(nueva_factura)
        db.session.commit()
        
        flash(f'Factura subida: {referencia}')
        return redirect('/historial')
    
    flash('Archivo no permitido')
    return redirect('/')

# === REGISTRA BLUEPRINTS ===
try:
    from routes.facturas import bp as facturas_bp
    app.register_blueprint(facturas_bp, url_prefix='/facturas')
except ImportError as e:
    print(f"⚠️ No se pudo importar facturas: {e}")

# === INICIAR DB ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
