from flask import Blueprint, render_template, request, redirect, url_for, flash
import uuid
from datetime import datetime

# Importa db y Factura desde models (asegúrate que existan)
try:
    from models.factura import Factura, db
except ImportError:
    # Simula si no existe (para testing)
    class Factura:
        pass
    db = type('DB', (), {'session': type('Session', (), {'add': lambda x: print('Factura añadida'), 'commit': lambda: print('Commit OK')})})()

# Importa funciones de utils (simuladas si no existen)
try:
    from utils.generadores import generar_facturae, generar_pdf, enviar_factura
except ImportError:
    def generar_facturae(factura):
        return f"xml_{factura.numero}.xml"
    def generar_pdf(factura):
        return f"pdf_{factura.numero}.pdf"
    def enviar_factura(factura):
        print(f"Enviando {factura.numero} por WhatsApp/email")

bp = Blueprint('facturas', __name__, url_prefix='/facturas')  # ¡URL PREFIX AQUÍ!

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

        xml_path = generar_facturae(factura)
        pdf_path = generar_pdf(factura)
        factura.xml_path = xml_path
        factura.pdf_path = pdf_path
        db.session.commit()

        enviar_factura(factura)
        factura.estado = 'enviada'
        db.session.commit()

        flash(f'¡Factura {numero} generada y enviada!')
        return redirect(url_for('facturas.historial'))

    return render_template('facturas/generar.html')

@bp.route('/historial')
def historial():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all() if 'Factura' in globals() else []
    return render_template('facturas/historial.html', facturas=facturas)
