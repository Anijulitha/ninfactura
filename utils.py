import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from twilio.rest import Client

# === CONFIG (cambia por tus claves) ===
TWILIO_SID = 'TU_SID'
TWILIO_TOKEN = 'TU_TOKEN'
TWILIO_FROM = 'whatsapp:+14155238886'
EMAIL_USER = 'tuemail@gmail.com'
EMAIL_PASS = 'tu_app_password'

def generar_facturae(factura):
    root = ET.Element('fe:Facturae', {
        'xmlns:fe': 'http://www.facturae.gob.es/formato/Versiones/Facturaev3_2_2.xml'
    })
    # (Versión simplificada - puedes ampliar con AEAT specs)
    ET.SubElement(root, 'InvoiceNumber').text = factura.numero
    ET.SubElement(root, 'IssueDate').text = factura.fecha_emision.strftime('%Y-%m-%d')

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(encoding='utf-8')
    os.makedirs('facturas', exist_ok=True)
    path = f"facturas/factura_{factura.numero}.xml"
    with open(path, 'wb') as f:
        f.write(xml_str)
    return path

def generar_pdf(factura):
    path = f"facturas/factura_{factura.numero}.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, f"FACTURA {factura.numero}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Cliente: {factura.cliente_nombre}")
    c.drawString(50, 750, f"Total: {factura.total:.2f} €")
    c.save()
    return path

def enviar_factura(factura):
    xml_path = factura.xml_path
    pdf_path = factura.pdf_path

    # WhatsApp
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        from_=TWILIO_FROM,
        to=f"whatsapp:{factura.cliente_telefono}",
        body=f"Factura {factura.numero} lista! Total: {factura.total}€\nPaga con Bizum: 123456789",
        media_url=[f"http://tudominio.com/{pdf_path}"]
    )

    # Email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = factura.cliente_email
    msg['Subject'] = f"Factura {factura.numero}"
    msg.attach(MIMEText(f"Adjunta tu factura. Total: {factura.total}€", 'plain'))

    for path in [xml_path, pdf_path]:
        with open(path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(path)}")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, factura.cliente_email, msg.as_string())
    server.quit()