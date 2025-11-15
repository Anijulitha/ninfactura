from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
import uuid
import urllib.parse
import os

# IMPORTA db Y Factura
from __init__ import db
from models.factura import Factura

# FUNCIONES SIMULADAS
try:
    from utils.generadores import generar_facturae, generar_pdf
except ImportError:
    def generar_facturae(factura):
        os.makedirs("facturas/xml", exist_ok=True)
        path = f"facturas/xml/{factura.numero}.xml"
        with open(path, "w") as f:
            f.write(f"<factura>{factura.numero}</factura>")
        return path

    def generar_pdf(factura):
        os.makedirs("facturas/pdf", exist_ok=True)
        path = f"facturas/pdf/{factura.numero}.pdf"
        with open(path, "w") as f:
            f.write(f"Factura {factura.numero} - {factura.total}€")
        return path

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

        # === ENVÍO POR WHATSAPP (ENLACE DIRECTO) ===
        telefono = request.form.get('telefono', '').replace(' ', '').replace('-', '')
        if not telefono.startswith('+'):
            telefono = '+34' + telefono

        mensaje = f"¡Hola {factura.cliente_nombre}! Aquí tienes tu factura {factura.numero} por {factura.total}€."
        pdf_url = request.url_root[:-1] + url_for('static', filename=factura.pdf_path.replace('facturas/', ''))

        whatsapp_url = f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje + ' ' + pdf_url)}"

        # === ENVÍO POR EMAIL (SIMULADO) ===
        print(f"EMAIL SIMULADO → {factura.cliente_email}: {mensaje}")
        print(f"WHATSAPP → {whatsapp_url}")

        # === ACTUALIZAR ESTADO ===
        factura.estado = 'enviada'
        db.session.commit()

        flash(f'Factura {numero} generada! Abre WhatsApp para enviar.')
        return redirect(whatsapp_url)  # ← ¡REDIRIGE A WHATSAPP!

    return render_template('facturas/generar.html')

@bp.route('/historial')
def historial():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
    return render_template('facturas/historial.html', facturas=facturas)
