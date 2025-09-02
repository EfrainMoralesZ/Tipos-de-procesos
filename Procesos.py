import os
import pandas as pd
import matplotlib.pyplot as plt

# Archivos
ARCHIVO_CODIGOS = os.path.join("resources", "codigos_cumple.json")  # Archivo con OBSERVACION
HISTORIAL = os.path.join("resources", "historial.xlsx")             # Archivo con códigos ingresados/procesados

def obtener_stats():
    stats = {}

    # Verificar existencia del archivo de códigos
    if os.path.exists(ARCHIVO_CODIGOS):
        df_codigos = pd.read_excel(ARCHIVO_CODIGOS)

        # Total de códigos (suma de todos los ITEMS)
        if 'ITEM' in df_codigos.columns:
            stats['total_codigos'] = df_codigos['ITEM'].sum()
        else:
            stats['total_codigos'] = 0

        # Códigos que cumplen (suma de ITEMS con OBSERVACION == "CUMPLE")
        if 'OBSERVACION' in df_codigos.columns and 'ITEM' in df_codigos.columns:
            stats['codigos_cumple'] = df_codigos[df_codigos['OBSERVACION'] == "CUMPLE"]['ITEM'].sum()
        else:
            stats['codigos_cumple'] = 0

        # Códigos que no cumplen
        stats['codigos_no_cumple'] = stats['total_codigos'] - stats['codigos_cumple']
    else:
        stats['total_codigos'] = 0
        stats['codigos_cumple'] = 0
        stats['codigos_no_cumple'] = 0

    # Códigos ingresados / procesados desde historial
    if os.path.exists(HISTORIAL):
        df_hist = pd.read_excel(HISTORIAL)
        stats['codigos_ingresados'] = len(df_hist)
    else:
        stats['codigos_ingresados'] = 0

    return stats

# Obtener estadísticas
stats = obtener_stats()
print("Estadísticas:", stats)

# Crear gráfica
categorias = ['Total códigos', 'Códigos que cumplen', 'Códigos no cumplen', 'Códigos ingresados']
valores = [stats['total_codigos'], stats['codigos_cumple'], stats['codigos_no_cumple'], stats['codigos_ingresados']]

plt.figure(figsize=(10,6))
plt.bar(categorias, valores, color=['#ecd925', '#4d4d4d', '#282828', '#d8d8d8'])
plt.title("Resumen de Códigos")
plt.ylabel("Cantidad de ITEMS")
for i, v in enumerate(valores):
    plt.text(i, v + 2, str(v), ha='center', fontweight='bold')
plt.show()
