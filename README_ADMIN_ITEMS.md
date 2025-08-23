# 🏢 Administrador de Ítems - BASE DECATHLON GENERAL

## 🎯 Descripción

El **Administrador de Ítems** es una nueva funcionalidad integrada en la aplicación que permite gestionar, editar y administrar todos los ítems del archivo **BASE DECATHLON GENERAL**.

## ✨ Características Principales

### **📊 Gestión Completa de Base de Datos**
- **63,026 ítems** gestionables
- **31 campos** por ítem
- **Navegación intuitiva** entre ítems
- **Búsqueda avanzada** por EAN o descripción

### **🔍 Campos Editables con Menús Desplegables**
- **NORMA**: NOM-004, NOM-015, NOM-020, NOM-024, NOM-050, NOM-141, SIN NORMA
- **CODIGO FORMATO**: NOM004, NOM004TEXX, NOM015, NOM020, NOM020INS, NOM024, NOM050, NOM141
- **TIPO DE ETIQUETA**: A, B, C, D
- **CLIENTE**: DECATHLON, OTRO
- **LOGO NOM**: 0, 1
- **LISTA**: PZA, KG, L, M, M2
- **PAIS DE PROCEDENCIA**: CHINA, VIETNAM, FRANCIA, COLOMBIA, MEXICO, OTRO

### **📋 Campos de Solo Lectura**
- EAN, DESCRIPTION, MODEL CODE, MARCA, CUIDADO
- CARACTERISTICAS, MEDIDAS, CONTENIDO, MAGNITUD
- DENOMINACION, LEYENDAS, EDAD, INSUMOS, FORRO
- TALLA, PAIS ORIGEN, IMPORTADOR, ITEM ESPAÑOL
- TYPE OF GOODS, HS CODE

## 🚀 Cómo Usar

### **1. Acceder al Administrador**
1. Ejecuta la aplicación principal: `py Procesos.py`
2. Haz clic en **"🏢 Administrar Ítems Base"**
3. Se abrirá la ventana de administración

### **2. Cargar Archivo Base**
- **Si ya está configurado**: El archivo se carga automáticamente
- **Si no está configurado**: Se solicita seleccionar el archivo BASE DECATHLON GENERAL

### **3. Navegar por los Ítems**
- **◀ Anterior**: Navega al ítem anterior
- **Siguiente ▶**: Navega al ítem siguiente
- **Indicador**: Muestra posición actual (ej: 1 / 63,026)

### **4. Buscar Ítems Específicos**
- **Por EAN**: Ingresa el número EAN del ítem
- **Por descripción**: Escribe parte de la descripción
- **Enter**: Presiona Enter o haz clic en "🔍 Buscar"

### **5. Editar Campos**
- **Campos editables**: Usa los menús desplegables para cambiar valores
- **Campos de solo lectura**: Se muestran para información pero no se pueden modificar

### **6. Guardar y Exportar**
- **💾 Guardar Cambios**: Guarda modificaciones en memoria
- **📤 Exportar Base**: Exporta la base completa modificada (Excel o JSON)

## 🎨 Interfaz de Usuario

### **Ventana Principal**
- **Tamaño**: 1200x800 píxeles
- **Diseño**: Moderno y responsive
- **Colores**: Esquema profesional con botones coloridos

### **Organización de Campos**
- **Panel izquierdo**: Información del ítem (campos de solo lectura)
- **Panel derecho**: Campos editables con menús desplegables
- **Panel superior**: Controles de navegación y búsqueda
- **Panel inferior**: Botones de acción

### **Estados Visuales**
- **✅ Verde**: Archivo cargado, operaciones exitosas
- **⚠️ Naranja**: Advertencias, archivo no cargado
- **🔵 Azul**: Botones de navegación
- **🟠 Naranja**: Botón de búsqueda

## 🔧 Funcionalidades Técnicas

