import requests
import pandas as pd

# ========= CONFIG =========
MOODLE_URL = "https://apac.net.pe/webservice/rest/server.php"
MOODLE_BASE = "https://apac.net.pe/course/view.php?id="
TOKEN = "6c0f01dc28a9a5e6f746760c3e0e6655"
OUTPUT_FILE = "cursos_modelo_paro.xlsx"

# ========= FUNCIONES =========
def call_moodle_ws(function, params):
    """Llamada al WS de Moodle"""
    params.update({
        "wstoken": TOKEN,
        "moodlewsrestformat": "json",
        "wsfunction": function
    })
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.post(MOODLE_URL, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

def get_all_courses():
    """Obtiene todos los cursos disponibles"""
    return call_moodle_ws("core_course_get_courses", {})  # devuelve todos

# ========= MAIN =========
def main():
    cursos = get_all_courses()
    resultados = []

    for curso in cursos:
        shortname = curso.get("shortname", "")
        if shortname.startswith("modelo_paro_ial"):  # filtro
            curso_id = curso["id"]
            url = f"{MOODLE_BASE}{curso_id}"
            resultados.append({
                "ID": curso_id,
                "SHORTNAME": shortname,
                "FULLNAME": curso.get("fullname", ""),
                "URL": url
            })
            print(f"✅ {shortname} -> {url}")

    if resultados:
        pd.DataFrame(resultados).to_excel(OUTPUT_FILE, index=False)
        print(f"🎯 Archivo generado: {OUTPUT_FILE} con {len(resultados)} cursos")
    else:
        print("⚠️ No se encontraron cursos con shortname que empiece por 'modelo_paro_ial'.")

if __name__ == "__main__":
    main()
