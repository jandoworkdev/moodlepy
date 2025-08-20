import requests
import pandas as pd

# ========= CONFIG =========
MOODLE_URL = "https://institutoloayzapresencial.edu.pe/TESTUAL/webservice/rest/server.php"
TOKEN = "218d0d11240cf17a7d78abb90e6b6caa"

# ========= FUNCIONES =========
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

def obtener_categoria_por_id(category_id):
    params = {"criteria[0][key]": "id", "criteria[0][value]": category_id}
    categorias = call_moodle_ws("core_course_get_categories", params)
    if categorias:
        return categorias[0]
    return None

def obtener_orden_categoria(category_id):
    cat = obtener_categoria_por_id(category_id)
    if not cat:
        print(f"❌ No se encontró la categoría con ID {category_id}")
        return
    parent_id = cat["parent"]
    # Obtener todas las subcategorías del padre
    subcats = call_moodle_ws("core_course_get_categories", {"criteria[0][key]": "parent", "criteria[0][value]": parent_id})
    # Ordenar por sortorder (como en la interfaz de Moodle)
    ordenadas = sorted(subcats, key=lambda x: x.get("sortorder", 0))
    data = []
    pos_categoria = None
    for idx, c in enumerate(ordenadas, 1):
        data.append({
            "POSICION": idx,
            "ID": c["id"],
            "NOMBRE": c["name"],
            "PARENT_ID": c["parent"],
            "TOTAL_SUBCATEGORIAS": len(ordenadas),
            "SORTORDER": c.get("sortorder", "")
        })
        if c["id"] == category_id:
            pos_categoria = idx
    df = pd.DataFrame(data)
    if pos_categoria:
        print(f"\nCategoría buscada (ID: {category_id}) está en la posición {pos_categoria} entre {len(ordenadas)} subcategorías de su padre (ID: {parent_id}), ordenadas por SORTORDER (como en la interfaz de Moodle):\n")
    else:
        print(f"\n❌ No se encontró la categoría con ID {category_id} entre las subcategorías de su padre.\n")
    print(df.to_string(index=False))


    # Preguntar si desea ordenar todas las subcategorías por nombre ascendente
    if pos_categoria:
        ordenar = input("¿Desea ordenar todas las subcategorías por NOMBRE ascendente? (S/N): ").strip().upper()
        if ordenar == "S":
            try:
                ordenar_subcategorias_por_nombre(parent_id)
            except Exception as e:
                print(f"Error: {e}")


def ordenar_subcategorias_por_nombre(parent_id):
    # Obtener subcategorías del padre
    subcats = call_moodle_ws("core_course_get_categories", {"criteria[0][key]": "parent", "criteria[0][value]": parent_id})
    # Ordenar por nombre ascendente
    ordenadas = sorted(subcats, key=lambda x: str(x.get("name", "")).lower())
    # Asignar sortorder en múltiplos de 1000 y enviar id, parent, name
    params = {}
    for i, c in enumerate(ordenadas):
        params[f"categories[{i}][id]"] = c["id"]
        params[f"categories[{i}][sortorder]"] = (i + 1) * 1000
        params[f"categories[{i}][parent]"] = c["parent"]
        params[f"categories[{i}][name]"] = c["name"]
    resp = call_moodle_ws("core_course_update_categories", params)
    if isinstance(resp, list):
        print(f"✅ Orden actualizado correctamente para las subcategorías de {parent_id}.")
        # Recursivo: ordenar subcategorías de cada subcategoría
        for c in ordenadas:
            ordenar_subcategorias_por_nombre(c["id"])
    else:
        print(f"❌ Error al actualizar el orden: {resp}")

def main():
    category_id = input("Ingrese el ID de la categoría: ").strip()
    if not category_id.isdigit():
        print("ID inválido.")
        return
    obtener_orden_categoria(int(category_id))

if __name__ == "__main__":
    main()
