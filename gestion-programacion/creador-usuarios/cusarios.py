import pandas as pd

# Archivo Excel
excel_file = "carga-moodle.xlsx"

# Leemos las hojas
df_carga = pd.read_excel(excel_file, sheet_name=0)  # Hoja 1
df_dicc  = pd.read_excel(excel_file, sheet_name=1)  # Hoja 2 (diccionario)

# Claves en común
keys = ["ESPC_ID", "SEDE", "CICLO1", "CURSO1", "CURSO2"]

# --- Merge para CURSO1_ID ---
df_carga = df_carga.merge(
    df_dicc[keys + ["CURSO1_ID"]],  # tomamos las claves + la columna de IDs
    how="left",
    on=keys
)

# --- Merge para CURSO2_ID ---
df_carga = df_carga.merge(
    df_dicc[keys + ["CURSO2_ID"]],
    how="left",
    on=keys
)

# Guardamos resultado
df_carga.to_excel("carga_moodle_con_ids.xlsx", index=False)
print("✅ IDs asignados y guardados en carga_moodle_con_ids.xlsx")
