import os
from datetime import datetime

# ==================== PDF BONITO CON HTML (pero sin WeasyPrint) ====================
def generar_pdf(factura):
    os.makedirs("facturas_templates/facturas/pdf", exist_ok=True)
    path = f"facturas_templates/facturas/pdf/factura_{factura.numero}.pdf"

    # HTML precioso que usaremos cuando tengas WeasyPrint o ReportLab
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f9f9ff; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .logo {{ font-size: 60px; }}
            h1 {{ color: #5B21B6; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
            th, td {{ border: 1px solid #ddd; padding: 15px; }}
            th {{ background-color: #f0eafc; color: #5B21B6; }}
            .total {{ font-size: 28px; font-weight: bold; text-align: right; margin-top: 40px; color: #5B21B6; }}
            .footer {{ margin-top: 80px; text-align: center; color: #888; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🚀</div>
            <h1>NINFACTURA</h1>
            <p>Factura {factura.numero} • {factura.fecha.strftime('%d/%m/%Y')}</p>
        </div>

        <p><strong>Cliente:</strong> {factura.cliente_nombre}<br>
           <strong>NIF:</strong> {factura.cliente_nif or 'Pendiente'}</p>

        <table>
            <tr><th>Concepto</th><th>Base</th><th>IVA 21%</th><th>Total</th></tr>
            <tr>
                <td>Servicios Ninfactura</td>
                <td>{factura.base_imponible:.2f} €</td>
                <td>{factura.iva:.2f} €</td>
                <td>{factura.total:.2f} €</td>
            </tr>
        </table>

        <div class="total">
            TOTAL A PAGAR: {factura.total:.2f} €
        </div>

        <div class="footer">
            ¡Gracias por confiar en Ninfactura! 🚀💜<br>
            www.ninfactura.onrender.com
        </div>
    </body>
    </html>
    """

    # PDF temporal válido (para que se abra mientras ponemos ReportLab)
    pdf_content = b"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]
    /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj
4 0 obj <</Length 500>> stream
BT /F1 24 Tf 100 700 Td (Factura NINFACTURA) Tj
100 650 Td (Numero: {numero}) Tj
100 600 Td (Cliente: {cliente}) Tj
100 550 Td (Total: {total} EUR) Tj ET
endstream endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000074 00000 n 
0000000125 00000 n 
0000000285 00000 n 
0000000475 00000 n 
trailer <</Size 6 /Root 1 0 R>>
startxref
600
%%EOF
""".replace(b"{numero}", factura.numero.encode()).replace(b"{cliente}", factura.cliente_nombre.encode()[:50]).replace(b"{total}", str(factura.total).encode())

    with open(path, "wb") as f:
        f.write(pdf_content)
    
    return path


# ==================== XML TEMPORAL PARA HACIENDA (sandbox) ====================
def generar_facturae_temporal(factura):
    os.makedirs("facturas_templates/facturas/xml", exist_ok=True)
    path = f"facturas_templates/facturas/xml/{factura.numero}.xml"
    
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
      <InvoiceTotals><TotalGrossAmount>{factura.base_imponible:.2f}</TotalGrossAmount></InvoiceTotals>
    </Invoice>
  </Invoices>
</fe:Facturae>"""
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)
    return path
