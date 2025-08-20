import requests
import pandas as pd
import os

# ========= CONFIG =========
MOODLE_URL = (
    "https://institutoloayzapresencial.edu.pe/TESTUAL/webservice/rest/server.php"
)
TOKEN = "218d0d11240cf17a7d78abb90e6b6caa"

EXCEL_FILE = "carga-moodle.xlsx"
SALIDA_FILE = "usuarios_generados.xlsx"

# ========= CABECERAS NECESARIAS =========
MODELO_CABECERAS_MIN = [
    "MDL_CURSO1_ID",
    "MDL_CURSO2_ID",
    "COD-EST",
    "APELLIDO-EST",
    "NOMBRE-EST",
    "EMAIL-EST",
    "COD-DOC1",
    "DOCENTE1",
    "COD-DOC2",
    "DOCENTE2",
]

# ========= LISTA PARA EXPORTAR =========
usuarios_creados = []


def crear_archivo_modelo(nombre_archivo):
    df_modelo = pd.DataFrame(columns=MODELO_CABECERAS_MIN)
    df_modelo.to_excel(nombre_archivo, index=False)
    print(f"✅ Archivo modelo '{nombre_archivo}' creado con las cabeceras necesarias.")


# ========= FUNCIONES MOODLE =========
def call_moodle_ws(function, params):
    params.update(
        {"wstoken": TOKEN, "moodlewsrestformat": "json", "wsfunction": function}
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.post(MOODLE_URL, params=params, headers=headers)
    r.raise_for_status()
    return r.json()


def normalizar_credenciales(codigo):
    """Genera username/password iguales (mínimo 5 caracteres)"""
    username = str(codigo).strip().lower()
    if "." in username:  # evitar casos como "13070.0"
        username = username.split(".")[0]
    # Si el username tiene menos de 5 caracteres, rellenamos con ceros
    if len(username) < 5:
        username = username.ljust(5, "0")
    password = username  # contraseña igual al usuario
    return username, password



def buscar_usuario(username):
    """Busca usuario en Moodle, devuelve id si existe"""
    data = {"field": "username", "values[0]": username}
    resp = call_moodle_ws("core_user_get_users_by_field", data)
    if isinstance(resp, list) and len(resp) > 0 and "id" in resp[0]:
        return resp[0]["id"], resp[0]["firstname"], resp[0]["lastname"]
    return None, None, None


def crear_usuario(
    username, password, firstname, lastname, email=None, codigo="", rol=""
):
    user_id, fn, ln = buscar_usuario(username)
    if user_id:  # Ya existe
        print(f"ℹ Usuario {username} ya existe con ID {user_id}")
        usuarios_creados.append(
            {
                "ID Moodle": user_id,
                "Usuario": username,
                "Contraseña": password,
                "Código": codigo,
                "Nombres": fn,
                "Apellidos": ln,
                "Rol": rol,
            }
        )
        return user_id

    # Crear nuevo usuario
    firstname = firstname if firstname.strip() != "" else "NOMBRE"
    lastname = lastname if lastname.strip() != "" else "APELLIDO"

    data = {
        "users[0][username]": username,
        "users[0][password]": password,
        "users[0][firstname]": firstname,
        "users[0][lastname]": lastname,
        "users[0][email]": (
            email if email and "@" in str(email) else f"{username}@noemail.com"
        ),
    }

    resp = call_moodle_ws("core_user_create_users", data)
    if isinstance(resp, list) and len(resp) > 0 and "id" in resp[0]:
        user_id = resp[0]["id"]
        print(f"✅ Usuario {username} creado con ID {user_id}")

        usuarios_creados.append(
            {
                "ID Moodle": user_id,
                "Usuario": username,
                "Contraseña": password,
                "Código": codigo,
                "Nombres": firstname,
                "Apellidos": lastname,
                "Rol": rol,
            }
        )
        return user_id
    else:
        print(f"❌ Error al crear usuario {username}: {resp}")
        return None


def matricular_usuario(user_id, course_id, role_id):
    data = {
        "enrolments[0][roleid]": role_id,
        "enrolments[0][userid]": user_id,
        "enrolments[0][courseid]": course_id,
    }
    resp = call_moodle_ws("enrol_manual_enrol_users", data)
    if resp in (None, {}):  # Moodle responde vacío si fue exitoso
        print(f"✅ Usuario {user_id} matriculado en curso {course_id}")
        return True
    else:
        print(f"❌ Error al matricular usuario {user_id} en curso {course_id}: {resp}")
        return False


# ========= ROLES MOODLE =========
ROLE_ESTUDIANTE = 5
ROLE_DOCENTE = 3


# ========= UTILIDADES =========
def split_docente(nombre_completo):
    if not isinstance(nombre_completo, str) or nombre_completo.strip() == "":
        return ("", "")
    partes = nombre_completo.strip().split()
    if len(partes) <= 2:
        return (" ".join(partes), "")
    apellidos = " ".join(partes[:2])
    nombres = " ".join(partes[2:])
    return (apellidos, nombres)


# ========= PROCESO PRINCIPAL =========
def main():
    respuesta = (
        input(
            "¿Desea generar un archivo modelo con las cabeceras necesarias antes de ejecutar? (S/N): "
        )
        .strip()
        .upper()
    )
    if respuesta == "S":
        if os.path.exists(EXCEL_FILE):
            sobrescribir = (
                input(
                    f"El archivo '{EXCEL_FILE}' ya existe. ¿Desea sobrescribirlo? (S/N): "
                )
                .strip()
                .upper()
            )
            if sobrescribir != "S":
                print("Operación cancelada.")
                return
        crear_archivo_modelo(EXCEL_FILE)
        print("Por favor, complete el archivo modelo y vuelva a ejecutar el programa.")
        return

    df = pd.read_excel(EXCEL_FILE, usecols=MODELO_CABECERAS_MIN)

    for _, row in df.iterrows():
        # --- ESTUDIANTE ---
        username_est, password_est = normalizar_credenciales(row["COD-EST"])
        firstname_est = str(row["NOMBRE-EST"]).strip()
        lastname_est = str(row["APELLIDO-EST"]).strip()
        email_est = row["EMAIL-EST"] if pd.notna(row["EMAIL-EST"]) else None

        user_id_est = crear_usuario(
            username_est,
            password_est,
            firstname_est,
            lastname_est,
            email_est,
            row["COD-EST"],
            "Estudiante",
        )
        if user_id_est:
            if pd.notna(row["MDL_CURSO1_ID"]):
                matricular_usuario(
                    user_id_est, int(row["MDL_CURSO1_ID"]), ROLE_ESTUDIANTE
                )
            if pd.notna(row["MDL_CURSO2_ID"]):
                matricular_usuario(
                    user_id_est, int(row["MDL_CURSO2_ID"]), ROLE_ESTUDIANTE
                )

        # --- DOCENTE 1 ---
        if pd.notna(row.get("DOCENTE1")) and pd.notna(row.get("COD-DOC1")):
            username_doc1, password_doc1 = normalizar_credenciales(row["COD-DOC1"])
            apellido_doc1, nombre_doc1 = split_docente(str(row["DOCENTE1"]).strip())
            user_id_doc1 = crear_usuario(
                username_doc1,
                password_doc1,
                nombre_doc1,
                apellido_doc1,
                None,
                row["COD-DOC1"],
                "Docente",
            )
            if user_id_doc1 and pd.notna(row["MDL_CURSO1_ID"]):
                matricular_usuario(
                    user_id_doc1, int(row["MDL_CURSO1_ID"]), ROLE_DOCENTE
                )

        # --- DOCENTE 2 ---
        if pd.notna(row.get("DOCENTE2")) and pd.notna(row.get("COD-DOC2")):
            username_doc2, password_doc2 = normalizar_credenciales(row["COD-DOC2"])
            apellido_doc2, nombre_doc2 = split_docente(str(row["DOCENTE2"]).strip())
            user_id_doc2 = crear_usuario(
                username_doc2,
                password_doc2,
                nombre_doc2,
                apellido_doc2,
                None,
                row["COD-DOC2"],
                "Docente",
            )
            if user_id_doc2 and pd.notna(row["MDL_CURSO2_ID"]):
                matricular_usuario(
                    user_id_doc2, int(row["MDL_CURSO2_ID"]), ROLE_DOCENTE
                )

    # ===== EXPORTAMOS LOS USUARIOS GENERADOS =====
    if usuarios_creados:
        df_out = pd.DataFrame(usuarios_creados)
        df_out.to_excel(SALIDA_FILE, index=False)
        print(f"✅ Proceso terminado. Usuarios creados/matriculados correctamente.")
        print(f"📂 Archivo generado: {SALIDA_FILE}")
    else:
        print("⚠ No se generaron usuarios nuevos.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
