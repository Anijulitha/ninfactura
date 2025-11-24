import requests
from cryptography.hazmat.primitives.serialization import pkcs12
import os

class HaciendaAPI:
    def enviar_factura(self, xml_path):
        cert_path = "certs/certificado_ninfactura.p12"
        cert_pass = "librabril2893!"  

        try:
            with open(xml_path, "rb") as f:
                xml_data = f.read()

            
            with open(cert_path, "rb") as f:
                private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                    f.read(), cert_pass.encode()
                )

            cert_pem = certificate.public_bytes(encoding=import serialization.Encoding.PEM)
            key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            files = {'factura': ('factura.xml', xml_data, 'application/xml')}
            
            response = requests.post(
                "https://www1.agenciatributaria.gob.es/wlpl/OVCT/RecepcionFacturas",
                files=files,
                cert=(cert_pem, key_pem),
                timeout=60
            )

            if response.status_code == 200:
                return "ENVIADA-OK-" + response.text[-12:]
            else:
                return f"ERROR-{response.status_code}"

        except Exception as e:
            return f"ERROR CERT: {str(e)[:100]}"
