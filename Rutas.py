import os
import sys

# Detectar si corre en .exe (PyInstaller) o en desarrollo
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# === Función universal para recursos ===
def recurso_path(ruta_relativa):
    """Devuelve la ruta absoluta de un recurso dentro de datos/ o img/"""
    return os.path.join(BASE_PATH, ruta_relativa)

# === Función para archivos de datos ===
def archivo_datos(nombre_archivo):
    """Acceso directo a la carpeta datos"""
    datos_path = os.path.join(BASE_PATH, "datos")
    os.makedirs(datos_path, exist_ok=True)
    return os.path.join(datos_path, nombre_archivo)
