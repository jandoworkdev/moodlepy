# Importar pandas
import pandas as pd

# Leer el archivo Excel
input_file = 'Programacion Agosto.xlsx'
df = pd.read_excel(input_file)

# Columnas a omitir para la comparación de duplicados
omit_cols = [
	'COD-EST', 'APELLIDO-EST', 'NOMBRE-EST', 'EMAIL-EST',
	'COD-DOC1', 'DOCENTE1', 'COD-DOC2', 'DOCENTE2'
]

# Columnas a usar para identificar duplicados
cols_to_check = [col for col in df.columns if col not in omit_cols]

# Eliminar duplicados
df_no_duplicates = df.drop_duplicates(subset=cols_to_check)

# Eliminar columnas de estudiantes y docentes
cols_to_drop = [
	'COD-EST', 'APELLIDO-EST', 'NOMBRE-EST', 'EMAIL-EST',
	'COD-DOC1', 'DOCENTE1', 'COD-DOC2', 'DOCENTE2'
]
df_final = df_no_duplicates.drop(columns=cols_to_drop, errors='ignore')

# Diccionario de especialidades
especialidad_dict = {
	'ENFERMERÍA TÉCNICA': 'ENT',
	'PRÓTESIS DENTAL': 'PRD',
	'LABORATORIO CLÍNICO Y ANATOMÍA PATOLÓGICA': 'LCA',
	'FISIOTERAPIA Y REHABILITACIÓN': 'FIR',
	'FARMACIA TÉCNICA': 'FAT',
}

# Insertar columna ESPC_ID a la derecha de ESPECIALIDAD
if 'ESPECIALIDAD' in df_final.columns:
	idx = df_final.columns.get_loc('ESPECIALIDAD')
	# Si idx es un entero, úsalo; si es un slice, usa el inicio; si es otra cosa, fallback
	if isinstance(idx, int):
		insert_idx = idx + 1
	elif isinstance(idx, slice):
		insert_idx = idx.start + 1 if idx.start is not None else 1
	else:
		insert_idx = 1
	df_final.insert(insert_idx, 'ESPC_ID', df_final['ESPECIALIDAD'].map(especialidad_dict))
else:
	df_final['ESPC_ID'] = ''

# Guardar el resultado en un nuevo archivo Excel
output_file = 'Programacion_Agosto_sin_duplicados.xlsx'
df_final.to_excel(output_file, index=False)

print(f"Archivo sin duplicados y columnas procesadas guardado en: {output_file}")
