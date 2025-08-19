import requests
import pandas as pd

# ========= CONFIG =========
MOODLE_URL = "https://institutoloayzapresencial.edu.pe/TESTUAL/webservice/rest/server.php"
TOKEN = "218d0d11240cf17a7d78abb90e6b6caa"
ROOT_CATEGORY_ID = 1152
# SE DEBE ASIGNAR EL ID DE LA CATEGORÍA RAÍZ
EXCEL_FILE = "carga_ccatg.xlsx"

# ========= FUNCIONES =========
def call_moodle_ws(function, params):
    """Llamar al WS de Moodle"""
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

def get_categories(parent_id):
    """Obtener subcategorías de un padre"""
    return call_moodle_ws("core_course_get_categories", {"criteria[0][key]": "parent", "criteria[0][value]": parent_id})

def get_or_create_category(name, parent_id, idnumber=None):
    """Verifica si existe, sino crea la categoría"""
    categories = get_categories(parent_id)
    for cat in categories:
        if cat["name"] == name:
            return cat["id"]

    # Crear si no existe
    data = {
        "categories[0][name]": name,
        "categories[0][parent]": parent_id
    }
    if idnumber:
        data["categories[0][idnumber]"] = idnumber

    response = call_moodle_ws("core_course_create_categories", data)
    return response[0]["id"]

# ========= MAIN =========
def main():

    df = pd.read_excel(EXCEL_FILE)
    # Lista para guardar los resultados
    resultados = []

    for _, row in df.iterrows():
        especialidad = row["ESPECIALIDAD"]
        esp_id = row["ESPC_ID"]
        sede = row["SEDE"]
        sede_id = row["SEDE_ID"]
        ciclo = row["CICLO1"]
        ciclo_id = row["CICLO1_ID"]

        # Nivel 1: Especialidad
        cat_especialidad_id = get_or_create_category(especialidad, ROOT_CATEGORY_ID, esp_id)

        # Nivel 2: Sede
        cat_sede_id = get_or_create_category(sede, cat_especialidad_id, sede_id)

        # Nivel 3: Ciclo
        cat_ciclo_id = get_or_create_category(ciclo, cat_sede_id, str(ciclo_id))

        # Guardar los ids en la lista de resultados
        resultados.append({
            "ESPECIALIDAD": especialidad,
            "ESPC_ID": esp_id,
            "ID_CATEGORIA_ESPECIALIDAD": cat_especialidad_id,
            "SEDE": sede,
            "SEDE_ID": sede_id,
            "ID_CATEGORIA_SEDE": cat_sede_id,
            "CICLO1": ciclo,
            "CICLO1_ID": ciclo_id,
            "ID_CATEGORIA_CICLO": cat_ciclo_id
        })

    # Crear un DataFrame con los resultados
    df_resultados = pd.DataFrame(resultados)

    # Escribir los resultados en una nueva hoja del Excel
    with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="ORIGINAL", index=False)
        df_resultados.to_excel(writer, sheet_name="CATEGORIAS_IDS", index=False)

    print("✅ Proceso terminado. Categorías creadas/verificadas y IDs guardados en el Excel.")

if __name__ == "__main__":
    main()
