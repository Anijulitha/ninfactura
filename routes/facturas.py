from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask import send_from_directory
import uuid
import urllib.parse
import os

# IMPORTA db y Factura
from __init__ import db
from models.factura import Factura

# ================================
# GENERADORES SIMULADOS (hasta que tengas los reales)
# ================================
try:
    from utils.generadores import generar_facturae, generar_pdf
except ImportError:
    def generar_facturae(factura):
        os.makedirs("factura_templates/facturas/xml", exist_ok=True)
        path = f"factura_templates/facturas/xml/{factura.numero}.xml"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"<factura>{factura.numero}</factura>")
        return path

    def generar_pdf(factura):
        os.makedirs("factura_templates/facturas/pdf", exist_ok=True)
        path = f"factura_templates/facturas/pdf/{factura.numero}.pdf"
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Factura {factura.numero} - {factura.total}€")
        return path

# ================================
# BLUEPRINT
# ================================
bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@bp.route('/generar', methods=['GET', 'POST'])
def generar():
    if request.method == 'POST':
        # 1. Generar número único
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
        factura.xml_path = generar_facturae(factura)
        factura.pdf_path = generar_pdf(factura)
        db.session.commit()

        # 3. ENVÍO A HACIENDA (OPCIONAL – COMENTADO HASTA QUE TENGAS CERTIFICADO)
        # ------------------------------------------------------------------
        # from utils.hacienda import HaciendaAPI
        # try:
        #     hacienda = HaciendaAPI(
        #         cert_path=os.getenv('HACIENDA_CERT_PATH'),
        #         cert_pass=os.getenv('HACIENDA_CERT_PASS')
        #     )
        #     codigo = hacienda.enviar_factura(factura.xml_path)
        #     factura.referencia_hacienda = codigo
        #     db.session.commit()
        #     flash(f'¡Factura enviada a Hacienda! Código: {codigo}')
        # except Exception as e:
        #     flash(f'Factura generada, pero error con Hacienda: {e}')
        # ------------------------------------------------------------------

        # 4. URL pública del PDF
        pdf_url = url_for('facturas.descargar', tipo='pdf', numero=factura.numero, _external=True)

        # 5. Mensaje WhatsApp
        mensaje = f"¡Hola {factura.cliente_nombre}! Aquí tienes tu factura {factura.numero} por {factura.total}€.\nDescarga el PDF: {pdf_url}"

        # 6. Teléfono limpio
        telefono = request.form.get('telefono', '').replace(' ', '').replace('-', '').lstrip('+')
        if not telefono.startswith('34'):
            telefono = '34' + telefono
        telefono = '+' + telefono

        # 7. Redirigir a WhatsApp
        whatsapp_url = f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"

        # 8. Actualizar estado
        factura.estado = 'enviada'
        db.session.commit()

        flash(f'Factura {numero} generada y lista para enviar por WhatsApp!')
        return redirect(whatsapp_url)

    return render_template('facturas/generar.html')

# ================================
# HISTORIAL Y DESCARGA
# ================================
@bp.route('/historial')
def historial():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
    return render_template('facturas/historial.html', facturas=facturas)

@bp.route('/descargar/<tipo>/<numero>')
def descargar(tipo, numero):
    if tipo == 'pdf':
        return send_from_directory('factura_templates/facturas/pdf', f'{numero}.pdf', as_attachment=True)
    elif tipo == 'xml':
        return send_from_directory('factura_templates/facturas/xml', f'{numero}.xml', as_attachment=True)
    else:
        return "Archivo no encontrado", 404
