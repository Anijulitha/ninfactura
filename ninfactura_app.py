from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Crear aplicación Flask
app = Flask(__name__, 
            template_folder='../factura_templates',
            static_folder='../static')

# CONFIGURACIÓN DE BASE DE DATOS
app.config['SECRET_KEY'] = 'clave-secreta-temporal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ninfatura.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Inicializar base de datos
db = SQLAlchemy(app)

# MODELOS DE BASE DE DATOS
class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(200), nullable=False)
    referencia_hacienda = db.Column(db.String(100))
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='subido')
    empresa = db.Column(db.String(100), default='Anónima')

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'pdf', 'xml', 'json', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Mostrar últimas facturas subidas
    facturas = Factura.query.order_by(Factura.fecha_subida.desc()).limit(5).all()
    return render_template('upload.html', facturas=facturas)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo')
            return redirect('/')
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo')
            return redirect('/')
        
        if file and allowed_file(file.filename):
            # Guardar archivo
            filename = secure_filename(file.filename)
            upload_dir = app.config['UPLOAD_FOLDER']
            
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Crear referencia de Hacienda
            referencia = 'HZ-' + datetime.now().strftime('%Y%m%d%H%M%S')
            
            # GUARDAR EN BASE DE DATOS
            nueva_factura = Factura(
                nombre_archivo=filename,
                referencia_hacienda=referencia,
                empresa=request.form.get('empresa', 'Anónima')
            )
            db.session.add(nueva_factura)
            db.session.commit()
            
            # Resultado
            result = {
                'status': 'success',
                'message': 'Factura subida correctamente',
                'hacienda_reference': referencia,
                'file_processed': filename,
                'id_factura': nueva_factura.id
            }
            
            return render_template('results.html', 
                                 filename=filename,
                                 result=result,
                                 timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        else:
            flash('Tipo de archivo no permitido')
            return redirect('/')
            
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect('/')

# NUEVA RUTA: Historial de facturas
@app.route('/historial')
def historial():
    facturas = Factura.query.order_by(Factura.fecha_subida.desc()).all()
    return render_template('historial.html', facturas=facturas)

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'service': 'Ninfatura'}

@app.route('/dashboard')
def dashboard():
    # Estadísticas
    total_facturas = Factura.query.count()
    facturas_hoy = Factura.query.filter(
        Factura.fecha_subida >= datetime.now().date()
    ).count()
    
    # Últimas facturas
    ultimas_facturas = Factura.query.order_by(Factura.fecha_subida.desc()).limit(10).all()
    
    # Empresas más activas
    from sqlalchemy import func
    empresas_activas = db.session.query(
        Factura.empresa, 
        func.count(Factura.id).label('total')
    ).group_by(Factura.empresa).order_by(func.count(Factura.id).desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_facturas=total_facturas,
                         facturas_hoy=facturas_hoy,
                         ultimas_facturas=ultimas_facturas,
                         empresas_activas=empresas_activas)

# BÚSQUEDA DE FACTURAS
@app.route('/buscar')
def buscar_facturas():
    query = request.args.get('q', '')
    empresa = request.args.get('empresa', '')
    
    facturas = Factura.query
    
    if query:
        facturas = facturas.filter(Factura.nombre_archivo.contains(query))
    
    if empresa:
        facturas = facturas.filter(Factura.empresa == empresa)
    
    facturas = facturas.order_by(Factura.fecha_subida.desc()).all()
    
    # Lista de empresas para el filtro
    empresas = db.session.query(Factura.empresa).distinct().all()
    empresas = [emp[0] for emp in empresas if emp[0]]
    
    return render_template('buscar.html', 
                         facturas=facturas, 
                         query=query, 
                         empresa=empresa,
                         empresas=empresas)

# ELIMINAR FACTURA (solo para admin)
@app.route('/eliminar/<int:factura_id>')
def eliminar_factura(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    db.session.delete(factura)
    db.session.commit()
    flash('Factura eliminada correctamente')
    return redirect('/dashboard')

# INICIAR SERVIDOR CON BASE DE DATOS
if __name__ == '__main__':
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        print("✅ Base de datos inicializada")
    
    print("🚀 NINFATURA CON BASE DE DATOS - Servidor iniciado!")
    print("📍 Accede en: http://localhost:5000")
    print("📊 Historial: http://localhost:5000/historial")
    app.run(host='0.0.0.0', port=5001, debug=False)