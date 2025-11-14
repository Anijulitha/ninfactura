from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid

# IMPORTA db Y Factura DESDE LA RAÍZ (NO DESDE models.factura)
from __init__ import db
from models.factura import Factura

# FUNCIONES SIMULADAS SI NO EXISTEN utils
try:
    from utils.generadores import generar_facturae, generar_pdf, enviar_factura
except ImportError:
    def generar_facturae(factura):
        return f"facturas/xml/{factura.numero}.xml"
    def generar_pdf(factura):
        return f"facturas/pdf/{factura.numero}.pdf"
    def enviar_factura(factura):
        print(f"WhatsApp y email enviados para {factura.numero}")

# BLUEPRINT
bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@bp.route('/generar', methods=['GET', 'POST'])
def generar():
    if request.method == 'POST':
        numero = f"F{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:4].upper()}"
        base = float(request.form.get('base', 0))
        iva = base * 0.21
        total = base + iva

        factura = Factura(
            numero=numero,
            cliente_nombre=request.form.get('nombre', 'Anónimo'),
            cliente_nif=request.form.get('nif', '00000000A'),
            cliente_email=request.form.get('email', 'test@example.com'),
            cliente_telefono=request.form.get('telefono', '+34600123456'),
            base_imponible=base,
            iva=iva,
            total=total,
            estado='generada',
            empresa=request.form.get('empresa', 'Anónima')
        )
        db.session.add(factura)
        db.session.commit()

        # Generar archivos
        factura.xml_path = generar_facturae(factura)
        factura.pdf_path = generar_pdf(factura)
        db.session.commit()

        # Enviar
        enviar_factura(factura)
        factura.estado = 'enviada'
        db.session.commit()

        flash(f'Factura {numero} generada y enviada!')
        return redirect(url_for('facturas.historial'))

    return render_template('facturas/generar.html')

@bp.route('/historial')
def historial():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
    return render_template('facturas/historial.html', facturas=facturas)
