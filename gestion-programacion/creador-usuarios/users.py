
import requests
import pandas as pd
import os

# ========= CONFIG =========
MOODLE_URL = "https://institutoloayzapresencial.edu.pe/TESTUAL/webservice/rest/server.php"
TOKEN = "218d0d11240cf17a7d78abb90e6b6caa"

EXCEL_FILE = "carga-moodle.xlsx"

# ========= MODELO CABECERAS =========
MODELO_CABECERAS = [
    "PERIODO", "MES", "NOMBRE MES", "ESPECIALIDAD", "ESPC_COD", "ESPC_ID", "FACTOR", "SEDE", "SEDE_COD", "SEDE_ID", "NUM_CICLO", "CICLO", "CICLO_ID", "MDL_CICLO_ID", "TURNO", "HORA1", "HORA2", "AULA1", "AULA2", "CURSO1", "CURSO1_COD", "MDL_CURSO1_ID", "SHORTNAME1", "CURSO2", "CURSO2_COD", "SHORTNAME2", "MDL_CURSO2_ID", "COD-EST", "EXTCODEST", "APELLIDO-EST", "NOMBRE-EST", "EMAIL-EST", "COD-DOC1", "EXTCODDOC1", "DOCENTE1", "COD-DOC2", "EXTCODDOC2", "DOCENTE2"
]

def crear_archivo_modelo(nombre_archivo):
    df_modelo = pd.DataFrame(columns=MODELO_CABECERAS)
    df_modelo.to_excel(nombre_archivo, index=False)
    print(f"✅ Archivo modelo '{nombre_archivo}' creado con las cabeceras necesarias.")

# ========= FUNCIONES MOODLE =========
def call_moodle_ws(function, params):
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

def crear_usuario(username, password, firstname, lastname, email):
    data = {
        "users[0][username]": username,
        "users[0][password]": password,
        "users[0][firstname]": firstname,
        "users[0][lastname]": lastname,
        "users[0][email]": email
    }
    resp = call_moodle_ws("core_user_create_users", data)
    if isinstance(resp, list) and len(resp) > 0 and "id" in resp[0]:
        return resp[0]["id"]
    else:
        print(f"❌ Error al crear usuario {username}: {resp}")
        return None

def matricular_usuario(user_id, course_id, role_id):
    data = {
        "enrolments[0][roleid]": role_id,
        "enrolments[0][userid]": user_id,
        "enrolments[0][courseid]": course_id
    }
    resp = call_moodle_ws("enrol_manual_enrol_users", data)
    if resp == {}:
        return True
    else:
        print(f"❌ Error al matricular usuario {user_id} en curso {course_id}: {resp}")
        return False

# ========= ROLES MOODLE =========
ROLE_ESTUDIANTE = 5
ROLE_DOCENTE = 3

# ========= PROCESO PRINCIPAL =========
def split_nombre_apellido(nombre_completo):
    partes = nombre_completo.strip().split()
    if len(partes) < 2:
        return (nombre_completo, "")
    return (" ".join(partes[1:]), partes[0])  # nombre(s), primer apellido

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

    for idx, row in df.iterrows():
        # --- ESTUDIANTE ---
        username_est = str(row["COD-EST"])
        password_est = str(row["COD-EST"])
        firstname_est = str(row["NOMBRE-EST"]).strip()
        lastname_est = str(row["APELLIDO-EST"]).strip()
        email_est = str(row["EMAIL-EST"]).strip() if pd.notna(row["EMAIL-EST"]) else f"{username_est}@mail.com"

        user_id_est = crear_usuario(username_est, password_est, firstname_est, lastname_est, email_est)
        if user_id_est:
            # Matricular en ambos cursos
            if pd.notna(row["MDL_CURSO1_ID"]):
                matricular_usuario(user_id_est, int(row["MDL_CURSO1_ID"]), ROLE_ESTUDIANTE)
            if pd.notna(row["MDL_CURSO2_ID"]):
                matricular_usuario(user_id_est, int(row["MDL_CURSO2_ID"]), ROLE_ESTUDIANTE)

        # --- DOCENTE 1 ---
        if pd.notna(row.get("DOCENTE1")) and pd.notna(row.get("COD-DOC1")):
            username_doc1 = str(row["COD-DOC1"])
            password_doc1 = str(row["COD-DOC1"])
            nombre_doc1, apellido_doc1 = split_nombre_apellido(str(row["DOCENTE1"]))
            email_doc1 = f"{username_doc1}@mail.com"
            user_id_doc1 = crear_usuario(username_doc1, password_doc1, nombre_doc1, apellido_doc1, email_doc1)
            if user_id_doc1 and pd.notna(row["MDL_CURSO1_ID"]):
                matricular_usuario(user_id_doc1, int(row["MDL_CURSO1_ID"]), ROLE_DOCENTE)

        # --- DOCENTE 2 ---
        if pd.notna(row.get("DOCENTE2")) and pd.notna(row.get("COD-DOC2")):
            username_doc2 = str(row["COD-DOC2"])
            password_doc2 = str(row["COD-DOC2"])
            nombre_doc2, apellido_doc2 = split_nombre_apellido(str(row["DOCENTE2"]))
            email_doc2 = f"{username_doc2}@mail.com"
            user_id_doc2 = crear_usuario(username_doc2, password_doc2, nombre_doc2, apellido_doc2, email_doc2)
            if user_id_doc2 and pd.notna(row["MDL_CURSO2_ID"]):
                matricular_usuario(user_id_doc2, int(row["MDL_CURSO2_ID"]), ROLE_DOCENTE)

    print("✅ Proceso terminado. Usuarios creados y matriculados.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
