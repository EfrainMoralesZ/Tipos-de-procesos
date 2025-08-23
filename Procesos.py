import os
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sys
import json
from Formato import exportar_excel
from admin_items import abrir_admin_items
from admin_codigos_cumple import abrir_admin_codigos_cumple
import re

# Variables globales para las rutas de archivos
BASE_GENERAL_PATH = None
INSPECCION_PATH = None
HISTORIAL_PATH = None

if getattr(sys, 'frozen', False):
    # Cuando está compilado en .exe
    BASE_PATH = sys._MEIPASS
else:
    # Cuando se ejecuta desde Python
    BASE_PATH = os.path.dirname(__file__)

# Archivo de configuración para persistir las rutas
CONFIG_FILE = os.path.join(BASE_PATH, "config.json")

def cargar_configuracion():
    """Carga la configuración guardada de archivos base"""
    global BASE_GENERAL_PATH, INSPECCION_PATH, HISTORIAL_PATH
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                BASE_GENERAL_PATH = config.get('BASE_GENERAL_PATH')
                INSPECCION_PATH = config.get('INSPECCION_PATH')
                HISTORIAL_PATH = config.get('HISTORIAL_PATH')
                return True
    except Exception as e:
        print(f"Error cargando configuración: {e}")
    
    return False

def guardar_configuracion():
    """Guarda la configuración actual de archivos base"""
    try:
        config = {
            'BASE_GENERAL_PATH': BASE_GENERAL_PATH,
            'INSPECCION_PATH': INSPECCION_PATH,
            'HISTORIAL_PATH': HISTORIAL_PATH
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False

def verificar_archivos_existen():
    """Verifica si los archivos configurados aún existen"""
    global BASE_GENERAL_PATH, INSPECCION_PATH, HISTORIAL_PATH
    
    archivos_validos = True
    
    if BASE_GENERAL_PATH and not os.path.exists(BASE_GENERAL_PATH):
        BASE_GENERAL_PATH = None
        archivos_validos = False
        
    if INSPECCION_PATH and not os.path.exists(INSPECCION_PATH):
        INSPECCION_PATH = None
        archivos_validos = False
        
    if HISTORIAL_PATH and not os.path.exists(HISTORIAL_PATH):
        HISTORIAL_PATH = None
        archivos_validos = False
    
    return archivos_validos

def cargar_archivos_automaticamente():
    """Intenta cargar los archivos base automáticamente desde la configuración"""
    if cargar_configuracion():
        if verificar_archivos_existen():
            return True
    
    return False

def seleccionar_archivos_base():
    """Permite al usuario seleccionar los archivos base necesarios para la aplicación"""
    global BASE_GENERAL_PATH, INSPECCION_PATH, HISTORIAL_PATH
    
    # Seleccionar archivo BASE GENERAL
    base_general = filedialog.askopenfilename(
        title="Seleccionar archivo BASE GENERAL (BASE DECATHLON GENERAL ADVANCE II.xlsx)",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if not base_general:
        return False
    
    # Seleccionar archivo de INSPECCIÓN (códigos cumple)
    inspeccion = filedialog.askopenfilename(
        title="Seleccionar archivo de INSPECCIÓN (codigos_cumple.xlsx)",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if not inspeccion:
        return False
    
    # Seleccionar archivo de HISTORIAL
    historial = filedialog.askopenfilename(
        title="Seleccionar archivo de HISTORIAL (HISTORIAL_PROCESOS.xlsx)",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if not historial:
        return False
    
    # Asignar las rutas seleccionadas
    BASE_GENERAL_PATH = base_general
    INSPECCION_PATH = inspeccion
    HISTORIAL_PATH = historial
    
    # Guardar la configuración para futuras sesiones
    guardar_configuracion()
    
    return True

def verificar_archivos_base():
    """Verifica si los archivos base han sido seleccionados"""
    return all([BASE_GENERAL_PATH, INSPECCION_PATH, HISTORIAL_PATH])

def actualizar_estado_archivos():
    """Actualiza la etiqueta de estado de archivos base en la interfaz"""
    if verificar_archivos_base():
        estado_archivos_label.config(text="Archivos base configurados", fg="#28A745")
    else:
        estado_archivos_label.config(text="Archivos base no configurados", fg="#FF6B35")

def procesar_reporte(reporte_path):
    global frame
    
    # Verificar que los archivos base estén seleccionados
    if not verificar_archivos_base():
        messagebox.showerror("Error", "Primero debes seleccionar los archivos base necesarios.\n\nUsa el botón 'Configurar Archivos Base' para seleccionarlos.")
        return
    
    try:
        # Crear barra de progreso en el frame principal
        try:
            global progress_label, progress_var, progress_bar, percent_label
            try:
                progress_label.destroy()
                progress_bar.destroy()
                percent_label.destroy()
            except Exception:
                pass
            progress_label = tk.Label(frame, text="Procesando...", font=("Segoe UI", 12), bg="#FFFFFF")
            progress_label.pack(pady=(10,0))
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100, length=250)
            progress_bar.pack(pady=5)
            percent_label = tk.Label(frame, text="0%", font=("Segoe UI", 10), bg="#FFFFFF")
            percent_label.pack()
            frame.update()


            def cargar_json(nombre_json):
                """
                Carga un archivo JSON como DataFrame de pandas.
                Funciona tanto en Python normal como en .exe creado con PyInstaller.
                """
                if getattr(sys, "frozen", False):
                    # Cuando se ejecuta como .exe
                    base_path = sys._MEIPASS
                else:
                    # Cuando se ejecuta como script normal
                    base_path = os.path.dirname(__file__)
                
                ruta = os.path.join(base_path, "resources", nombre_json)
                
                if not os.path.exists(ruta):
                    raise FileNotFoundError(f"No se encontró el archivo JSON: {ruta}")
                
                with open(ruta, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                return pd.DataFrame(data)


            # Leer archivos base usando las rutas seleccionadas por el usuario
            df_base = cargar_json("base_general.json")
            df_codigos_cumple = cargar_json("codigos_cumple.json")
            df_reporte = pd.read_excel(reporte_path)  # El reporte sigue siendo cargado por el usuario

#=========================================================================================================================0
            # --- Detectar tipo de reporte y columnas ---
            # Primero revisamos si es FH
            if 'Número de Parte' in df_reporte.columns:
                # Reporte FH
                num_parte_col = 'Número de Parte'
                desc_col = 'Desc. Pedimento'
                norma_col = 'Normas'
                criterio_col = 'CRITERIO'   # FH usa CRITERIO
            elif any(col.strip().lower() in ['num. parte', 'num.parte', 'numero de parte','num.parte'] for col in df_reporte.columns):
                # Reporte MIMPO
                for col in df_reporte.columns:
                    if col.strip().lower() in ['num. parte', 'num.parte', 'numero de parte','num.parte']:
                        num_parte_col = col
                        break
                for col in df_reporte.columns:
                    if col.strip().lower() == 'descripción agente aduanal':
                        desc_col = col
                        break
                norma_col = 'NOMs'
                criterio_col = 'CRITERIO'   # 👈 ajusta aquí si en MIMPO se llama distinto (ej: "Criterio")
            else:
                raise ValueError("No se encontró ninguna columna de NUM. PARTE válida en el reporte")

            # --- 1. Columna ITEM ---
            items = pd.to_numeric(df_reporte[num_parte_col], errors='coerce').dropna().astype(int).unique()
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
                    # Verificamos si existe la columna 'OBSERVACIONES'
                    if 'OBSERVACIONES' in match.columns:
                        obs = str(match.iloc[0]['OBSERVACIONES']).upper().strip()
                        if 'CUMPLE' in obs:
                            crit = 'CUMPLE'
                        else:
                            # Si no contiene 'CUMPLE', tomamos el valor de la columna CRITERIO del archivo codigos_cumple
                            crit = str(match.iloc[0]['CRITERIO']).strip() if 'CRITERIO' in match.columns else ''
                    else:
                        crit = ''
                else:
                    crit = ''
                    
                criterio.append(crit)

            # Barra de progreso
            progress = 60 + ((idx + 1) / total) * 20
            progress_var.set(progress)
            percent_label.config(text=f"{int(progress)}%")
            frame.update()


            # --- Crear DataFrame final ---
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
#======================================================================================================

            # Reglas de modificación
            normas_adherible = [
                '015', '050', '004-SE', '024', '141',
                'NOM-015-SCFI-2007', 'NOM-050-SCFI-2004', 'NOM-004-SE-2021',
                'NOM-024-SCFI-2013', 'NOM-141-SSA1/SCFI-2012',
                'NOM004TEXX', 'NOM020INS'
            ]
            normas_costura = ['004', '020', 'NOM004', 'NOM020']

            def contiene_numero(texto, lista_numeros):
                texto = str(texto)
                return any(n in texto for n in lista_numeros)

            def modificar_tipo_proceso(row):
                norma = str(row['NORMA'])
                tipo = str(row['TIPO DE PROCESO'])
                if 'NOM004TEXX' in tipo or 'TEXX' in norma:
                    return 'ADHERIBLE'
                if 'NOM004' in tipo or '004' in norma:
                    return 'COSTURA'
                if 'NOM020INS' in norma:
                    return 'ADHERIBLE'
                if contiene_numero(norma, normas_adherible):
                    return 'ADHERIBLE'
                if contiene_numero(norma, normas_costura):
                    return 'COSTURA'
                if norma == '0':
                    return 'SIN NORMA'
                if norma == 'N/D':
                    return ''
                return tipo

            df_result['TIPO DE PROCESO'] = df_result.apply(modificar_tipo_proceso, axis=1)

            def modificar_norma(norma):
                if str(norma) == '0':
                    return 'SIN NORMA'
                elif str(norma) == 'N/D':
                    return ''
                return norma
            df_result['NORMA'] = df_result['NORMA'].apply(modificar_norma)

            def modificar_criterio(criterio):
                crit = str(criterio).strip().upper()
                if 'NO CUMPLE' in crit:
                    return criterio
                if any(palabra in crit for palabra in ['CUMPLE', 'C']):
                    return 'CUMPLE'
                return criterio
            df_result['CRITERIO'] = df_result['CRITERIO'].apply(modificar_criterio)

#=============================================================================================================
            normas_validas = ['003','004','NOM-004-SE-2021','008','015','020','NOM-020-SCFI-1997',
                            '024','NOM-024-SCFI-2013','035','050','051','116','141','142','173','185','186','189','192','199','235']

            for idx, row in df_result.iterrows():
                # Normalizar valores
                tipo = str(row['TIPO DE PROCESO']).strip() if not pd.isna(row['TIPO DE PROCESO']) else ''
                norma = str(row['NORMA']).strip() if not pd.isna(row['NORMA']) else ''
                criterio = str(row['CRITERIO']).strip().upper() if not pd.isna(row['CRITERIO']) else ''

                # Normas no válidas
                if norma not in normas_validas:
                    df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                    if norma in ['', '0']:
                        df_result.at[idx, 'NORMA'] = 'SIN NORMA'

                # Tipo vacío
                if tipo == '' or (tipo == '0' and norma == '0') or (tipo == '' and norma == ''):
                    df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                    df_result.at[idx, 'NORMA'] = 'SIN NORMA'

                # Criterio
                if 'CUMPLE' in criterio:
                    df_result.at[idx, 'TIPO DE PROCESO'] = 'CUMPLE'
                    df_result.at[idx, 'CRITERIO'] = ''
                elif criterio not in ['', 'N/D']:
                    # Cualquier texto que NO sea vacío ni "N/D" se convierte en REVISADO
                    df_result.at[idx, 'CRITERIO'] = 'REVISADO'

                # Normas especiales
                if norma in ['NOM-050-SCFI-2004', 'NOM-015-SCFI-2007'] and 'CUMPLE' not in criterio:
                    df_result.at[idx, 'TIPO DE PROCESO'] = 'ADHERIBLE'


#=============================================================================================================
            progress_var.set(100)
            percent_label.config(text="100%")
            progress_label.config(text="¡Completado!")
            frame.update()

            def remove_progress_widgets():
                progress_label.destroy()
                progress_bar.destroy()
                percent_label.destroy()
            frame.after(500, remove_progress_widgets)

            # Guardar archivo final con formato
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx")],
                title="Guardar archivo TIPO DE PROCESO",
                initialfile="TIPO DE PROCESO.xlsx"
            )

            if save_path:
                # Guardar con formato (usa Formato.py)
                exportar_excel(df_result, save_path)

                # Actualizar historial (sin formato especial)
                if Path(HISTORIAL_PATH).exists():
                    df_hist = pd.read_excel(HISTORIAL_PATH)
                    df_final = pd.concat([df_hist, df_result]).drop_duplicates(subset=["ITEM"])
                else:
                    df_final = df_result.copy()
                df_final.to_excel(HISTORIAL_PATH, index=False)

                # Solo mostrar mensaje
                messagebox.showinfo("Éxito", "GUARDADO EXITOSAMENTE")
                
                # Verificar si hay items nuevos para agregar a la base general
                verificar_items_nuevos(df_reporte, df_base)
            else:
                messagebox.showwarning("Cancelado", "No se guardó el archivo.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")

def verificar_items_nuevos(df_reporte, df_base):
    """Verifica si hay items nuevos en el reporte y los agrega a la base general"""
    global BASE_GENERAL_PATH
    
    try:
        # Detectar tipo de reporte y obtener columna de número de parte
        if 'Número de Parte' in df_reporte.columns:
            num_parte_col = 'Número de Parte'
        elif any(col.strip().lower() in ['num. parte', 'num.parte', 'numero de parte','num.parte'] for col in df_reporte.columns):
            for col in df_reporte.columns:
                if col.strip().lower() in ['num. parte', 'num.parte', 'numero de parte','num.parte']:
                    num_parte_col = col
                    break
        else:
            return
        
        # Obtener items del reporte
        items_reporte = pd.to_numeric(df_reporte[num_parte_col], errors='coerce').dropna().astype(int).unique()
        
        # Obtener items de la base general
        items_base = pd.to_numeric(df_base['EAN'], errors='coerce').dropna().astype(int).unique()
        
        # Encontrar items nuevos
        items_nuevos = set(items_reporte) - set(items_base)
        
        if len(items_nuevos) > 0:
            # Preguntar al usuario si quiere agregar los items nuevos
            respuesta = messagebox.askyesno(
                "Items Nuevos Detectados", 
                f"Se detectaron {len(items_nuevos):,} items nuevos en el reporte que no están en la base general.\n\n"
                f"¿Deseas agregarlos automáticamente a la base general?"
            )
            
            if respuesta:
                # Crear nuevos registros para los items
                nuevos_items = []
                for item in items_nuevos:
                    # Buscar información del item en el reporte
                    item_info = df_reporte[df_reporte[num_parte_col].astype(str) == str(item)].iloc[0]
                    
                    # Crear registro con campos por defecto
                    nuevo_registro = {
                        'EAN': str(item),
                        'DESCRIPTION': item_info.get('Desc. Pedimento', '') if 'Desc. Pedimento' in item_info else '',
                        'MODEL CODE': '',
                        'MARCA': '',
                        'CUIDADO': '',
                        'CARACTERISTICAS': '',
                        'MEDIDAS': '',
                        'CONTENIDO': '',
                        'MAGNITUD': '',
                        'DENOMINACION': '',
                        'LEYENDAS': '',
                        'EDAD': '',
                        'INSUMOS': '',
                        'FORRO': '',
                        'TALLA': '',
                        'PAIS ORIGEN': '',
                        'IMPORTADOR': '',
                        'ITEM ESPAÑOL': '',
                        'TYPE OF GOODS': '',
                        'HS CODE': '',
                        'NORMA': 'SIN NORMA',
                        'CODIGO FORMATO': '',
                        'TIPO DE ETIQUETA': '',
                        'CLIENTE': 'DECATHLON',
                        'LOGO NOM': '0',
                        'LISTA': 'PZA',
                        'PAIS DE PROCEDENCIA': 'OTRO'
                    }
                    
                    # Intentar obtener descripción si existe
                    if 'descripción agente aduanal' in df_reporte.columns:
                        nuevo_registro['DESCRIPTION'] = item_info.get('descripción agente aduanal', '')
                    
                    nuevos_items.append(nuevo_registro)
                
                # Agregar a la base general
                df_base_nuevo = pd.concat([df_base, pd.DataFrame(nuevos_items)], ignore_index=True)
                
                # Guardar la base actualizada
                if BASE_GENERAL_PATH and BASE_GENERAL_PATH.endswith('.xlsx'):
                    df_base_nuevo.to_excel(BASE_GENERAL_PATH, index=False)
                    messagebox.showinfo(
                        "Items Agregados", 
                        f"Se han agregado {len(items_nuevos):,} items nuevos a la base general.\n\n"
                        f"La base ha sido actualizada y guardada."
                    )
                else:
                    messagebox.showwarning(
                        "Advertencia", 
                        f"Se detectaron {len(items_nuevos):,} items nuevos, pero no se pudo actualizar la base general.\n\n"
                        f"Por favor, usa el administrador de ítems para agregarlos manualmente."
                    )
        
    except Exception as e:
        print(f"Error verificando items nuevos: {e}")

def seleccionar_reporte():
    ruta = filedialog.askopenfilename(
        title="Seleccionar REPORTE DE MERCANCIA",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if ruta:
        procesar_reporte(ruta)

def configurar_archivos_base():
    """Permite al usuario configurar los archivos base necesarios."""
    if seleccionar_archivos_base():
        estado_archivos_label.config(text="Archivos base configurados", fg="#28A745")
        messagebox.showinfo("Éxito", "Archivos base configurados correctamente.\n\nLa configuración se ha guardado y se cargará automáticamente en futuras sesiones.")
    else:
        estado_archivos_label.config(text="Archivos base no configurados", fg="#FF6B35")
        messagebox.showwarning("Advertencia", "No se pudieron configurar los archivos base. Por favor, seleccione los archivos necesarios.")

# Crear ventana principal
root = tk.Tk()
root.title("Generador TIPO DE PROCESO")
root.geometry("650x480")
root.configure(bg="#FFFFFF")

if __name__ == "__main__":
    frame = tk.Frame(root, bg="#FFFFFF")
    frame.pack(expand=True, fill="both")

    frame_top = tk.Frame(frame, bg="#FFFFFF")
    frame_top.pack(pady=(30, 0), fill="x")

    try:
        logo_path = os.path.join(BASE_PATH, "img", "logo.png")
        if os.path.exists(logo_path):
            logo_img_raw = Image.open(logo_path).resize((150, 100), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(logo_img_raw)
            logo_label = tk.Label(frame_top, image=logo_img, bg="#FFFFFF")
            logo_label.image = logo_img
            logo_label.pack(side="top", pady=(0, 10))
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    label = tk.Label(frame_top, text="Generador de archivo TIPO DE PROCESO",
                     font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#282828")
    label.pack(pady=0, padx=10)

    desc = tk.Label(frame, text="Sube el archivo REPORTE DE MERCANCIA y genera el archivo Tipo de proceso.",
                    font=("Segoe UI", 9), bg="#FFFFFF", fg="#282828")
    desc.pack(pady=(0,15))
    
    # Frame para información de archivos base
    frame_archivos = tk.Frame(frame, bg="#FFFFFF")
    frame_archivos.pack(pady=(0, 15))
    
    # Etiqueta de estado de archivos base
    global estado_archivos_label
    estado_archivos_label = tk.Label(frame_archivos, 
                                    text="Cargando configuración...", 
                                    font=("Segoe UI", 9), 
                                    bg="#FFFFFF", 
                                    fg="#FF6B35")
    estado_archivos_label.pack(pady=(0, 5))
    
    # Botón para configurar archivos base
    btn_configurar = ttk.Button(frame_archivos, 
                               text="Configurar Archivos Base", 
                               command=lambda: configurar_archivos_base(), 
                               style='TButton')
    btn_configurar.pack(pady=5, ipadx=10, ipady=3)
    
    # Botón para administrar ítems
    btn_admin_items = ttk.Button(frame_archivos, 
                                text="Administrar Ítems Base", 
                                command=lambda: abrir_admin_items(root), 
                                style='TButton')
    btn_admin_items.pack(pady=5, ipadx=10, ipady=3)
    
    # Botón para administrar códigos cumple
    btn_admin_codigos = ttk.Button(frame_archivos, 
                                  text="Administrar Códigos Cumple", 
                                  command=lambda: abrir_admin_codigos_cumple(root), 
                                  style='TButton')
    btn_admin_codigos.pack(pady=5, ipadx=10, ipady=3)
    
    # Información adicional sobre el administrador de ítems
    info_admin_label = tk.Label(frame_archivos, 
                               text="El administrador de ítems usará automáticamente la base ya configurada", 
                               font=("Segoe UI", 8), 
                               bg="#FFFFFF", 
                               fg="#666666")
    info_admin_label.pack(pady=(0, 5))
    
    # Cargar archivos automáticamente al iniciar
    def cargar_al_iniciar():
        if cargar_archivos_automaticamente():
            actualizar_estado_archivos()
            messagebox.showinfo("Configuración Cargada", 
                              "Los archivos base se han cargado automáticamente desde la configuración guardada.\n\n"
                              "Puedes usar la aplicación directamente o modificar la configuración si es necesario.")
        else:
            actualizar_estado_archivos()
    
    # Ejecutar carga automática después de que la interfaz esté lista
    root.after(100, cargar_al_iniciar)
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', background='#ECD925', foreground='#282828', font=('Segoe UI', 11, 'bold'), borderwidth=0)
    style.map('TButton', background=[('active', '#ECD925')], foreground=[('active', '#282828')])

    btn_cargar = ttk.Button(frame, text="Subir REPORTE DE MERCANCIA", command=seleccionar_reporte, style='TButton')
    btn_cargar.pack(pady=10, ipadx=10, ipady=5)

    btn_salir = ttk.Button(frame, text="Salir", command=root.quit, style='TButton')
    btn_salir.pack(pady=20, ipadx=5, ipady=3)

    root.mainloop()