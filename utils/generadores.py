# utils/generadores.py - Funciones para crear XML, PDF y enviar

def generar_facturae(factura):
    """Simula generación de Facturae XML"""
    path = f"facturas_xml/{factura.numero}.xml"
    # Aquí iría el código real con librerías
    print(f"XML generado: {path}")
    return path

def generar_pdf(factura):
    """Simula generación de PDF"""
    path = f"facturas_pdf/{factura.numero}.pdf"
    # Aquí iría ReportLab o WeasyPrint
    print(f"PDF generado: {path}")
    return path

def enviar_factura(factura):
    """Simula envío por WhatsApp + Email"""
    print(f"📱 Enviando a {factura.cliente_telefono} (WhatsApp)")
    print(f"📧 Enviando a {factura.cliente_email}")