### **Detección Inteligente de Archivos**
```python
# Si ya está configurado, usa la ruta existente
if hasattr(self.parent, 'BASE_GENERAL_PATH') and self.parent.BASE_GENERAL_PATH:
    ruta_archivo = self.parent.BASE_GENERAL_PATH
else:
    # Solicita nueva ruta
    ruta_archivo = filedialog.askopenfilename(...)
```

### **Gestión de Memoria**
- **Carga eficiente**: Solo carga los datos necesarios
- **Navegación rápida**: Cambio instantáneo entre ítems
- **Búsqueda optimizada**: Algoritmos eficientes de búsqueda

### **Validación de Datos**
- **Campos requeridos**: Verificación de integridad
- **Formato de datos**: Validación de tipos y valores
- **Manejo de errores**: Mensajes claros y útiles

## 📁 Estructura de Archivos

### **Archivos Principales**
- `admin_items.py` - Módulo principal de administración
- `Procesos.py` - Aplicación principal (integración agregada)
- `Formato.py` - Gestión de formato de Excel

### **Dependencias**
- `pandas` - Manejo de datos
- `tkinter` - Interfaz gráfica
- `openpyxl` - Exportación a Excel
- `json` - Manejo de archivos JSON

## 🧪 Pruebas y Verificación

### **Script de Pruebas**
```bash
py test_admin.py
```

### **Pruebas Incluidas**
- ✅ Importación del módulo
- ✅ Estructura de archivos
- ✅ Integración en Procesos.py
- ✅ Accesibilidad del archivo base

## 💡 Casos de Uso

### **Para Administradores**
- **Actualización masiva** de normas y códigos
- **Corrección de datos** incorrectos
- **Mantenimiento** de la base de datos
- **Auditoría** de información

### **Para Usuarios Técnicos**
- **Verificación** de datos
- **Búsqueda rápida** de ítems específicos
- **Exportación** de datos para análisis
- **Respaldo** de información

### **Para Operaciones**
- **Consulta rápida** de especificaciones
- **Verificación** de códigos de formato
- **Validación** de normas aplicables
- **Trazabilidad** de cambios

## 🔒 Seguridad y Validación

### **Protección de Datos**
- **Campos de solo lectura**: Previene modificación accidental
- **Validación de entrada**: Verifica formatos correctos
- **Confirmación de cambios**: Mensajes claros de operaciones

### **Manejo de Errores**
- **Try-catch**: Captura y maneja errores gracefully
- **Mensajes informativos**: Explica problemas claramente
- **Recuperación**: Permite continuar operación después de errores

## 🚀 Próximas Mejoras

### **Funcionalidades Planificadas**
- **Edición en lote**: Modificar múltiples ítems simultáneamente
- **Filtros avanzados**: Búsqueda por múltiples criterios
- **Historial de cambios**: Registro de modificaciones realizadas
- **Respaldo automático**: Copias de seguridad automáticas

### **Optimizaciones Técnicas**
- **Carga lazy**: Carga de datos bajo demanda
- **Cache inteligente**: Almacenamiento en memoria optimizado
- **Búsqueda indexada**: Algoritmos de búsqueda más rápidos

## 📞 Soporte y Ayuda

### **Solución de Problemas Comunes**
- **Error de carga**: Verificar que el archivo esté accesible
- **Búsqueda sin resultados**: Verificar ortografía y formato
- **Error de guardado**: Verificar permisos de escritura

### **Contacto**
- **Documentación**: Revisar este README
- **Pruebas**: Ejecutar `test_admin.py`
- **Logs**: Revisar mensajes de consola

## 🎯 Resumen

El **Administrador de Ítems** es una herramienta poderosa que transforma la gestión de la base de datos DECATHLON GENERAL de un proceso manual a uno automatizado y eficiente. Con su interfaz intuitiva, funcionalidades avanzadas y diseño profesional, permite a los usuarios gestionar **63,026 ítems** de manera fácil y segura.

**¡La funcionalidad está lista para uso en producción!** 🚀
