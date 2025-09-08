import os
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sys
import json
from Editor_Codigos import EditorCodigos
from Formato import exportar_excel
import re
import time
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.utils import ImageReader
import subprocess

# Configuración de rutas para .py y .exe
if getattr(sys, 'frozen', False):
    # Cuando está compilado en .exe
    BASE_PATH = sys._MEIPASS
else:
    # Cuando se ejecuta desde Python
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Archivos de configuración
CONFIG_FILE = os.path.join(BASE_PATH, "config.json")
ARCHIVOS_PROCESADOS_FILE = os.path.join(BASE_PATH, "archivos_procesados.json")
CODIGOS_CUMPLE = os.path.join(BASE_PATH, "codigos_cumple.xlsx")
CODIGOS_JSON = os.path.join(BASE_PATH, "codigos_cumple.json")

# Configuración de Rutas
def configurar_rutas():
    """Abre la ventana de configuración de rutas externa"""
    try:
        # Si corres desde exe, busca el script en BASE_PATH
        rutas_py = os.path.join(BASE_PATH, "Rutas.py")
        subprocess.Popen([sys.executable, rutas_py])
    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo abrir la configuración:\n{e}")

# REGISTRAR LOS ARCHIVOS PROCESADOS
# Carpeta donde se guardarán las configuraciones y JSONs
# Carpeta de configuración
CONFIG_DIR = "Guardar Archivos Generados"
os.makedirs(CONFIG_DIR, exist_ok=True)

# Ruta del archivo de procesados
ARCHIVOS_PROCESADOS_FILE = os.path.join(CONFIG_DIR, "archivos_procesados.json")

# Lista global de archivos procesados
archivos_procesados = []

