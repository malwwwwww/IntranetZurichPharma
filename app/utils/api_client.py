import requests
from flask import current_app

class PaperlessAPIClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def get_token(self, username, password):
        try:
            current_app.logger.debug(f"Solicitando token en {self.api_url}/token/")
            response = requests.post(
                f"{self.api_url}/token/",
                data={'username': username, 'password': password},
                timeout=5
            )
            if response.status_code == 200:
                token = response.json().get('token')
                current_app.logger.debug("Token obtenido exitosamente")
                return token
            else:
                current_app.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            current_app.logger.error(f"Error al conectar con la API: {str(e)}")
            return None

    def get_user_info(self, token, username):
        try:
            headers = {'Authorization': f'Token {token}'}
            current_app.logger.debug(f"Obteniendo información del usuario en {self.api_url}/users/")
            response = requests.get(f"{self.api_url}/users/", headers=headers, timeout=5)
            if response.status_code == 200:
                users = response.json().get('results', [])
                for user in users:
                    if user['username'] == username:
                        current_app.logger.debug(f"Usuario encontrado: {user}")
                        return user
                current_app.logger.error(f"No se encontró el usuario {username}")
                return None
            else:
                current_app.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            current_app.logger.error(f"Error al conectar con la API: {str(e)}")
            return None

    def get_document(self, token, doc_id):
        try:
            headers = {'Authorization': f'Token {token}'}
            current_app.logger.debug(f"Obteniendo documento {doc_id} en {self.api_url}/documents/{doc_id}/")
            response = requests.get(f"{self.api_url}/documents/{doc_id}/", headers=headers, timeout=5)
            if response.status_code == 200:
                current_app.logger.debug("Documento obtenido exitosamente")
                return response.json()
            else:
                current_app.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            current_app.logger.error(f"Error al conectar con la API: {str(e)}")
            return None