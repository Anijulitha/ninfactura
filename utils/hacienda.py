import requests
import os
from OpenSSL import crypto

class HaciendaAPI:
    def enviar_factura(self, xml_path):
        cert_path = "certs/certificado_ninfactura.p12"
        cert_pass = "librabril2893!"   # ← PON LA CONTRASEÑA QUE ELEGISTE AL EXPORTAR

        try:
            with open(xml_path, "rb") as f:
                xml_data = f.read()

            p12 = crypto.load_pkcs12(open(cert_path, "rb").read(), cert_pass.encode())
            cert = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
            key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())

            files = {'factura': ('factura.xml', xml_data, 'application/xml')}
            
            response = requests.post(
                "https://www1.agenciatributaria.gob.es/wlpl/OVCT/RecepcionFacturas",
                files=files,
                cert=(cert, key),
                timeout=40
            )

            if response.status_code == 200:
                return "ENVIADA-OK-" + response.text[-12:]
            else:
                return f"ERROR-{response.status_code}: {response.text[:200]}"

        except Exception as e:
            return f"ERROR CERT: {str(e)}"
