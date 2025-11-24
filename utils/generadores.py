from weasyprint import HTML
import os

def generar_pdf(factura):
    os.makedirs("facturas_templates/facturas/pdf", exist_ok=True)
    path = f"facturas_templates/facturas/pdf/factura_{factura.numero}.pdf"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .logo {{ font-size: 48px; }}
            h1 {{ color: #5B21B6; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f0eafc; }}
            .total {{ font-size: 24px; font-weight: bold; text-align: right; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <span class="logo">🚀</span>
            <h1>NINFACTURA</h1>
            <p>Factura {factura.numero} • {factura.fecha.strftime('%d/%m/%Y')}</p>
        </div>

        <p><strong>Cliente:</strong> {factura.cliente_nombre}<br>
           <strong>NIF:</strong> {factura.cliente_nif}</p>

        <table>
            <tr><th>Concepto</th><th>Base imponible</th><th>IVA 21%</th><th>Total</th></tr>
            <tr>
                <td>Servicios de facturación Ninfactura</td>
                <td>{factura.base_imponible:.2f} €</td>
                <td>{factura.iva:.2f} €</td>
                <td>{factura.total:.2f} €</td>
            </tr>
        </table>

        <div class="total">
            TOTAL A PAGAR: {factura.total:.2f} €
        </div>

        <p style="margin-top: 60px; color: #888; font-size: 12px;">
            ¡Gracias por confiar en Ninfactura! 🚀💜<br>
            www.ninfactura.onrender.com
        </p>
    </body>
    </html>
    """

    HTML(string=html_content).write_pdf(path)
    return path
