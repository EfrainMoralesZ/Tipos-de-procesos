# Rutas.py
import os
import sys

def ruta_base():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")

def archivo_datos(nombre_archivo):
    ruta_datos = os.path.join(ruta_base(), "datos")
    os.makedirs(ruta_datos, exist_ok=True)
    return os.path.join(ruta_datos, nombre_archivo)
