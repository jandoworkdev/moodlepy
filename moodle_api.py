# capa de conexión con Moodle
import requests

# -----------------------------
# Configuración del cliente Moodle
# -----------------------------
MOODLE_URL = "https://institutoloayzapresencial.edu.pe/TESTUAL"
SERVICE = "moodle_mobile_app"   # Ajustar si el admin habilita otro servicio

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


class MoodleAPI:
    def __init__(self):
        self.token = None

    # -----------------------------
    # Login con usuario y contraseña
    # -----------------------------
    def login(self, username, password):
        try:
            params = {
                "username": username,
                "password": password,
                "service": SERVICE
            }
            url = f"{MOODLE_URL}/login/token.php"
            response = requests.post(url, params=params, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            if "token" in data:
                self.token = data["token"]
                return True
            else:
                print("⚠️ Error de login:", data)
                return False
        except Exception as e:
            print("❌ Excepción en login:", e)
            return False

    # -----------------------------
    # Ejemplo: obtener cursos
    # -----------------------------
    def get_courses(self):
        if not self.token:
            return {"error": "No autenticado"}

        params = {
            "wstoken": self.token,
            "wsfunction": "core_course_get_courses",
            "moodlewsrestformat": "json"
        }
        url = f"{MOODLE_URL}/webservice/rest/server.php"
        try:
            response = requests.get(url, params=params, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
