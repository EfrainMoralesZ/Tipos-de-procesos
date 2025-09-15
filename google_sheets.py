import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# ==========================
# CONFIGURACIÓN INICIAL
# ==========================
SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(__file__),
    "GoogleCloud",
    "tiposdeproceso-d429ca0a3040.json"
)

# IDs de tus Google Sheets
SHEET_ID_CODIGOS = "1_85Ze5kfCREAdI5oglAq4tTWaxwwcfNJwBJ8fc9Nm0Q"
SHEET_ID_ARCHIVOS = "1Hfa6mR8eLL-lcbmz0zTYOzZwzZdMH55nLDtDa3PDm3k"

# ==========================
# CONEXIÓN
# ==========================
def conectar_sheets(service_account_json=SERVICE_ACCOUNT_FILE):
    """
    Conecta con la API de Google Sheets y devuelve el cliente autorizado.
    """
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_json, scope)
    client = gspread.authorize(creds)
    return client


def abrir_hoja_por_id(client, sheet_id):
    """
    Abre la primera hoja de un Google Sheet usando su ID.
    """
    return client.open_by_key(sheet_id).sheet1


# ==========================
# FUNCIONES
# ==========================
def registrar_archivo(sheet_archivos, nombre_archivo, usuario, estado="Procesado"):
    """
    Registra un archivo procesado en la hoja ARCHIVOS PROCESADOS,
    evitando duplicados por nombre.
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registros = sheet_archivos.get_all_records()
    
    if any(r.get("nombre") == nombre_archivo for r in registros):
        print(f"ℹ️ Archivo ya registrado: {nombre_archivo}")
        return
    
    fila = [nombre_archivo, fecha, usuario, estado]
    sheet_archivos.append_row(fila)
    print(f"✅ Archivo registrado correctamente: {nombre_archivo}")


def obtener_codigos(sheet_codigos):
    """
    Devuelve los registros de CODIGOS INSPECCIONADOS como DataFrame.
    """
    return pd.DataFrame(sheet_codigos.get_all_records())


# ==========================
# EJEMPLO DE USO
# ==========================
if __name__ == "__main__":
    client = conectar_sheets()

    # Conectar a cada hoja
    sheet_codigos = abrir_hoja_por_id(client, SHEET_ID_CODIGOS)
    sheet_archivos = abrir_hoja_por_id(client, SHEET_ID_ARCHIVOS)

    # Ejemplo: registrar archivo en historial
    registrar_archivo(sheet_archivos, "ArchivoPrueba.xlsx", "Usuario1")

    # Ejemplo: obtener todos los códigos inspeccionados
    df_codigos = obtener_codigos(sheet_codigos)
    print(df_codigos.head())
