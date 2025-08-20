import requests
import pandas as pd
import os

# ========= CONFIG =========
MOODLE_URL = "https://apac.net.pe/webservice/rest/server.php"
MOODLE_BASE = "https://apac.net.pe/course/view.php?id="  # base para construir URL
TOKEN = "6c0f01dc28a9a5e6f746760c3e0e6655"
EXCEL_FILE = "shortnames.xlsx"   # archivo de entrada
OUTPUT_FILE = "cursos_urls.xlsx" # archivo de salida

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

def get_course_by_shortname(shortname):
    """Obtiene curso por shortname"""
    res = call_moodle_ws("core_course_get_courses_by_field", {
        "field": "shortname",
        "value": shortname
    })
    if res.get("courses"):
        return res["courses"][0]
    return None

# ========= MAIN =========
def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ No existe el archivo '{EXCEL_FILE}'")
        return

    df_in = pd.read_excel(EXCEL_FILE)
    resultados = []
    resultados_ids = []

    for _, row in df_in.iterrows():
        shortname = str(row["SHORTNAMES"]).strip()
        curso = get_course_by_shortname(shortname)

        if curso:
            curso_id = curso["id"]
            url = f"{MOODLE_BASE}{curso_id}"
            print(f"✅ {shortname} -> ID={curso_id}, URL={url}")

            resultados.append({
                "SHORTNAME": shortname,
                "ID": curso_id,
                "URL": url
            })
            resultados_ids.append({
                "SHORTNAME": shortname,
                "ID": curso_id
            })
        else:
            print(f"❌ No se encontró curso con shortname {shortname}")
            resultados.append({
                "SHORTNAME": shortname,
                "ID": "NO_ENCONTRADO",
                "URL": ""
            })
            resultados_ids.append({
                "SHORTNAME": shortname,
                "ID": "NO_ENCONTRADO"
            })

    # Guardar en dos hojas dentro del mismo Excel
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        pd.DataFrame(resultados).to_excel(writer, sheet_name="URLS", index=False)
        pd.DataFrame(resultados_ids).to_excel(writer, sheet_name="IDS", index=False)

    print(f"🎯 Proceso finalizado. Revisa el archivo '{OUTPUT_FILE}' con hojas 'URLS' y 'IDS'.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
