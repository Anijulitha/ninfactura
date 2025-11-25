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
    os.makedirs("factura_templates/facturas/pdf", exist_ok=True)
    path = f"factura_templates/facturas/pdf/factura_{factura.numero}.pdf"

    # PDF temporal válido
    contenido = b"%PDF-1.4\n1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n3 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>>\nendobj\n4 0 obj\n<</Length 250>>\nstream\nBT /F1 24 Tf 100 700 Td (Factura Ninfactura) Tj\n100 650 Td (Numero: {numero}) Tj\n100 600 Td (Total: {total:.2f} EUR) Tj ET\nendstream\nendobj\n5 0 obj\n<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000074 00000 n \n0000000125 00000 n \n0000000285 00000 n \n0000000475 00000 n \ntrailer <</Size 6 /Root 1 0 R>>\nstartxref\n600\n%%EOF\n"

    with open(path, "wb") as f:
        f.write(contenido.replace(b"{numero}", factura.numero.encode()).replace(b"{total}", str(factura.total).encode()))

    return path
