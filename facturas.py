from flask import Blueprint, render_template, request, flash, redirect, url_for
from models.factura import Factura, db
from utils.generadores import generar_facturae, generar_pdf, enviar_factura
import uuid
from datetime import datetime

bp = Blueprint('facturas', _name_, url_prefix='/facturas')

@bp.route('/generar', methods=['GET', 'POST'])
def generar():
    if request.method == 'POST':
        # Generar número único
        numero = 'F' + datetime.now().strftime('%Y%m') + '-' + str(uuid.uuid4())[:4].upper()
        
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

        # Generar archivos
        xml_path = generar_facturae(factura)
        pdf_path = generar_pdf(factura)
        factura.xml_path = xml_path
        factura.pdf_path = pdf_path
        db.session.commit()

        # Enviar
        enviar_factura(factura)
        factura.estado = 'enviada'
        db.session.commit()

        flash(f'Factura {numero} enviada por WhatsApp y email!')
        return redirect('/facturas/historial')

    return render_template('facturas/generar.html')

@bp.route('/historial')
def historial():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
    return render_template('facturas/historial.html', facturas=facturas)