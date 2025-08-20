import requests
import pandas as pd
import os

# # ========= CONFIG =========
# MOODLE_URL = "https://institutoloayzapresencial.edu.pe/TESTUAL/webservice/rest/server.php"
# TOKEN = "218d0d11240cf17a7d78abb90e6b6caa"
# EXCEL_FILE = "carga_ccursos.xlsx"

# ========= CONFIG =========
MOODLE_URL = "https://apac.net.pe/webservice/rest/server.php"
TOKEN = "6c0f01dc28a9a5e6f746760c3e0e6655"
EXCEL_FILE = "carga_ccursos.xlsx"

# ========= MODELO CABECERAS =========
MODELO_CABECERAS = [
    "CICLO_MDL_ID",
    "CURSO1",
    "SHORTNAME1",
    "CURSO2",
    "SHORTNAME2"
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

def get_courses_by_field(field, value):
    """Buscar cursos por shortname o fullname"""
    return call_moodle_ws("core_course_get_courses_by_field", {"field": field, "value": value})

def create_course(fullname, shortname, categoryid):
    """Crear curso en Moodle"""
    data = {
        "courses[0][fullname]": fullname,
        "courses[0][shortname]": shortname,
        "courses[0][categoryid]": categoryid
    }
    response = call_moodle_ws("core_course_create_courses", data)
    if isinstance(response, list) and len(response) > 0 and "id" in response[0]:
        return response[0]["id"]
    else:
        print(f"❌ Error al crear el curso '{shortname}': {response}")
        return None

def validar_duplicados(df):
    """Valida si hay shortnames duplicados en el Excel"""
    shorts = []
    for _, row in df.iterrows():
        if pd.notna(row["SHORTNAME1"]):
            shorts.append(row["SHORTNAME1"])
        if pd.notna(row["SHORTNAME2"]):
            shorts.append(row["SHORTNAME2"])
    series = pd.Series(shorts)
    repetidos = series[series.duplicated()].unique()
    if len(repetidos) > 0:
        print("⚠️ Hay SHORTNAMES duplicados en el Excel:")
        for rep in repetidos:
            print("   ", rep)
        return False
    return True

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

    # Continuar con el proceso normal
    df = pd.read_excel(EXCEL_FILE)

    # 1. Validar duplicados
    if not validar_duplicados(df):
        print("❌ Corrige los duplicados antes de ejecutar.")
        return

    # 2. Procesar cada fila y recolectar resultados
    resultados = []
    for _, row in df.iterrows():
        cat_id = int(row["CICLO_MDL_ID"])

        # Curso 1
        curso1_id = None
        if pd.notna(row["CURSO1"]) and pd.notna(row["SHORTNAME1"]):
            cursos_exist = get_courses_by_field("shortname", row["SHORTNAME1"])
            if cursos_exist.get("courses"):
                print(f"ℹ️ Ya existe el curso: {row['SHORTNAME1']} → {row['CURSO1']}")
                # Si ya existe, obtener el id del primer curso encontrado
                curso1_id = cursos_exist["courses"][0].get("id")
            else:
                new_id = create_course(row["CURSO1"], row["SHORTNAME1"], cat_id)
                if new_id is not None:
                    print(f"✅ Creado curso ID {new_id}: {row['SHORTNAME1']} → {row['CURSO1']}")
                    curso1_id = new_id

        # Curso 2
        curso2_id = None
        if pd.notna(row["CURSO2"]) and pd.notna(row["SHORTNAME2"]):
            cursos_exist = get_courses_by_field("shortname", row["SHORTNAME2"])
            if cursos_exist.get("courses"):
                print(f"ℹ️ Ya existe el curso: {row['SHORTNAME2']} → {row['CURSO2']}")
                curso2_id = cursos_exist["courses"][0].get("id")
            else:
                new_id = create_course(row["CURSO2"], row["SHORTNAME2"], cat_id)
                if new_id is not None:
                    print(f"✅ Creado curso ID {new_id}: {row['SHORTNAME2']} → {row['CURSO2']}")
                    curso2_id = new_id

        # Guardar resultado de la fila
        fila_resultado = row.to_dict()
        fila_resultado["CURSO1_ID"] = curso1_id
        fila_resultado["CURSO2_ID"] = curso2_id
        resultados.append(fila_resultado)

    # Guardar resultados en una nueva hoja del Excel
    df_resultados = pd.DataFrame(resultados)
    with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="ORIGINAL", index=False)
        df_resultados.to_excel(writer, sheet_name="CURSOS_IDS", index=False)

    print("🎯 Proceso terminado. Resultados guardados en hoja CURSOS_IDS.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
