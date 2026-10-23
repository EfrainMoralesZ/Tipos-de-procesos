# Generador TIPO DE PROCESO

Aplicación de escritorio (customtkinter) que procesa reportes de mercancía en Excel, clasifica cada ítem según su norma (ADHERIBLE, COSTURA, CUMPLE, SIN NORMA) y genera el archivo `TIPO DE PROCESO.xlsx`.

## Estructura

```
Tipos-de-procesos/
├── ProcesosV4.py          Punto de entrada: menú principal y procesamiento del reporte
├── Configurar.py          Ventana para seleccionar los Excel base y convertirlos a JSON
├── Editor_Codigos.py      Editor de códigos de cumplimiento (agregar, editar, importar Excel)
├── Reglas.py              Reglas ADHERIBLE/COSTURA, excepciones por descripción y su editor
├── Dashboard.py           Indicadores, archivos procesados y exportación a PDF
├── Estilos.py             Colores, iconos y componentes compartidos de la interfaz
├── Rutas.py               Ubicación de la carpeta de datos (.py y .exe)
├── Formato.py             Exportación de Excel con formato
├── ProcesosV4.spec        Configuración de PyInstaller
├── requierements          Dependencias (pip freeze)
├── img/                   Logo e icono de la app
├── Datos/                 Base local: JSON/Excel de códigos, base general y configuración
├── dist/                  Ejecutable compilado
└── versiones_anteriores/  ProcesosV2/V3 y su spec (solo histórico, no se usan)
```

## Flujo

1. **Configurar**: se eligen los Excel de *códigos de cumplimiento* y *base general*. Se copian a `Datos/` y se convierten a JSON.
2. **Reporte**: se elige un reporte de mercancía. Se cruza con `base_general.json` y `codigos_cumple.json`, se aplican las reglas de normas y se guarda `TIPO DE PROCESO.xlsx`.
3. **Reglas**: edita `reglas.json` (normas adheribles, de costura, válidas y excepciones por palabra en la descripción, p. ej. calcetas o mochilas con NOM-004/NOM-020 → ADHERIBLE). Incluye una pestaña para probar una norma y descripción. Si se borra `reglas.json`, se vuelve a crear con los valores originales.
4. **Editor**: mantiene `codigos_cumple` (Excel y JSON). Al importar un Excel muestra los cambios para revisarlos antes de aplicarlos.
5. **Dashboard**: lee `codigos_cumple.json` y `archivos_procesados.json`, se actualiza solo cada 2 s y exporta un PDF.

`Datos/` se crea junto al script (o junto al `.exe`) y es el punto de intercambio entre ventanas.

## Ejecutar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install pandas openpyxl xlrd customtkinter pillow reportlab matplotlib
python ProcesosV4.py
```

## Compilar

```bash
pyinstaller ProcesosV4.spec
```