def cargar_archivos_procesados():
    """Carga la lista de archivos procesados, crea el JSON si no existe"""
    global archivos_procesados
    try:
        if os.path.exists(ARCHIVOS_PROCESADOS_FILE):
            with open(ARCHIVOS_PROCESADOS_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                archivos_procesados = datos if isinstance(datos, list) else []
        else:
            archivos_procesados = []
            # Crear archivo vacío
            with open(ARCHIVOS_PROCESADOS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            print(f"📁 Archivo {ARCHIVOS_PROCESADOS_FILE} no encontrado. Se creó uno nuevo.")
    except Exception as e:
        archivos_procesados = []
        print(f"❌ Error cargando archivos procesados: {e}")
    return archivos_procesados

def registrar_archivo_procesado(nombre_archivo, fecha_proceso):
    """Registra un archivo procesado en el sistema de estadísticas"""
    try:
        cargar_archivos_procesados()
        
        # Evitar duplicados
        if any(a["nombre"] == nombre_archivo for a in archivos_procesados):
            print(f"ℹ️ Archivo ya registrado: {nombre_archivo}")
            return
        
        # Agregar nuevo archivo
        archivo_info = {
            "nombre": nombre_archivo,
            "fecha_proceso": fecha_proceso,
            "fecha_archivo": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        archivos_procesados.append(archivo_info)
        
        # Guardar cambios en JSON
        with open(ARCHIVOS_PROCESADOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(archivos_procesados, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Archivo registrado correctamente: {nombre_archivo}")
    
    except Exception as e:
        print(f"❌ Error registrando archivo: {e}")

# OBTENER ESTADISTICAS DE ARCHIVOS
def obtener_estadisticas_archivos():
    """Obtiene estadísticas de archivos procesados"""
    try:
        if os.path.exists(ARCHIVOS_PROCESADOS_FILE):
            with open(ARCHIVOS_PROCESADOS_FILE, 'r', encoding='utf-8') as f:
                archivos = json.load(f)
            return {
                "total_archivos": len(archivos),
                "archivos_recientes": archivos[-5:] if len(archivos) > 5 else archivos,
                "ultimo_proceso": archivos[-1]["fecha_proceso"] if archivos else "Ninguno"
            }
        else:
            return {
                "total_archivos": 0,
                "archivos_recientes": [],
                "ultimo_proceso": "Ninguno"
            }
    except Exception as e:
        print(f"[ERROR] Error obteniendo estadísticas: {e}")
        return {
            "total_archivos": 0,
            "archivos_recientes": [],
            "ultimo_proceso": "Error"
        }

# CARGAR CONFIGURACION DE RUTAS
def cargar_configuracion():
    """Carga la configuración desde el archivo JSON"""
    CONFIG_DIR = "Guardar Configuracion"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"rutas": {"base_general": "", "codigos_cumple": ""}}
    except Exception as e:
        print(f"Error al cargar configuración: {str(e)}")
        return {"rutas": {"base_general": "", "codigos_cumple": ""}}

# FUNCION PARA ACTUALIZAR CODIGOS 
def abrir_editor_codigos(parent):
    """Abre el editor de códigos"""
    # Cargar la configuración para obtener las rutas
    config = cargar_configuracion()
    
    if not config:
        messagebox.showerror("Error", "No se pudo cargar la configuración")
        return
    
    rutas = config.get("rutas", {})
    ARCHIVO_CODIGOS = rutas.get("codigos_cumple", "")
    ARCHIVO_JSON = rutas.get("codigos_cumple", "").replace(".xlsx", ".json").replace(".xls", ".json")
    
    if ARCHIVO_CODIGOS and ARCHIVO_JSON:
        editor = EditorCodigos(parent, ARCHIVO_CODIGOS, ARCHIVO_JSON)
        return editor
    else:
        messagebox.showwarning("Advertencia", "Primero debe configurar los archivos en Configuración de Rutas")
        return None

#  FUNCION PARA GENERAR EL TIPO DE REPORTE 
def procesar_reporte(reporte_path):
    global frame

    # REGISTRAR ARCHIVO PROCESADO
    nombre_archivo = os.path.basename(reporte_path)
    fecha_proceso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Agregar a estadísticas de archivos procesados
    registrar_archivo_procesado(nombre_archivo, fecha_proceso)

    # SE CREA LA BARRA DE PROGRESO EN EL FRAME PRINCIPAL (LADO DERECHO)
    try:
        global progress_label, progress_var, progress_bar, percent_label
        # Inicializar variables globales si no existen
        if 'progress_label' not in globals():
            progress_label = None
        if 'progress_bar' not in globals():
            progress_bar = None
        if 'percent_label' not in globals():
            percent_label = None
            
        try:
            # Limpiar widgets existentes si existen
            for widget_name in ['progress_label', 'progress_bar', 'percent_label']:
                if widget_name in globals():
                    widget = globals()[widget_name]
                    if widget is not None and hasattr(widget, 'destroy'):
                        try:
                            widget.destroy()
                        except:
                            pass
        except Exception:
            pass

        # Etiqueta de texto
        progress_label = tk.Label(frame, text="Procesando...", font=("Segoe UI", 9, "bold"), bg="#FFFFFF")
        progress_label.place(relx=1.0, rely=1.0, x=-20, y=-80, anchor="se")  # Separación superior

        # Barra de progreso
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100, length=220)  # Más pequeña
        progress_bar.place(relx=1.0, rely=1.0, x=-20, y=-50, anchor="se")  # Debajo de la etiqueta

        # Porcentaje
        percent_label = tk.Label(frame, text="0%", font=("Segoe UI", 10, "bold"), bg="#FFFFFF")
        percent_label.place(relx=1.0, rely=1.0, x=-20, y=-25, anchor="se")  # Debajo de la barra

        frame.update()

        # LECTURA DE DATOS DE LOS ARCHIVOS DE EXCEL CONVERTIDOS EN JSON
        def cargar_json(nombre_json):
            """
            Carga un archivo JSON como DataFrame de pandas.
            Funciona tanto en Python normal como en .exe creado con PyInstaller.
            """
            if getattr(sys, "frozen", False):
                # Cuando se ejecuta como .exe
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
            else:
                # Cuando se ejecuta como script normal
                base_path = os.path.dirname(__file__)
            
            ruta = os.path.join(base_path, "resources", nombre_json)
            
            if not os.path.exists(ruta):
                raise FileNotFoundError(f"No se encontró el archivo JSON: {ruta}")
            
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return pd.DataFrame(data)

        # LEER ARCHIVOS BASE EN FORMATO JSON
        df_base = cargar_json("base_general.json")
        df_codigos_cumple = cargar_json("codigos_cumple.json")
        df_reporte = pd.read_excel(reporte_path)  # El reporte sigue siendo cargado por el usuario

        # --- Detectar tipo de reporte y columnas ---
        if 'Número de Parte' in df_reporte.columns:
            # Reporte FH
            num_parte_col = 'Número de Parte'
            desc_col = 'Desc. Pedimento'
            norma_col = 'Normas'
            criterio_col = 'CRITERIO'   # FH usa CRITERIO
        elif any(col.strip().lower() in ['num. parte', 'num.parte', 'numero de parte'] for col in df_reporte.columns):
            # Reporte MIMPO
            for col in df_reporte.columns:
                if col.strip().lower() in ['num. parte', 'num.parte', 'numero de parte']:
                    num_parte_col = col
                    break
            for col in df_reporte.columns:
                if col.strip().lower() == 'descripción agente aduanal':
                    desc_col = col
                    break
            norma_col = 'NOMs'
            criterio_col = 'CRITERIO'
        else:
            raise ValueError("No se encontró ninguna columna de NUM. PARTE válida en el reporte")
        
        # --- Armado de columnas del archivo TIPO DE PROCESO ---
        items_series = pd.to_numeric(df_reporte[num_parte_col], errors='coerce')
        # Filtrar valores no nulos manualmente
        items_list = []
        # Simplificar el procesamiento de items
        try:
            # Usar método más simple y directo
            items_list = []
            # Simplificar completamente el procesamiento
            try:
                # Usar método más simple - verificar si es iterable
                if hasattr(items_series, '__iter__') and not isinstance(items_series, (str, bytes)):
                    items_series_list = list(items_series)
                else:
                    items_series_list = []
            except:
                items_series_list = []
            # Verificar que sea iterable
            if not isinstance(items_series_list, (list, tuple)):
                items_series_list = []
            for val in items_series_list:
                try:
                    if val is not None and str(val).strip() != '' and str(val).lower() != 'nan':
                        items_list.append(int(val))
                except (ValueError, TypeError):
                    continue
        except:
            items_list = []
        # Convertir a set para eliminar duplicados y luego a lista
        items = list(set(items_list))
        total = len(items)

        # --- 2. TIPO DE PROCESO ---
        df_base['EAN'] = df_base['EAN'].astype(str)
        tipo_proceso = []
        for idx, item in enumerate(items):
            match = df_base[df_base['EAN'] == str(item)]
            tipo = match.iloc[0]['CODIGO FORMATO'] if not match.empty and 'CODIGO FORMATO' in match.columns else ''
            tipo_proceso.append(tipo)
            progress = ((idx + 1) / total) * 20
            progress_var.set(progress)
            percent_label.config(text=f"{int(progress)}%")
            frame.update()

        # --- 3. NORMA ---
        norma = []
        for idx, item in enumerate(items):
            match = df_reporte[df_reporte[num_parte_col].astype(str) == str(item)]
            n = match.iloc[0][norma_col] if not match.empty and norma_col in match.columns else ''
            norma.append(n)
            progress = 20 + ((idx + 1) / total) * 20
            progress_var.set(progress)
            percent_label.config(text=f"{int(progress)}%")
            frame.update()

        # --- 4. DESCRIPCION ---
        descripcion = []
        for idx, item in enumerate(items):
            match = df_reporte[df_reporte[num_parte_col].astype(str) == str(item)]
            desc = match.iloc[0][desc_col] if not match.empty and desc_col in match.columns else ''
            descripcion.append(desc)
            progress = 40 + ((idx + 1) / total) * 20
            progress_var.set(progress)
            percent_label.config(text=f"{int(progress)}%")
            frame.update()

        # --- 5. CRITERIO ---
        criterio = []
        for idx, item in enumerate(items):
            match = df_codigos_cumple[df_codigos_cumple['ITEM'].astype(str) == str(item)]
            if not match.empty:
                if 'OBSERVACIONES' in match.columns:
                    obs = str(match.iloc[0]['OBSERVACIONES']).upper().strip()
                    if 'CUMPLE' in obs:
                        crit = 'CUMPLE'
                    else:
                        crit = str(match.iloc[0]['CRITERIO']).strip() if 'CRITERIO' in match.columns else ''
                else:
                    crit = ''
            else:
                crit = ''
            criterio.append(crit)
            progress = 60 + ((idx + 1) / total) * 20
            progress_var.set(progress)
            percent_label.config(text=f"{int(progress)}%")
            frame.update()

        # Crear DataFrame final
        df_result = pd.DataFrame({
            'ITEM': items,
            'TIPO DE PROCESO': tipo_proceso,
            'NORMA': norma,
            'CRITERIO': criterio,
            'DESCRIPCION': descripcion,
        })
        progress_var.set(80)
        percent_label.config(text="80%")
        frame.update()

        # REGLAS PARA MODIFICAR TIPO DE PROCESO, NORMA Y CRITERIO
        normas_adherible = [
            'NOM-050-SCFI-2004', 'NOM-121-SCFI-2004',
            'NOM-015-SCFI-2007', 'NOM-050-SCFI-2004',
            'NOM-024-SCFI-2013', 'NOM-141-SSA1/SCFI-2012',
            'NOM004TEXX', 'NOM020INS', 'NOM-115-STPS-2009','NOM-189-SSA1/SCFI-2018'
        ]
        normas_costura = ['NOM-004-SE-2021', 'NOM-020-SCFI-1997', 'NOM004', 'NOM020']

        def contiene_numero(texto, lista_numeros):
            texto = str(texto)
            return any(n in texto for n in lista_numeros)

        def modificar_tipo_proceso(row):
            norma_val = str(row['NORMA'])
            tipo = str(row['TIPO DE PROCESO'])
            if 'NOM004TEXX' in tipo or 'TEXX' in norma_val:
                return 'ADHERIBLE'
            if 'NOM004' in tipo or '004' or 'NOM-004-SE-2021' in norma_val:
                return 'COSTURA'
            if 'NOM020INS' in norma_val:
                return 'ADHERIBLE'
            if contiene_numero(norma_val, normas_adherible):
                return 'ADHERIBLE'
            if contiene_numero(norma_val, normas_costura):
                return 'COSTURA'
            if norma_val == '0':
                return 'SIN NORMA'
            if norma_val == 'N/D':
                return ''
            return tipo

        df_result['TIPO DE PROCESO'] = df_result.apply(modificar_tipo_proceso, axis=1)

        def modificar_norma(norma_val):
            if str(norma_val) == '0':
                return 'SIN NORMA'
            elif str(norma_val) == 'N/D':
                return ''
            return norma_val
        df_result['NORMA'] = df_result['NORMA'].apply(modificar_norma)

        def modificar_criterio(crit_val):
            crit = str(crit_val).strip().upper()
            if 'NO CUMPLE' in crit:
                return crit_val
            if any(palabra in crit for palabra in ['CUMPLE', 'C']):
                return 'CUMPLE'
            return crit_val
        df_result['CRITERIO'] = df_result['CRITERIO'].apply(modificar_criterio)

        # LISTADO DE NORMAS VALIDAS
        normas_validas = ['003','NOM-004-SE-2021','008','NOM-015-SCFI-2007','020','NOM-020-SCFI-1997',
                          'NOM-024-SCFI-2013','035','NOM-050-SCFI-2004','051','116','NOM-141-SSA1/SCFI-2012','142','173','185','186','NOM-189-SSA1/SCFI-2018','192','199','235','NOM-115-STPS-2009','NOM-121-SCFI-2004']

        # REGLAS ADICIONALES
        for idx, row in df_result.iterrows():
            tipo_val = row['TIPO DE PROCESO']
            norma_val_raw = row['NORMA']
            criterio_val_raw = row['CRITERIO']
            
            # Simplificar verificaciones de valores nulos
            tipo = str(tipo_val).strip() if tipo_val is not None and str(tipo_val).strip() != '' and str(tipo_val).lower() != 'nan' else ''
            norma_val = str(norma_val_raw).strip() if norma_val_raw is not None and str(norma_val_raw).strip() != '' and str(norma_val_raw).lower() != 'nan' else ''
            criterio_val = str(criterio_val_raw).strip().upper() if criterio_val_raw is not None and str(criterio_val_raw).strip() != '' and str(criterio_val_raw).lower() != 'nan' else ''

            if norma_val not in normas_validas:
                df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                if norma_val in ['', '0']:
                    df_result.at[idx, 'NORMA'] = 'SIN NORMA'

            if tipo == '' or (tipo == '0' and norma_val == '0') or (tipo == '' and norma_val == ''):
                df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                df_result.at[idx, 'NORMA'] = 'SIN NORMA'

            if 'CUMPLE' in criterio_val:
                df_result.at[idx, 'TIPO DE PROCESO'] = 'CUMPLE'
                df_result.at[idx, 'CRITERIO'] = ''
            elif criterio_val not in ['', 'N/D']:
                df_result.at[idx, 'CRITERIO'] = 'REVISADO'

            if norma_val in ['NOM-050-SCFI-2004', 'NOM-015-SCFI-2007'] and 'CUMPLE' not in criterio_val:
                df_result.at[idx, 'TIPO DE PROCESO'] = 'ADHERIBLE'

        progress_var.set(100)
        percent_label.config(text="100%")
        progress_label.config(text="¡Completado!")
        frame.update()

        def remove_progress_widgets():
            try:
                if 'progress_label' in globals() and progress_label is not None:
                    progress_label.destroy()
                if 'progress_bar' in globals() and progress_bar is not None:
                    progress_bar.destroy()
                if 'percent_label' in globals() and percent_label is not None:
                    percent_label.destroy()
            except:
                pass
        frame.after(500, remove_progress_widgets)

        # Guardar archivo final
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar archivo TIPO DE PROCESO",
            initialfile="TIPO DE PROCESO.xlsx"
        )

        if save_path:
            exportar_excel(df_result, save_path)
        else:
            messagebox.showwarning("Cancelado", "No se guardó el archivo.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")

def seleccionar_reporte():
    ruta = filedialog.askopenfilename(
        title="Seleccionar REPORTE DE MERCANCIA",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if ruta:
        procesar_reporte(ruta)
#  CATALOGO DE DECATHLON 
def actualizar_catalogo(frame_principal):
    barra = None
    try:
        # Seleccionar archivo Excel
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de catálogo",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return  # Usuario canceló

        barra = BarraProgreso(frame_principal, "Cargando catálogo...")

        # Paso 1: leer Excel
        barra.actualizar(20)
        df = pd.read_excel(file_path)

        # Paso 2: preparar rutas
        barra.actualizar(50)
        if getattr(sys, "frozen", False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        else:
            base_path = os.path.dirname(__file__)

        resources_path = os.path.join(base_path, "resources")
        if not os.path.exists(resources_path):
            os.makedirs(resources_path)

        json_path = os.path.join(resources_path, "base_general.json")

        # Paso 3: guardar JSON
        barra.actualizar(80)
        df.to_json(json_path, orient="records", force_ascii=False, indent=4)

        # Paso 4: finalizar
        barra.actualizar(100)
        time.sleep(0.5)
        barra.finalizar()

        messagebox.showinfo("Catálogo actualizado", "El catálogo fue cargado correctamente.")

    except Exception as e:
        if barra:
            barra.finalizar()
        messagebox.showerror("Error", f"No se pudo actualizar el catálogo:\n{e}")

#  FUNCION PARA EXPORTAR EL CATALOGO DE DECATHLON 
def exportar_concentrado_catalogo(frame_principal):
    try:
        # Detectar ruta base (para .exe y script)
        if getattr(sys, "frozen", False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        else:
            base_path = os.path.dirname(__file__)

        resources_path = os.path.join(base_path, "resources")
        json_path = os.path.join(resources_path, "base_general.json")

        if not os.path.exists(json_path):
            messagebox.showerror("Error", "No se encontró el archivo base_general.json")
            return

        df = pd.read_json(json_path)

        # Crear barra de progreso
        barra = BarraProgreso(frame_principal, "Descargando catalogo...")

        total_filas = len(df)
        for i in range(total_filas):
            barra.actualizar((i + 1) / total_filas * 100)

        # Seleccionar ruta de guardado
        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar concentrado del catálogo"
        )
        if not ruta_guardado:
            barra.finalizar()
            return

        # Exportar a Excel
        with pd.ExcelWriter(ruta_guardado, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        barra.finalizar()
        messagebox.showinfo("Exportar Catálogo", f"[OK] Se exportó correctamente el concentrado a:\n{ruta_guardado}")

    except Exception as e:
        try:
            barra.finalizar()
        except:
            pass
        messagebox.showerror("Error", f"No se pudo exportar el catálogo:\n{e}")

#  VENTANA DEL DASHBOARD MEJORADO 
def mostrar_estadisticas():
    """Llama al archivo Dashboard.py para mostrar el dashboard externo"""
    try:
        subprocess.Popen(["python", "Dashboard.py"])
    except Exception as e:
        print(f"Error al abrir el dashboard: {e}")

#  FUNCION PARA LA BARRA DE PROGRESO 
class BarraProgreso:
    def __init__(self, frame, texto="Procesando...", ancho=250, posicion="derecha"):
        """
        frame: contenedor donde se mostrará la barra
        texto: texto de la barra
        ancho: longitud de la barra
        posicion: "derecha" o "izquierda"
        """
        self.frame = frame
        self.ancho = ancho
        self.var = tk.DoubleVar()
        
        self.lbl = tk.Label(frame, text=texto, font=("INTER", 10, "bold"), bg="#FFFFFF", fg="#282828")
        self.percent_lbl = tk.Label(frame, text="0%", font=("INTER", 10, "bold"), bg="#FFFFFF", fg="#282828")
        self.bar = ttk.Progressbar(frame, variable=self.var, maximum=100, length=self.ancho)
        
        # Guardar posición
        self.posicion = posicion
        self._colocar_widgets()
        frame.update()

    def _colocar_widgets(self):
        """Coloca los widgets según la posición deseada."""
        if self.posicion == "derecha":
            anchor = "se"
            x_offset = -20
        else:  # izquierda
            anchor = "sw"
            x_offset = 20

        # Barra y etiquetas
        self.bar.place(relx=1.0 if self.posicion=="derecha" else 0.0, rely=1.0, x=x_offset, y=-40, anchor=anchor)
        self.lbl.place(relx=1.0 if self.posicion=="derecha" else 0.0, rely=1.0, x=x_offset, y=-60, anchor=anchor)
        self.percent_lbl.place(relx=1.0 if self.posicion=="derecha" else 0.0, rely=1.0, x=x_offset, y=-20, anchor=anchor)

    def actualizar(self, valor, texto=None):
        try:
            self.var.set(valor)
            if texto and hasattr(self, 'lbl') and self.lbl.winfo_exists():
                self.lbl.config(text=texto)
            if hasattr(self, 'percent_lbl') and self.percent_lbl.winfo_exists():
                self.percent_lbl.config(text=f"{int(valor)}%")
            if hasattr(self, 'frame') and self.frame.winfo_exists():
                self.frame.update()
        except Exception as e:
            print(f"Error actualizando barra de progreso: {e}")

    def finalizar(self, mensaje="¡Completado!"):
        try:
            self.var.set(100)
            if hasattr(self, 'lbl') and self.lbl.winfo_exists():
                self.lbl.config(text=mensaje)
            if hasattr(self, 'percent_lbl') and self.percent_lbl.winfo_exists():
                self.percent_lbl.config(text="100%")
            if hasattr(self, 'frame') and self.frame.winfo_exists():
                self.frame.update()
                # Ocultar widgets después de un tiempo
                self.frame.after(800, self._ocultar)
        except Exception as e:
            print(f"Error finalizando barra de progreso: {e}")

    def _ocultar(self):
        try:
            if hasattr(self, 'bar') and self.bar.winfo_exists():
                self.bar.place_forget()
            if hasattr(self, 'lbl') and self.lbl.winfo_exists():
                self.lbl.place_forget()
            if hasattr(self, 'percent_lbl') and self.percent_lbl.winfo_exists():
                self.percent_lbl.place_forget()
        except Exception as e:
            print(f"Error ocultando widgets: {e}")

#  VENTANA PRINCIPAL 
root = tk.Tk()
root.title("GENERADOR DE TIPO DE PROCESO")
root.geometry("900x600")
root.configure(bg="#FFFFFF")


#  DISEÑO DE LA VENTANA 
if __name__ == "__main__":
    # Configurar estilo global
    style = ttk.Style()
    style.theme_use('clam')
    
    # Frame principal con fondo blanco
    frame = tk.Frame(root, bg="#FFFFFF")
    frame.pack(expand=True, fill="both", padx=30, pady=30)

    # --- Header con título ---
    header_frame = tk.Frame(frame, bg="#FFFFFF")
    header_frame.pack(fill="x", pady=(0, 25))

    # Título principal
    label_titulo = tk.Label(
        header_frame, 
        text="INSPECCIÓN DE CUMPLIMIENTO\nNORMATIVO AL ARRIBO",
        font=("Inter", 24, "bold"), 
        fg="#282828", 
        bg="#FFFFFF", 
        justify="center"
    )
    label_titulo.pack(pady=(0, 8))

    # Subtítulo
    label_sub = tk.Label(
        header_frame, 
        text="Sistema integral para la gestión de procesos normativos",
        font=("Inter", 11), 
        fg="#4B4B4B", 
        bg="#FFFFFF",
        justify="center"
    )
    label_sub.pack()

    # --- Contenido principal: Logo y Botones ---
    content_frame = tk.Frame(frame, bg="#FFFFFF")
    content_frame.pack(fill="both", expand=True, pady=(0, 15))

    # Panel izquierdo: Logo centrado
    left_panel = tk.Frame(content_frame, bg="#FFFFFF", width=250)
    left_panel.pack(side="left", fill="y")
    left_panel.pack_propagate(False)

    # Logo más pequeño
    try:
        logo_path = os.path.join(BASE_PATH, "img", "logo.png")
        if os.path.exists(logo_path):
            logo_img_raw = Image.open(logo_path).resize((250, 190), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(logo_img_raw)
            logo_label = tk.Label(left_panel, image=logo_img, bg="#FFFFFF")
            logo_label.image = logo_img
            logo_label.pack(pady=(15, 0))
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    # Separador visual
    separator = tk.Frame(left_panel, bg="#ECD925", height=2)
    separator.pack(fill="x", pady=10, padx=8)

    # Texto descriptivo bajo el logo
    tk.Label(left_panel, 
             text="Expertos en NOM's\n Líderes en evaluación regulatoria.", 
             font=("Inter", 9), 
             fg="#4B4B4B", 
             bg="#FFFFFF",
             justify="center").pack()

    # Panel derecho: Botones organizados
    right_panel = tk.Frame(content_frame, bg="#FFFFFF")
    right_panel.pack(side="right", fill="both", expand=True)

    # Configurar estilo de botones MÁS PEQUEÑOS
        # --- Estilo más compacto y estético de botones ---
    style.configure(
        'SmallCard.TButton',
        background='#ecd925',   # Amarillo corporativo
        foreground='#282828',
        font=('Inter', 10, 'bold'),
        borderwidth=0,
        padding=(6, 4),
        focusthickness=0,
        focuscolor='none'
    )
    style.map(
        'SmallCard.TButton',
        background=[('active', '#Ecd926'), ('hover', '#FFF176')],
        relief=[('pressed', 'sunken')]
    )

    # Contenedor principal
    main_button_container = tk.Frame(right_panel, bg="#FFFFFF")
    main_button_container.pack(fill="both", expand=True, padx=5, pady=5)

    # Botones más pequeños con emojis arriba
    botones = [
        ("⚙️ Configurar", configurar_rutas),
        ("📊 Reportes", seleccionar_reporte),
        ("📋 Editor", lambda: abrir_editor_codigos(right_panel)),
        ("📈 Dashboard", mostrar_estadisticas),
        ("🔄 Actualizar", lambda: actualizar_catalogo(right_panel)),
        ("💾 Exportar", lambda: exportar_concentrado_catalogo(right_panel))
    ]

    cols = 3
    for i, (texto, comando) in enumerate(botones):
        row = i // cols
        col = i % cols

        btn = ttk.Button(
            main_button_container,
            text=texto,
            command=comando,
            style='SmallCard.TButton',
            width=5
        )
        btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew", ipadx=3, ipady=6)

    # Ajuste de filas/columnas
    for i in range(2):
        main_button_container.grid_rowconfigure(i, weight=1)
    for i in range(cols):
        main_button_container.grid_columnconfigure(i, weight=1)

    # Footer minimalista más pequeño
    footer_frame = tk.Frame(frame, bg="#FFFFFF")
    footer_frame.pack(fill="x", pady=(10, 0))

    # Línea decorativa más delgada
    footer_line = tk.Frame(footer_frame, bg="#ECD925", height=1)
    footer_line.pack(fill="x", pady=(0, 8))

    tk.Label(footer_frame, 
             text="Sistema de Gestión de Procesos V&C - Versión 2.0 • © 2025", 
             font=("Inter", 8,'bold'),  # Fuente más pequeña
             fg="#4B4B4B", 
             bg="#FFFFFF").pack()

root.mainloop()