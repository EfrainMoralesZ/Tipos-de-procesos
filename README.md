# Generador TIPO DE PROCESO

Aplicación para procesar reportes de mercancía y generar archivos de tipo de proceso.

## Archivos Principales

- `Procesos.py` - Aplicación principal (versión optimizada)
- `data_manager.py` - Gestor de datos optimizado
- `item_dialog.py` - Diálogos para nuevos ítems
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
- Carga rápida de datos
- Compatible con PyInstaller

## Uso

### Ejecutar Aplicación
```bash
python Procesos.py
```

### Crear Ejecutable
```bash
pyinstaller build.spec
```

## Dependencias
```bash
pip install pandas openpyxl Pillow
```

## Notas
- Los datos ya están migrados en la carpeta `data/`
- La aplicación usa JSON/Pickle para mejor rendimiento
- Compatible con PyInstaller sin problemas
- Manejo automático de ítems nuevos con interfaz gráfica
