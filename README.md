# Generador TIPO DE PROCESO

Aplicación para procesar reportes de mercancía y generar archivos de tipo de proceso.

## Archivos Principales

- `ProcesosV4.py` - Aplicación principal (versión recomendada)
- `data_manager.py` - Gestor de datos optimizado
- `item_dialog.py` - Diálogos para nuevos ítems
- `database_manager_dialog.py` - Gestor de exportación/importación de bases de datos
- `data/` - Carpeta con datos migrados (JSON/Pickle)

## Funcionalidades

### ✅ Procesamiento de Reportes
- Carga reportes de Excel (.xlsx)
- Procesa automáticamente ítems existentes
- Genera archivos de tipo de proceso

### ✅ Gestión de Nuevos Ítems
- **Detección automática** de ítems nuevos
- **Diálogo interactivo** para agregar información
- **Procesamiento en lote** para múltiples ítems
- **Validación de campos** requeridos

### ✅ Base de Datos Optimizada
- Almacenamiento en JSON/Pickle
````markdown
# Generador TIPO DE PROCESO

Aplicación para procesar reportes de mercancía y generar archivos de tipo de proceso.

## Visión general — Qué hace esta aplicación

Esta aplicación facilita el procesamiento de reportes (por ejemplo, archivos Excel) para identificar ítems, clasificarlos según reglas definidas y generar los archivos de "tipo de proceso" correspondientes. Soporta detección y manejo interactivo de ítems nuevos y está preparada para ser distribuida como ejecutable (PyInstaller).

> Nota: el proyecto contiene varias versiones (`ProcesosV2.py`, `ProcesosV3.py`, `ProcesosV4.py`) y un posible `Procesos.py` como punto de entrada; usar la versión apropiada según la rama/versión que se desee ejecutar.

## Componentes principales

- `ProcesosV4.py`: punto de entrada recomendado de la aplicación (interfaz de usuario y flujo principal). Otras versiones (`Procesos.py`, `ProcesosV2.py`, `ProcesosV3.py`) se mantienen para referencia o pruebas.
- `data_manager.py`: carga, parseo y manipulación de datos (Excel ↔ JSON/Pickle).
- `item_dialog.py`: diálogo/ventana para crear o editar información de ítems nuevos.
- `database_manager_dialog.py`: import/export de bases de datos y gestión de persistencia.
- `Editor_Codigos.py`: interfaz para editar códigos o metadatos de ítems.
- `Dashboard.py`: vistas y reportes para el usuario (resumen, resultados, estado).
- `google_sheets.py`: utilidades para sincronizar/exportar datos a Google Sheets (si está configurado).
- `Datos/` (o `Datos` en la raíz / `Datos/` en el repo): carpeta compartida con archivos JSON que actúan como base de datos local y punto de comunicación entre componentes cuando se usan ejecutables.

Archivos de datos de ejemplo (en `Datos/`):
- `base_general.json`
- `archivos_procesados.json`
- `codigos_cumple.json`
- `config.json`

## Flujo de datos y diagrama (descripción)

1. El usuario inicia la aplicación (por ejemplo `ProcesosV4.py`).
2. Se carga un reporte de Excel (.xlsx) desde la interfaz.
3. `data_manager.py` lee el Excel (usando pandas/openpyxl) y convierte las filas en registros internos.
4. Para cada ítem del reporte, la aplicación comprueba si existe en la base local (`base_general.json`).
	 - Si el ítem existe: se procesa automáticamente según las reglas y plantillas definidas.
	 - Si el ítem es nuevo: se lanza `item_dialog.py` para solicitar datos faltantes (o en modo batch, acumula y muestra un diálogo de edición masiva).
5. El `Editor_Codigos.py` permite al usuario completar o modificar códigos/metadatos necesarios.
6. Una vez validados, los ítems se transforman en archivos/registro de tipo de proceso y se guardan en `Datos/` (o exportan a Excel/JSON/Pickle según configuración).
7. `Dashboard.py` muestra resúmenes, estadísticas y permite exportar/importar mediante `database_manager_dialog.py`.
8. Opcional: sincronización con Google Sheets mediante `google_sheets.py`.

Diagrama textual simplificado (componentes y flechas):

Usuario -> [Interfaz Procesos] -> data_manager.py -> (compara) base_general.json
																				|-> item_dialog.py (si es nuevo) -> Editor_Codigos
																				|-> Generación archivos tipo_proceso -> Datos/ (JSON/Pickle/Excel)
Dashboard <-> Datos/ (resúmenes, import/export)

## Contrato mínimo (inputs / outputs / errores)

- Inputs:
	- Archivos Excel (.xlsx) con reportes de mercancía
	- Ediciones manuales desde diálogos (ítems nuevos)
- Outputs:
	- Archivos de "tipo de proceso" (JSON/Excel/Pickle), reportes procesados
	- Bases actualizadas en `Datos/` (`base_general.json`, etc.)
- Errores / modos de fallo comunes:
	- Formato Excel inválido (columnas faltantes) -> se muestra error al cargar
	- Campos obligatorios vacíos en ítems nuevos -> se valida en `item_dialog` antes de guardar
	- Permisos de archivo (sin escritura en `Datos/`) -> fallo al exportar

## Casos borde a considerar

- Reportes masivos: procesar en lotes para evitar bloqueos de UI.
- Filas con datos inconsistentes: marcar y listar para revisión manual.
- Conflictos al empaquetar con PyInstaller: asegurar incluir archivos JSON en el bundle y usar rutas relativas/absolutas correctas.

## Cómo ejecutar (local, desarrollo)

1. Crear/activar entorno virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate  # zsh
```

2. Instalar dependencias:

```bash
pip install -r requierements || pip install pandas openpyxl Pillow
```

3. Ejecutar la aplicación (versión recomendada `ProcesosV4.py`):

```bash
python ProcesosV4.py
```

4. Para crear un ejecutable (PyInstaller):

```bash
pyinstaller ProcesosV4.spec
```

## Estructura de carpetas (clave)

- `Datos/` — Base de datos local y archivos de comunicación entre módulos y .exe
- `archivos/` — (posible) salidas y recursos
- `build/` — artefactos generados por PyInstaller
- `*.spec` — archivos de especificación para PyInstaller

## Notas importantes sobre empaquetado y comunicación

La carpeta `Datos/` (a veces nombrada `Datos` o `data`) actúa como punto de intercambio entre `Editor_Codigos` y `Dashboard` cuando la aplicación está empaquetada como `.exe`. Asegúrate de que los archivos JSON necesarios estén incluidos en el bundle de PyInstaller y de que las rutas a esos archivos sean resueltas correctamente tanto en modo desarrollo (python) como en ejecutable.

## Dependencias

- pandas
- openpyxl
- Pillow

Instalación mínima:

```bash
pip install pandas openpyxl Pillow
```

## Sugerencias de mantenimiento y siguientes pasos

- Añadir tests unitarios para `data_manager.py` (parser y normalización de filas).
- Añadir un pequeño script de integración que ejecute un flujo corto (carga -> procesado -> export) como prueba automatizada.
- Documentar las columnas esperadas en los Excel de entrada para evitar errores de formato.

---

Actualizado: explicación del flujo y notas para desarrolladores/usuarios que quieran entender cómo funciona la aplicación y cómo empaquetarla.
````