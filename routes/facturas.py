from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.factura import Factura, db
from utils.generadores import generar_facturae, generar_pdf, enviar_factura
import uuid
from datetime import datetime

bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@bp.route('/generar', methods=['GET', 'POST'])
def generar():
    if request.method == 'POST':
        numero = f"F{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:4].upper()}"
        base = float(request.form['base'])
        iva = base * 0.21
        total = base + iva

        factura = Factura(
            numero=numero,
            cliente_nombre=request.form['nombre'],
            cliente_nif=request.form['nif'],
            cliente_email=request.form['email'],
            cliente_telefono=request.form['telefono'],
            base_imponible=base,
            iva=iva,
            total=total,
            estado='generada',
            empresa=request.form.get('empresa', 'Anónima')
        )
        db.session.add(factura)
        db.session.commit()

        # Generar archivos (simulado si no existe utils)
        factura.xml_path = f"factura_{numero}.xml"
        factura.pdf_path = f"factura_{numero}.pdf"
        db.session.commit()

        flash(f'¡Factura {numero} generada!')
        return redirect(url_for('facturas.historial'))

    return render_template('facturas/generar.html')

@bp.route('/historial')
def historial():
    facturas = Factura.query.all()
    return render_template('facturas/historial.html', facturas=facturas)
