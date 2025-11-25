from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from datetime import datetime
import uuid
import urllib.parse
import os

# IMPORTA db y Factura
from __init__ import db
from models.factura import Factura

# IMPORT DE FUNCIONES
from utils.generadores import generar_pdf, generar_facturae_temporal

# ================================
# BLUEPRINT CON PREFIX CORRECTO
# ================================
bp = Blueprint('facturas', __name__, url_prefix='/facturas')  # ¡¡AQUÍ ESTABA EL PROBLEMA!!

@bp.route('/', methods=['GET', 'POST'])  # ← ahora /facturas/ lleva directo al generador
def generar():
    if request.method == 'POST':
        # 1. Número único de factura
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

        # 2. Generar PDF + XML
        factura.xml_path = generar_facturae_temporal(factura)
        factura.pdf_path = generar_pdf(factura)
        db.session.commit()

        # 3. URL pública del PDF
        pdf_url = url_for('facturas.descargar', tipo='pdf', numero=factura.numero, _external=True)

        # 4. Mensaje WhatsApp
        mensaje = f"¡Hola {factura.cliente_nombre}! Aquí tienes tu factura {factura.numero} por {factura.total:.2f}€.\nDescarga el PDF: {pdf_url}"

        # 5. Limpiar teléfono
        telefono = request.form.get('telefono', '').replace(' ', '').replace('-', '').lstrip('+')
        if telefono.startswith('0'):
            telefono = telefono[1:]
        if not telefono.startswith('34'):
            telefono = '34' + telefono
        telefono = '+' + telefono

        # 6. Redirigir a WhatsApp
        whatsapp_url = f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"

        # 7. Actualizar estado
        factura.estado = 'enviada'
        db.session.commit()

        flash('¡Factura generada y enviada correctamente!', 'success')
        return redirect(whatsapp_url)

    return render_template('facturas/generar.html')


# ================================
# DESCARGA PDF Y XML
# ================================
@bp.route('/descargar/<tipo>/<numero>')
def descargar(tipo, numero):
    factura = Factura.query.filter_by(numero=numero).first_or_404()
    
    if tipo == 'pdf' and factura.pdf_path:
        return send_from_directory(
            os.path.dirname(factura.pdf_path),
            os.path.basename(factura.pdf_path),
            as_attachment=True
        )
    elif tipo == 'xml' and factura.xml_path:
        return send_from_directory(
            os.path.dirname(factura.xml_path),
            os.path.basename(factura.xml_path),
            as_attachment=True
        )
    else:
        flash("Archivo no encontrado", "danger")
        return redirect(url_for('facturas.generar'))
