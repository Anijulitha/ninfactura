import requests
import xml.etree.ElementTree as ET
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64

class HaciendaAPI:
    def __init__(self, cert_path, cert_pass):
        self.cert_path = cert_path
        self.cert_pass = cert_pass
        self.base_url = "https://face.gob.es/api/v1"

    def enviar_factura(self, xml_path):
        """Envía XML Facturae a FACe"""
        with open(xml_path, 'rb') as f:
            xml_data = f.read()

        # Carga certificado
        with open(self.cert_path, 'rb') as cert_file:
            cert = serialization.load_pem_private_key(
                cert_file.read(), self.cert_pass, backend=default_backend()
            )

        # Firma XML
        signature = cert.sign(
            xml_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature_b64 = base64.b64encode(signature).decode()

        # Envío a FACe
        headers = {
            'Content-Type': 'application/xml',
            'X-Signature': signature_b64
        }
        response = requests.post(
            f"{self.base_url}/facturas",
            data=xml_data,
            headers=headers,
            cert=(self.cert_path, self.cert_pass)
        )

        if response.status_code == 200:
            return response.json()['verificacion_code']
        else:
            raise Exception(f"Error FACe: {response.text}")
