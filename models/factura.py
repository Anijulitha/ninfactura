from __init__ import db  # Importa db de la raíz
from datetime import datetime

class Factura(db.Model):
    __tablename__ = 'factura'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cliente_nombre = db.Column(db.String(200))
    cliente_nif = db.Column(db.String(20))
    cliente_email = db.Column(db.String(120))
    cliente_telefono = db.Column(db.String(20))
    base_imponible = db.Column(db.Float, default=0.0)
    iva = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_pago = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='pendiente')
    empresa = db.Column(db.String(100), default='Anónima')
    xml_path = db.Column(db.String(200))
    pdf_path = db.Column(db.String(200))
    referencia_hacienda = db.Column(db.String(100))

    def __repr__(self):
        return f'<Factura {self.numero}>'
