import requests
from flask import current_app

class PaperlessAPIClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def get_token(self, username, password):
        try:
            response = requests.post(
                f"{self.api_url}/token/",
                data={'username': username, 'password': password},
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get('token')
            current_app.logger.error(f"Error en la API: {response.status_code}")
            return None
        except requests.RequestException as e:
            current_app.logger.error(f"Error al conectar con la API: {str(e)}")
            return None