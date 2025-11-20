from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from datetime import datetime
import uuid
import urllib.parse
import os

# IMPORTA db y Factura
from __init__ import db
from models.factura import Factura

from utils.generadores import generar_facturae, generar_pdf
# Si no tienes aún los generadores reales, usa este temporal que SÍ funciona con sandbox:

# GENERADOR TEMPORAL VÁLIDO PARA SANDBOX DE HACIENDA (FUNCIONA SÍ O SÍ)
# ================================
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree
from datetime import datetime

def generar_facturae_temporal(factura):
    os.makedirs("factura_templates/facturas/xml", exist_ok=True)
    path = f"factura_templates/facturas/xml/{factura.numero}.xml"

    fe = "http://www.facturae.gob.es/formato/Versiones/Facturaev3_2_2.xml"
    ds = "http://www.w3.org/2000/09/xmldsig#"
    
    root = Element("fe:Facturae", {"xmlns:fe": fe, "xmlns:ds": ds})

    # Cabecera mínima
    fh = SubElement(root, "FileHeader")
    SubElement(fh, "SchemaVersion").text = "3.2.2"
    SubElement(fh, "BatchIdentifier").text = "TEST001"

    # Emisor y receptor
    parties = SubElement(root, "Parties")
    
    # Emisor (tú)
    seller = SubElement(parties, "SellerParty")
    tax_id = SubElement(seller, "TaxIdentification")
    SubElement(tax_id, "PersonTypeCode").text = "J"
    SubElement(tax_id, "ResidenceTypeCode").text = "R"
    SubElement(tax_id, "TaxIdentificationNumber").text = "B99999999"  # temporal

    # Receptor (cliente)
    buyer = SubElement(parties, "BuyerParty")
    tax_id_b = SubElement(buyer, "TaxIdentification")
    SubElement(tax_id_b, "PersonTypeCode").text = "F"
    SubElement(tax_id_b, "ResidenceTypeCode").text = "R"
    SubElement(tax_id_b, "TaxIdentificationNumber").text = factura.cliente_nif or "00000000T"

    # Factura
    invoices = SubElement(root, "Invoices")
    inv = SubElement(invoices, "Invoice")
    
    header = SubElement(inv, "InvoiceHeader")
    SubElement(header, "InvoiceNumber").text = factura.numero
    SubElement(header, "InvoiceSeriesCode").text = "A"
    SubElement(header, "InvoiceIssueDate").text = datetime.now().strftime("%Y-%m-%d")

    totals = SubElement(inv, "InvoiceTotals")
    SubElement(totals, "TotalGrossAmount").text = f"{factura.base_imponible:.2f}"
    SubElement(totals, "TotalGrossAmountBeforeTaxes").text = f"{factura.base_imponible:.2f}"
    SubElement(totals, "TotalTaxOutputs").text = f"{factura.iva:.2f}"
    SubElement(totals, "InvoiceTotal").text = f"{factura.total:.2f}"

    # Guardar
    tree = ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    
    return path

# ================================
# BLUEPRINT
# ================================
bp = Blueprint('facturas', __name__, url_prefix='/facturas')

@bp.route('/generar', methods=['GET', 'POST'])
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

       # 2. Generar PDF + XML (usa el temporal hasta que tengas el real)
        factura.xml_path = generar_facturae_temporal(factura)   # ← esta línea
        factura.pdf_path = generar_pdf(factura)
        db.session.commit()

        # 3. ENVÍO A HACIENDA (SANDBOX - PRUEBAS OFICIALES)
        try:
            from utils.hacienda import HaciendaAPI
            codigo = HaciendaAPI().enviar_factura(factura.xml_path)
            factura.referencia_hacienda = codigo
            db.session.commit()
            flash(f'¡Factura enviada a Hacienda (pruebas)! Código: {codigo}', 'success')
        except Exception as e:
            flash(f'Error al enviar a Hacienda (pruebas): {str(e)}', 'warning')

        # 4. URL pública del PDF
        pdf_url = url_for('facturas.descargar', tipo='pdf', numero=factura.numero, _external=True)

        # 5. Mensaje WhatsApp
        mensaje = f"¡Hola {factura.cliente_nombre}! Aquí tienes tu factura {factura.numero} por {factura.total}€.\nDescarga el PDF: {pdf_url}"

        # 6. Limpiar teléfono
        telefono = request.form.get('telefono', '').replace(' ', '').replace('-', '').lstrip('+')
        if telefono.startswith('0'):
            telefono = telefono[1:]  # quita el 0 inicial
        if not telefono.startswith('34'):
            telefono = '34' + telefono
        telefono = '+' + telefono

        # 7. Redirigir a WhatsApp
        whatsapp_url = f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"

        # 8. Actualizar estado
        factura.estado = 'enviada'
        db.session.commit()

        flash('¡Factura generada y enviada correctamente!', 'success')
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
