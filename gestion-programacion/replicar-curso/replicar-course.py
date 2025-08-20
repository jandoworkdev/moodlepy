import requests
import pandas as pd
import os

# ========= CONFIG =========
MOODLE_URL = "https://apac.net.pe/webservice/rest/server.php"
TOKEN = "6c0f01dc28a9a5e6f746760c3e0e6655"
EXCEL_FILE = "carga_replicar.xlsx"

# ========= CABECERAS PARA EXCEL =========
MODELO_CABECERAS = [
    "CURSO_ORIGEN_SHORTNAME",   # Shortname del curso modelo
    "CURSO_DESTINO_SHORTNAME",  # Shortname del curso al que replicar
]

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
    """Obtener curso por shortname"""
    res = call_moodle_ws("core_course_get_courses_by_field", {
        "field": "shortname",
        "value": shortname
    })
    if res.get("courses"):
        return res["courses"][0]
    return None

def import_course_contents(sourceid, destid):
    """Importar contenidos de un curso modelo a otro existente."""
    params = {
        "importfrom": sourceid,
        "importto": destid
    }
    res = call_moodle_ws("core_course_import_course", params)
    if isinstance(res, dict) and "exception" in res:
        print(f"❌ Error al importar: {res}")
        return False
    return True

def restore_course_info(course):
    """Restaura fullname y shortname del curso después de la importación."""
    params = {
        "courses[0][id]": course["id"],
        "courses[0][fullname]": course["fullname"],
        "courses[0][shortname]": course["shortname"]
    }
    res = call_moodle_ws("core_course_update_courses", params)
    if isinstance(res, dict) and "exception" in res:
        print(f"⚠️ Error al restaurar nombres en {course['id']}: {res}")
        return False
    return True

def crear_archivo_modelo(nombre_archivo):
    """Crea un archivo Excel modelo con las cabeceras necesarias."""
    df_modelo = pd.DataFrame(columns=MODELO_CABECERAS)
    df_modelo.to_excel(nombre_archivo, index=False)
    print(f"✅ Archivo modelo '{nombre_archivo}' creado con las cabeceras necesarias.")

# ========= MAIN =========
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

    # Si ya existe, continuar con replicación
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ No existe el archivo '{EXCEL_FILE}'. Ejecuta de nuevo y elige 'S' para generarlo.")
        return

    df = pd.read_excel(EXCEL_FILE)
    resultados = []

    for _, row in df.iterrows():
        origen_sn = row["CURSO_ORIGEN_SHORTNAME"]
        destino_sn = row["CURSO_DESTINO_SHORTNAME"]

        curso_origen = get_course_by_shortname(origen_sn)
        curso_destino = get_course_by_shortname(destino_sn)

        if not curso_origen:
            print(f"❌ No se encontró curso origen: {origen_sn}")
            continue
        if not curso_destino:
            print(f"❌ No se encontró curso destino: {destino_sn}")
            continue

        print(f"📌 Importando contenidos de {origen_sn} → {destino_sn}...")

        # Guardar nombre y shortname originales del destino
        curso_destino_info = {
            "id": curso_destino["id"],
            "fullname": curso_destino["fullname"],
            "shortname": curso_destino["shortname"]
        }

        ok = import_course_contents(curso_origen["id"], curso_destino["id"])

        if ok:
            # Restaurar nombre y shortname originales
            restore_course_info(curso_destino_info)
            print(f"✅ Contenidos replicados en {destino_sn} (nombre restaurado)")
            resultados.append({
                "CURSO_ORIGEN": origen_sn,
                "CURSO_DESTINO": destino_sn,
                "ESTADO": "OK"
            })
        else:
            resultados.append({
                "CURSO_ORIGEN": origen_sn,
                "CURSO_DESTINO": destino_sn,
                "ESTADO": "ERROR"
            })

    if resultados:
        df_res = pd.DataFrame(resultados)
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="ORIGINAL", index=False)
            df_res.to_excel(writer, sheet_name="RESULTADOS", index=False)
        print("🎯 Proceso finalizado. Revisa la hoja RESULTADOS en el Excel.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
