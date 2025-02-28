import requests
# import jwt
import time
from datetime import datetime


class CameraManager:
    def __init__(self, login_url, play_url, username, password):
        self.login_url = login_url
        self.play_url = play_url
        self.username = username
        self.password = password
        self.token_largo = None
        self.token_corto = None
        self.camera_id = None
        self.token_expiration = None

    def authenticate(self):
        """Obtiene el token largo al hacer login."""
        payload = {
            "user": self.username,
            "password": self.password,
            "language": "en_GB",
            "origin": "WebM",
            "platform": "smart2",
            "provider": "null"
            }
        headers = {"Content-Type": "application/json;charset=UTF-8",
                   "Accept": "application/json, text/plain, /",
                   "Origin": "https://alarmas.movistarproseguralarmas.es",
                   "Referer": "https://alarmas.movistarproseguralarmas.es/",
                   "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"}
        
        response = requests.post(self.login_url, json=payload, headers=headers)
        if response.status_code == 200:
            self.token_largo = response.json().get("data", {}).get("token")
            # self._set_token_expiration()
            print("✅ Autenticación exitosa.")
        else:
            raise Exception(f"❌ Error al autenticar: {response.status_code} - {response.text}")

    # def _set_token_expiration(self):
    #     """Intenta extraer la expiración del token largo si es un JWT."""
    #     if not self.token_largo:
    #         print("⚠️ No hay token largo disponible.")
    #         return

        # try:
            # Intenta decodificar el token para obtener la fecha de expiración
            # payload = jwt.decode(self.token_largo, options={"verify_signature": False})
            # exp_time = payload.get("exp")

            # if exp_time:
            #     self.token_expiration = datetime.fromtimestamp(exp_time)
            #     print(f"⏳ Token largo expira en: {self.token_expiration}")
            # else:
            #     print("⚠️ El token no contiene información de expiración.")

        # except jwt.DecodeError:
        #     print("⚠️ No se pudo extraer la expiración del token: No es un JWT válido.")
        # except Exception as e:
        #     print(f"⚠️ Error al procesar el token largo: {e}")

    # def _is_token_valid(self):
    #     """Verifica si el token largo sigue siendo válido."""
    #     if self.token_expiration is None:
    #         return False
    #     return time.time() < self.token_expiration.timestamp() - 60  # Se renueva 1 minuto antes de expirar
        


    def get_streaming_link(self):
        """Obtiene el token corto y genera el link de streaming."""
        # if not self._is_token_valid():
        #     print("🔄 Token largo expirado, autenticando nuevamente...")
        #     self.authenticate()

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://alarmas.movistarproseguralarmas.es",
            "Referer": "https://alarmas.movistarproseguralarmas.es/",
            "x-smart-token": self.token_largo,
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }
        response = requests.get(self.play_url, headers=headers)

        if response.status_code == 200:
            data = response.json().get("data", {})
            self.token_corto = data.get("accessToken")
            self.camera_id = data.get("code")
            streaming_url = f"https://{data.get('url')}/stream/hls/getPlaylist?access_token={self.token_corto}&camera_id={self.camera_id}"
            print(f"✅ Link generado: {streaming_url}")
            return streaming_url
        else:
            raise Exception(f"❌ Error al obtener el link: {response.status_code} - {response.text}")


