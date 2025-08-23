# Generador TIPO DE PROCESO

Aplicación para procesar reportes de mercancía y generar archivos de tipo de proceso.

## 🆕 Nueva Funcionalidad - Selección Dinámica de Archivos

**La aplicación ahora permite al usuario seleccionar dinámicamente los archivos base necesarios, eliminando la dependencia de rutas fijas codificadas.**

### ✅ Ventajas de la Nueva Implementación

- **Flexibilidad total**: Los archivos pueden estar en cualquier ubicación del sistema
- **Independencia de rutas**: No más errores por archivos movidos o renombrados
- **Interfaz intuitiva**: Botón dedicado para configurar archivos base
- **Validación automática**: Verifica que todos los archivos estén configurados antes de procesar
- **Estado visual**: Indicador claro del estado de configuración de archivos

## Archivos Principales

- `Procesos.py` - Aplicación principal (versión optimizada con selección dinámica)
- `Formato.py` - Gestor de formato de Excel
- `archivosJSON.py` - Conversor de archivos Excel a JSON
- `resources/` - Carpeta con datos migrados (JSON)

## Funcionalidades

### ✅ Procesamiento de Reportes
- Carga reportes de Excel (.xlsx)
- Procesa automáticamente ítems existentes
- Genera archivos de tipo de proceso

### ✅ Gestión de Archivos Base
- **Selección dinámica** de archivos base necesarios
- **Configuración flexible** de ubicaciones
- **Validación automática** de archivos requeridos
- **Interfaz intuitiva** para gestión de archivos

### ✅ Gestión de Nuevos Ítems
- **Detección automática** de ítems nuevos
- **Procesamiento en lote** para múltiples ítems
- **Validación de campos** requeridos

### ✅ Base de Datos Optimizada
- Almacenamiento en JSON para mejor rendimiento
- Carga rápida de datos
- Compatible con PyInstaller
- Exportación/importación a Excel
- Gestión completa de bases de datos

## 🚀 Uso de la Aplicación

### 1. Configurar Archivos Base (NUEVO)
**IMPORTANTE**: Antes de procesar cualquier reporte, debes configurar los archivos base:

1. Ejecuta la aplicación
2. Haz clic en **"⚙️ Configurar Archivos Base"**
3. Selecciona los tres archivos necesarios:
   - **BASE GENERAL**: `BASE DECATHLON GENERAL ADVANCE II.xlsx`
   - **INSPECCIÓN**: `codigos_cumple.xlsx`
   - **HISTORIAL**: `HISTORIAL_PROCESOS.xlsx`

### 2. Procesar Reportes
Una vez configurados los archivos base:
1. Haz clic en **"📂 Subir REPORTE DE MERCANCIA"**
2. Selecciona tu archivo de reporte
3. La aplicación procesará automáticamente los datos
4. Guarda el archivo resultante donde desees

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

## 📁 Estructura de Archivos Requeridos

### Archivos Base (Seleccionados por el usuario)
- **BASE GENERAL**: Contiene códigos EAN y tipos de proceso
- **INSPECCIÓN**: Define criterios de cumplimiento
- **HISTORIAL**: Registro de procesos realizados

### Archivos de Datos (Automáticos)
- `resources/base_general.json` - Datos base convertidos
- `resources/codigos_cumple.json` - Códigos de cumplimiento
- `resources/historial.json` - Historial de procesos

## 🔧 Solución de Problemas

### Error: "Archivos base no configurados"
**Solución**: Usa el botón "⚙️ Configurar Archivos Base" para seleccionar los archivos necesarios.

### Error: "No se encontró el archivo JSON"
**Solución**: Ejecuta `archivosJSON.py` para convertir los archivos Excel a JSON.

### Los archivos pueden estar en cualquier ubicación
Ya no es necesario mantener los archivos en la carpeta `archivos/` específica.

## Notas
- **Los datos ya están migrados** en la carpeta `resources/`
- La aplicación usa **JSON para mejor rendimiento**
- **Compatible con PyInstaller** sin problemas
- **Manejo automático** de ítems nuevos con interfaz gráfica
- **Configuración flexible** de archivos base
