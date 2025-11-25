import os
from datetime import datetime

# ======================= XML PARA HACIENDA (sandbox) =======================
def generar_facturae_temporal(factura):
    os.makedirs("factura_templates/facturas/xml", exist_ok=True)
    path = f"factura_templates/facturas/xml/{factura.numero}.xml"

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


# ============================= PDF BONITO =============================
def generar_pdf(factura):
    # ¡¡AQUÍ ESTABA EL ERROR!! → ahora mismo nombre que el XML
    os.makedirs("factura_templates/facturas/pdf", exist_ok=True)
    path = f"factura_templates/facturas/pdf/factura_{factura.numero}.pdf"

    contenido = f"""%PDF-1.4
%âãÏÓ
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R /F2 6 0 R>>>>>> endobj
4 0 obj <</Length 1400>> stream
BT
/F2 48 Tf 100 780 Td (NINFACTURA) Tj
/F1 28 Tf 180 730 Td (Factura {factura.numero}) Tj
/F1 20 Tf 80 680 Td (Cliente: {factura.cliente_nombre}) Tj
80 650 Td (NIF: {factura.cliente_nif or 'Pendiente'}) Tj
80 600 Td (Concepto: Servicios de facturación Ninfactura) Tj
80 550 Td (Base imponible: {factura.base_imponible:.2f} EUR) Tj
80 520 Td (IVA 21%: {factura.iva:.2f} EUR) Tj
/F2 40 Tf 80 460 Td (TOTAL: {factura.total:.2f} EUR) Tj
/F1 18 Tf 80 400 Td (¡Gracias por confiar en Ninfactura! 🚀💜) Tj
80 370 Td (www.ninfactura.onrender.com) Tj
ET
endstream endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>> endobj
6 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj
xref
0 7
0000000000 65535 f 
0000000015 00000 n 
0000000079 00000 n 
0000000165 00000 n 
0000000316 00000 n 
0000000703 00000 n 
0000000795 00000 n 
trailer <</Size 7 /Root 1 0 R>>
startxref
1450
%%EOF""".encode('latin-1')

    with open(path, "wb") as f:
        f.write(contenido)
    return path
