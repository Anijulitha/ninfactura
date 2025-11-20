import requests
from flask import current_app

class HaciendaAPI:
    def enviar_factura(self, xml_path):
        url = "https://face-sandbox.gob.es/api/v1/facturas"
        
        with open(xml_path, "rb") as f:
            xml_data = f.read()

        files = {'file': ('factura.xml', xml_data, 'application/xml')}
        data = {'emailNotificacion': 'anijuli2893@gmail.com'}  # ← PON TU EMAIL REAL AQUÍ

        response = requests.post(url, files=files, data=data, timeout=30)

        if response.status_code in (200, 201):
            resultado = response.json()
            return resultado.get('codigo', 'TEST-OK')
        else:
            raise Exception(f"Error sandbox: {response.status_code} - {response.text}")
