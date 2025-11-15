from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
from flask import send_from_directory
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

        # === URL PÚBLICA DEL PDF (USANDO RUTA DESCARGAR) ===
        pdf_url = url_for('facturas.descargar', tipo='pdf', numero=factura.numero, _external=True)

        # === MENSAJE PARA WHATSAPP ===
        mensaje = f"¡Hola {factura.cliente_nombre}! Aquí tienes tu factura {factura.numero} por {factura.total}€.\nDescarga el PDF: {pdf_url}"

        # === TELÉFONO LIMPIO ===
        telefono = request.form.get('telefono', '').replace(' ', '').replace('-', '').lstrip('+')
        if not telefono.startswith('34'):
            telefono = '34' + telefono
        if not telefono.startswith('+'):
            telefono = '+' + telefono

        # === REDIRIGIR A WHATSAPP ===
        whatsapp_url = f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"

        # === EMAIL SIMULADO ===
        print(f"EMAIL SIMULADO → {factura.cliente_email}")
        print(f"WHATSAPP → {whatsapp_url}")

        # === ACTUALIZAR ESTADO ===
        factura.estado = 'enviada'
        db.session.commit()

        flash(f'Factura {numero} generada! Abre WhatsApp para enviar.')
        return redirect(whatsapp_url)

    return render_template('facturas/generar.html')

@bp.route('/historial')
def historial():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
    return render_template('facturas/historial.html', facturas=facturas)

@bp.route('/descargar/<tipo>/<numero>')
def descargar(tipo, numero):
    """Sirve PDF o XML al cliente"""
    if tipo == 'pdf':
        return send_from_directory('factura_templates/facturas/pdf', f'{numero}.pdf', as_attachment=True)
    elif tipo == 'xml':
        return send_from_directory('facturas/xml', f'{numero}.xml', as_attachment=True)
    else:
        return "Archivo no encontrado", 404
