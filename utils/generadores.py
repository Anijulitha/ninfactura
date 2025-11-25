import os

def generar_pdf(factura):
    os.makedirs("factura_templates/facturas/pdf", exist_ok=True)
    path = f"factura_templates/facturas/pdf/factura_{factura.numero}.pdf"

    contenido = f"""%PDF-1.4
%âãÏÓ
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R /F2 6 0 R>>>>>> endobj
4 0 obj <</Length 1600>> stream
BT
/F2 52 Tf 140 790 Td (NINFACTURA) Tj
/F1 32 Tf 170 740 Td (Factura {factura.numero}) Tj
/F1 22 Tf 80 690 Td (Cliente: {factura.cliente_nombre or 'Anónimo'}) Tj
80 660 Td (NIF: {factura.cliente_nif or 'Pendiente'}) Tj
80 610 Td (Concepto: Servicios de facturación Ninfactura) Tj
80 560 Td (Base imponible: {factura.base_imponible:.2f} €) Tj
80 530 Td (IVA 21%: {factura.iva:.2f} €) Tj
/F2 48 Tf 80 470 Td (TOTAL: {factura.total:.2f} €) Tj
/F1 20 Tf 80 400 Td (Gracias por confiar en Ninfactura!) Tj
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
1650
%%EOF""".encode('latin-1')

    with open(path, "wb") as f:
        f.write(contenido)
    return path
