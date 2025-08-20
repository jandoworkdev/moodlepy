import requests
import pandas as pd
import os

# # ========= CONFIG =========
# MOODLE_URL = "https://institutoloayzapresencial.edu.pe/TESTUAL/webservice/rest/server.php"
# TOKEN = "218d0d11240cf17a7d78abb90e6b6caa"
# ROOT_CATEGORY_ID = 1325
# # SE DEBE ASIGNAR EL ID DE LA CATEGORÍA RAÍZ
# EXCEL_FILE = "carga_ccatg.xlsx"

# ========= CONFIG =========
MOODLE_URL = "https://apac.net.pe/webservice/rest/server.php"
TOKEN = "6c0f01dc28a9a5e6f746760c3e0e6655"
ROOT_CATEGORY_ID = 306
# SE DEBE ASIGNAR EL ID DE LA CATEGORÍA RAÍZ
EXCEL_FILE = "carga_ccatg.xlsx"

# ========= MODELO CABECERAS =========
MODELO_CABECERAS = [
    "ESPECIALIDAD",
    "ESPC_ID",
    "SEDE",
    "SEDE_ID",
    "CICLO",
    "CICLO_ID"
]

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
    # Validar que la respuesta sea una lista de dicts
    if not isinstance(categories, list) or (len(categories) > 0 and not isinstance(categories[0], dict)):
        print(f"❌ Error al obtener categorías para parent_id={parent_id}. Respuesta inesperada: {categories}")
        raise Exception(f"Respuesta inesperada de get_categories: {categories}")
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
    if isinstance(response, list) and len(response) > 0 and "id" in response[0]:
        return response[0]["id"]
    else:
        print(f"❌ Error al crear la categoría '{name}': {response}")
        raise Exception(f"No se pudo crear la categoría '{name}'. Respuesta: {response}")

# ========= MAIN =========

def crear_archivo_modelo(nombre_archivo):
    """Crea un archivo Excel modelo con las cabeceras necesarias."""
    df_modelo = pd.DataFrame(columns=MODELO_CABECERAS)
    df_modelo.to_excel(nombre_archivo, index=False)
    print(f"✅ Archivo modelo '{nombre_archivo}' creado con las cabeceras necesarias.")

def main():
    # Preguntar si desea generar el archivo modelo
    respuesta = input("¿Desea generar un archivo modelo con las cabeceras necesarias antes de ejecutar? (S/N): ").strip().upper()
    if respuesta == "S":
        if os.path.exists(EXCEL_FILE):
            sobrescribir = input(f"El archivo '{EXCEL_FILE}' ya existe. ¿Desea sobrescribirlo? (S/N): ").strip().upper()
            if sobrescribir != "S":
                print("Operación cancelada. No se generó el archivo modelo.")
                return
        crear_archivo_modelo(EXCEL_FILE)
        print("Por favor, complete el archivo modelo y vuelva a ejecutar el programa.")
        return

    df = pd.read_excel(EXCEL_FILE)
    # Lista para guardar los resultados
    resultados = []

    for _, row in df.iterrows():
        especialidad = row["ESPECIALIDAD"]
        esp_id = row["ESPC_ID"]
        sede = row["SEDE"]
        sede_id = row["SEDE_ID"]
        ciclo = row["CICLO"]
        ciclo_id = row["CICLO_ID"]

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
            "CICLO": ciclo,
            "CICLO_ID": ciclo_id,
            "ID_CATEGORIA_CICLO": cat_ciclo_id
        })

    # Crear un DataFrame con los resultados
    df_resultados = pd.DataFrame(resultados)

    # Escribir los resultados en una nueva hoja del Excel
    with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="ORIGINAL", index=False)
        df_resultados.to_excel(writer, sheet_name="CATEGORIAS_IDS", index=False)

    print("✅ Proceso terminado. Categorías creadas/verificadas y IDs guardados en el Excel.")

if __name__ == "__main__":
    main()
