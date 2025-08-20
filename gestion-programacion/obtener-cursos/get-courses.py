import requests
import pandas as pd
import os

# ========= CONFIG =========
MOODLE_URL = "https://institutoloayzapresencial.edu.pe/TESTUAL/webservice/rest/server.php"
TOKEN = "218d0d11240cf17a7d78abb90e6b6caa"

# ========= MODELO CABECERAS =========
MODELO_CABECERAS = [
    "CICLO_MDL_ID",
    "CURSO",
    "SHORTNAME",
    "MDL_CURSO_ID"
]

# ========= FUNCIONES =========
def call_moodle_ws(function, params):
    """Llamada al WS de Moodle"""
    params.update({
        "wstoken": TOKEN,
        "moodlewsrestformat": "json",
        "wsfunction": function
    })
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
    }
    r = requests.post(MOODLE_URL, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

def crear_archivo_modelo(nombre_archivo):
    """Crea un archivo Excel modelo con las cabeceras necesarias."""
    df_modelo = pd.DataFrame(columns=MODELO_CABECERAS)
    df_modelo.to_excel(nombre_archivo, index=False)
    print(f"✅ Archivo modelo '{nombre_archivo}' creado con las cabeceras necesarias.")

def obtener_todos_los_cursos():
    """Obtiene todos los cursos de Moodle."""
    cursos = call_moodle_ws("core_course_get_courses", {})
    return cursos

def main():
    # Obtener todos los cursos
    cursos = obtener_todos_los_cursos()
    # Filtrar y estructurar los datos
    datos = []
    for curso in cursos:
        # Excluir categorías y cursos sin categoría válida
        if (
            "categoryid" in curso and curso["categoryid"] and
            "fullname" in curso and "shortname" in curso and
            "id" in curso
        ):
            datos.append({
                "CICLO_MDL_ID": curso["categoryid"],
                "CURSO": curso["fullname"],
                "SHORTNAME": curso["shortname"],
                "MDL_CURSO_ID": curso["id"]
            })
    df = pd.DataFrame(datos)
    df.to_excel("mdl-cursos.xlsx", index=False)
    print(f"✅ Archivo 'mdl-cursos.xlsx' generado con los cursos extraídos de Moodle.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
