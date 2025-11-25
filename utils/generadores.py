import os
from datetime import datetime

def generar_facturae_temporal(factura):
    os.makedirs("factura_templates/facturas/xml", exist_ok=True)
    path = f"factura_templates/facturas/xml/{factura.numero}.xml"

    # XML temporal válido para sandbox
    contenido = f"""<?xml version="1.0" encoding="UTF-8"?>
<fe:Facturae xmlns:fe="http://www.facturae.gob.es/formato/Versiones/Facturaev3_2_2.xml">
  <FileHeader><SchemaVersion>3.2.2</SchemaVersion></FileHeader>
  <Parties>
    <SellerParty><TaxIdentification><TaxIdentificationNumber>B99999999</TaxIdentificationNumber></TaxIdentification></SellerParty>
    <BuyerParty><TaxIdentification><TaxIdentificationNumber>{factura.cliente_nif or '00000000T'}</TaxIdentificationNumber></TaxIdentification></BuyerParty>
  </Parties>
  <Invoices>
    <Invoice>
      <InvoiceHeader><InvoiceNumber>{factura.numero}</InvoiceNumber></InvoiceHeader>
      <InvoiceTotals><InvoiceTotal>{factura.total:.2f}</InvoiceTotal></InvoiceTotals>
    </Invoice>
  </Invoices>
</fe:Facturae>"""
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)
    return path

def generar_pdf(factura):
    os.makedirs("facturas_templates/facturas/pdf", exist_ok=True)
    path = f"facturas_templates/facturas/pdf/factura_{factura.numero}.pdf"

    contenido = f"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj
4 0 obj <</Length 700>> stream
BT /F1 36 Tf 180 780 Td (NINFACTURA) Tj
   /F1 26 Tf 150 730 Td (Factura {factura.numero}) Tj
   /F1 20 Tf 50 680 Td (Cliente: {factura.cliente_nombre}) Tj
   50 650 Td (NIF: {factura.cliente_nif or 'Pendiente'}) Tj
   50 600 Td (Concepto: Servicios Ninfactura) Tj
   50 550 Td (Base imponible: {factura.base_imponible:.2f} €) Tj
   50 520 Td (IVA 21%: {factura.iva:.2f} €) Tj
   /F1 36 Tf 50 460 Td (TOTAL: {factura.total:.2f} €) Tj
   /F1 18 Tf 50 380 Td (Gracias por confiar en Ninfactura! 🚀💜) Tj
ET
endstream endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>> endobj
xref 0 6
0000000000 65535 f 
0000000010 00000 n 
0000000074 00000 n 
0000000125 00000 n 
0000000285 00000 n 
0000000700 00000 n 
trailer <</Size 6 /Root 1 0 R>> startxref 1000 %%EOF""".encode('utf-8')   # ← AQUÍ EL CAMBIO: utf-8 en vez de latin-1

    with open(path, "wb") as f:
        f.write(contenido)
    return path
