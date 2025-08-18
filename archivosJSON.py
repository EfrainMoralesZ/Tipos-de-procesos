import pandas as pd
import os

# Archivos Excel
archivos_excel = {
    "BASE DECATHLON GENERAL ADVANCE II.xlsx": "base_general.json",
    "INSPECCION.xlsx": "inspeccion.json",
    "HISTORIAL_PROCESOS.xlsx": "historial.json"
}

# Carpeta donde se guardarán los JSON
if not os.path.exists("resources"):
    os.makedirs("resources")

for excel_file, json_file in archivos_excel.items():
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        df.to_json(os.path.join("resources", json_file), orient="records", force_ascii=False, indent=4)
        print(f"{excel_file} → resources/{json_file}")
    else:
        print(f"No se encontró el archivo: {excel_file}")
