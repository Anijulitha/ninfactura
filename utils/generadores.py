import os
from datetime import datetime

# Aseguramos las carpetas
os.makedirs("facturas_templates/facturas/pdf", exist_ok=True)
os.makedirs("facturas_templates/facturas/xml", exist_ok=True)


def generar_facturae(factura):
    """Genera XML Facturae (temporal válido para sandbox)"""
    path = f"facturas_templates/facturas/xml/{factura.numero}.xml"
    
    # Aquí puedes dejar tu código temporal o el real cuando lo tengas
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<factura>
  <numero>{factura.numero}</numero>
  <cliente>{factura.cliente_nombre}</cliente>
  <total>{factura.total}€</total>
  <fecha>{datetime.now().strftime('%d/%m/%Y')}</fecha>
</factura>""")
    
    return path


def generar_pdf(factura):
    """Genera PDF real (simulado pero en la ruta correcta)"""
    path = f"facturas_templates/facturas/pdf/factura_{factura.numero}.pdf"
    
    # Aquí pondrás ReportLab o WeasyPrint cuando quieras el PDF bonito
    # De momento creamos un archivo vacío para que la descarga funcione
    with open(path, "wb") as f:
        f.write(b"%PDF-1.4\n%Esto es un PDF de prueba generado por Ninfactura 🚀\n")
    
    return path
