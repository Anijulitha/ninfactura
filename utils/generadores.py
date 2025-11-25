import os

# ======================= XML HACIENDA =======================
def generar_facturae_temporal(factura):
    os.makedirs("static/facturas/xml", exist_ok=True)
    path = f"static/facturas/xml/{factura.numero}.xml"

    contenido = f"""<?xml version="1.0" encoding="UTF-8"?>
<fe:Facturae xmlns:fe="http://www.facturae.gob.es/formato/Versiones/Facturaev3_2_2.xml">
  <FileHeader><SchemaVersion>3.2.2</SchemaVersion></FileHeader>
  <Invoices><Invoice><InvoiceHeader><InvoiceNumber>{factura.numero}</InvoiceNumber></InvoiceHeader></Invoice></Invoices>
</fe:Facturae>"""
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)
    return path


# ========================== PDF SIMPLE Y QUE SIEMPRE FUNCIONA ==========================
def generar_pdf(factura):
    # Usamos carpeta "static" que Render nunca falla
    os.makedirs("static/facturas/pdf", exist_ok=True)
    path = f"static/facturas/pdf/factura_{factura.numero}.pdf"

    # PDF ultra-simple pero con TODO visible (sin emojis ni caracteres raros)
    contenido = f"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj
4 0 obj <</Length 900>> stream
BT /F1 42 Tf 150 800 Td (NINFACTURA) Tj
   /F1 28 Tf 170 750 Td (Factura {factura.numero}) Tj
   /F1 20 Tf 80 700 Td (Cliente: {factura.cliente_nombre}) Tj
   80 670 Td (NIF: {factura.cliente_nif or 'Pendiente'}) Tj
   80 620 Td (Concepto: Servicios Ninfactura) Tj
   80 570 Td (Base: {factura.base_imponible:.2f} EUR - IVA: {factura.iva:.2f} EUR) Tj
   /F1 38 Tf 80 500 Td (TOTAL: {factura.total:.2f} EUR) Tj
   /F1 18 Tf 80 420 Td (Gracias por confiar en Ninfactura) Tj
   80 390 Td (www.ninfactura.onrender.com) Tj
ET
endstream endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>> endobj
xref 0 6 0000000000 65535 f 0000000010 00000 n 0000000074 00000 n 0000000128 00000 n 0000000285 00000 n 0000000700 00000 n 
trailer <</Size 6 /Root 1 0 R>> startxref 1000 %%EOF""".encode('ascii', 'ignore')

    with open(path, "wb") as f:
        f.write(contenido)
    return path
