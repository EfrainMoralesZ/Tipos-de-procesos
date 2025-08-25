import os
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sys
import json
from Formato import exportar_excel
import re
import time

if getattr(sys, 'frozen', False):
    # Cuando está compilado en .exe
    BASE_PATH = sys._MEIPASS
else:
    # Cuando se ejecuta desde Python
    BASE_PATH = os.path.dirname(__file__)

# Archivos fijos
BASE_GENERAL = os.path.join(BASE_PATH, "archivos","BASE DECATHLON GENERAL ADVANCE II.xlsx")
INSPECCION = os.path.join(BASE_PATH, "archivos","codigos_cumple.xlsx")
HISTORIAL = os.path.join(BASE_PATH, "archivos","HISTORIAL_PROCESOS.xlsx")

# Rutas de archivos
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INSPECCION = os.path.join(BASE_PATH, "archivos","codigos_cumple.xlsx")

def actualizar_observacion_interactiva(item, obs_actual, obs_nueva):
    ventana = tk.Toplevel()
    ventana.title(f"Actualizar OBSERVACIONES - ITEM {item}")
    ventana.geometry("400x200")
    ventana.grab_set()

    tk.Label(ventana, text=f"ITEM: {item}", font=("Segoe UI", 10, "bold")).pack(pady=(10,5))
    tk.Label(ventana, text="Observación actual:").pack()
    tk.Label(ventana, text=obs_actual, fg="blue").pack(pady=(0,10))
    
    tk.Label(ventana, text="Nueva observación:").pack()
    entrada = tk.Entry(ventana, width=50)
    entrada.insert(0, obs_nueva)
    entrada.pack(pady=(0,10))

    resultado = {"valor": obs_actual}

    def guardar():
        resultado["valor"] = entrada.get()
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar, bg="#ECD925").pack(pady=10)
    ventana.wait_window()
    return resultado["valor"]

# --- Función para actualizar códigos ---
def actualizar_codigos(frame_principal):
    try:
        nuevo_file = filedialog.askopenfilename(
            title="Selecciona el archivo con nuevos códigos",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if not nuevo_file:
            return

        df_base = pd.read_excel(INSPECCION) if os.path.exists(INSPECCION) else pd.DataFrame(columns=["ITEM","OBSERVACIONES","CRITERIO"])
        df_nuevo = pd.read_excel(nuevo_file)

        if "ITEM" not in df_nuevo.columns:
            messagebox.showerror("Error", "El archivo nuevo no contiene la columna 'ITEM'")
            return

        df_nuevo = df_nuevo.drop_duplicates(subset=["ITEM"])
        for col in ["OBSERVACIONES","CRITERIO"]:
            if col not in df_nuevo.columns:
                df_nuevo[col] = ""

        items_existentes = set(df_base["ITEM"].astype(str))
        nuevos_items = []

        # Barra de progreso unificada
        barra = BarraProgreso(frame_principal, "Actualizando items...")

        for idx, row in df_nuevo.iterrows():
            item = str(row["ITEM"])
            obs_nueva = str(row.get("OBSERVACIONES",""))
            criterio_nuevo = str(row.get("CRITERIO",""))

            if item in items_existentes:
                fila_base = df_base[df_base["ITEM"].astype(str) == item].iloc[0]
                obs_actual = str(fila_base.get("OBSERVACIONES",""))
                if obs_actual != obs_nueva:
                    obs_final = actualizar_observacion_interactiva(item, obs_actual, obs_nueva)
                    df_base.loc[df_base["ITEM"].astype(str) == item, "OBSERVACIONES"] = obs_final
            else:
                nuevos_items.append({"ITEM": item, "OBSERVACIONES": obs_nueva, "CRITERIO": criterio_nuevo})

            barra.actualizar((idx+1)/len(df_nuevo)*100)

        if nuevos_items:
            df_base = pd.concat([df_base, pd.DataFrame(nuevos_items)], ignore_index=True)

        df_base.to_excel(INSPECCION, index=False)
        barra.finalizar()

        messagebox.showinfo(
            "Actualizar ITEMS",
            f"✅ Se actualizaron OBSERVACIONES y se agregaron {len(nuevos_items)} ITEMS nuevos.\n📊 Total ahora: {len(df_base)}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema al actualizar los códigos:\n{e}")

# --- Función para exportar concentrado ---
def exportar_concentrado_codigos(frame_principal):
    try:
        if not os.path.exists(INSPECCION):
            messagebox.showerror("Error", f"No se encontró el archivo {INSPECCION}")
            return

        df_codigos = pd.read_excel(INSPECCION)
        total_filas = len(df_codigos)

        barra = BarraProgreso(frame_principal, "Generando concentrado...")

        for i in range(total_filas):
            barra.actualizar((i+1)/total_filas*100)

        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")],
            title="Guardar concentrado de codigos_cumple"
        )
        if not ruta_guardado:
            barra.finalizar()
            return

        df_codigos.to_excel(ruta_guardado, index=False)
        barra.finalizar()
        messagebox.showinfo("Exportar Codigos", f"✅ Se exportó correctamente el concentrado a:\n{ruta_guardado}")

    except Exception as e:
        barra.finalizar()
        messagebox.showerror("Error", f"Ocurrió un problema al exportar el concentrado:\n{e}")

def crear_boton_exportar_concentrado(frame):
    """
    Crea un botón ttk dentro del frame indicado para exportar el concentrado de codigos_cumple.xlsx
    """
    btn_exportar = ttk.Button(
        frame, 
        text="📦 EXPORTAR CONCENTRADO CODIGOS", 
        command=exportar_concentrado_codigos,  # Función que definimos antes
        style='TButton'
    )
    btn_exportar.pack(pady=10, ipadx=10, ipady=5)
    return btn_exportar

def procesar_reporte(reporte_path):
    global frame
    try:
        # SE CREA LA BARRA DE PROGRESO EN LA FRAME PRINCIPAL
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

            # LECTURA DE DATOS DE LOS ARCHIVOS DE EXCEL CONVERTIDOS EN JSON
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

            # LEER ARCHIVOS BASE EN FORMATO JSON
            df_base = cargar_json("base_general.json")
            df_codigos_cumple = cargar_json("codigos_cumple.json")
            df_reporte = pd.read_excel(reporte_path)  # El reporte sigue siendo cargado por el usuario

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
            
            # ABUSQUEDA QUE SE REALIZA PARA EL ARMADO DE LAS COLUMNAS DEL ARCHIVO TIPOS DE PROCESOS

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

            # ORDEN EN EL QUE SE IMPRIMEN LAS COLUMNAS EN EL ARCHIVO TIPO DE PROCESO
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

            # REGLAS PARA MODIFICAR EN LA COLUMNA TIPO DE PROCESO
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
            
            # SE VALIDA QUE AMBAS COLUMNAS ESTEN VACIAS PARA PONER "SIN NORMA"
            def modificar_norma(norma):
                if str(norma) == '0':
                    return 'SIN NORMA'
                elif str(norma) == 'N/D':
                    return ''
                return norma
            df_result['NORMA'] = df_result['NORMA'].apply(modificar_norma)
            
            # SE MODIFICA C o CUMPLE por CUMPLE
            def modificar_criterio(criterio):
                crit = str(criterio).strip().upper()
                if 'NO CUMPLE' in crit:
                    return criterio
                if any(palabra in crit for palabra in ['CUMPLE', 'C']):
                    return 'CUMPLE'
                return criterio
            df_result['CRITERIO'] = df_result['CRITERIO'].apply(modificar_criterio)

            # LISTADO DE NORMAS VALIDAS PARA REALIZAR LOS TIPO DE PROCESOS
            normas_validas = ['003','004','NOM-004-SE-2021','008','015','020','NOM-020-SCFI-1997',
                            '024','NOM-024-SCFI-2013','035','050','051','116','141','142','173','185','186','189','192','199','235']
            
            # REGLAS PARA MODIFICAR EL ARCHIVO TIPO DE PROCESO
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
                    # ✅ Cualquier texto que NO sea vacío ni "N/D" se convierte en REVISADO
                    df_result.at[idx, 'CRITERIO'] = 'REVISADO'

                # Normas especiales
                if norma in ['NOM-050-SCFI-2004', 'NOM-015-SCFI-2007'] and 'CUMPLE' not in criterio:
                    df_result.at[idx, 'TIPO DE PROCESO'] = 'ADHERIBLE'

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
                # ✅ Guardar con formato (usa Formato.py)
                exportar_excel(df_result, save_path)

                # ✅ Actualizar historial (sin formato especial)
                if Path(HISTORIAL).exists():
                    df_hist = pd.read_excel(HISTORIAL)
                    df_final = pd.concat([df_hist, df_result]).drop_duplicates(subset=["ITEM"])
                else:
                    df_final = df_result.copy()
                df_final.to_excel(HISTORIAL, index=False)

                # ✅ Solo mostrar mensaje
                messagebox.showinfo("Éxito", "GUARDADO EXITOSAMENTE")
            else:
                messagebox.showwarning("Cancelado", "No se guardó el archivo.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")

def seleccionar_reporte():
    ruta = filedialog.askopenfilename(
        title="Seleccionar REPORTE DE MERCANCIA",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if ruta:
        procesar_reporte(ruta)

# --- Función unificada para la barra de progreso ---
class BarraProgreso:
    def __init__(self, frame, texto="Procesando..."):
        self.frame = frame
        self.lbl = tk.Label(frame, text=texto, font=("Segoe UI", 10), bg="#FFFFFF")
        self.lbl.pack(pady=(10,0))
        self.var = tk.DoubleVar()
        self.bar = ttk.Progressbar(frame, variable=self.var, maximum=100, length=400)
        self.bar.pack(pady=10)
        frame.update()

    def actualizar(self, valor):
        self.var.set(valor)
        self.frame.update()

    def finalizar(self, mensaje="¡Completado!"):
        self.var.set(self.bar["maximum"])
        self.lbl.config(text=mensaje)
        self.frame.update()
        self.frame.after(800, lambda: (self.lbl.destroy(), self.bar.destroy()))

# VENTANA PRINCIPAL
root = tk.Tk()
root.title("Generador TIPO DE PROCESO")
root.geometry("750x580")
root.configure(bg="#FFFFFF")

#DISEÑO DE LA VENTANA
if __name__ == "__main__":
    frame = tk.Frame(root, bg="#FFFFFF")
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # --- Frame superior con logo y títulos ---
    frame_top = tk.Frame(frame, bg="#FFFFFF")
    frame_top.pack(pady=(0, 20), fill="x")

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

    label = tk.Label(
        frame_top, 
        text="Generador de archivo TIPO DE PROCESO",
        font=("Segoe UI", 16, "bold"), 
        bg="#FFFFFF", 
        fg="#282828"
    )
    label.pack(pady=(0, 5))

    desc = tk.Label(
        frame_top,
        text="Sube el archivo REPORTE DE MERCANCIA y genera el archivo Tipo de proceso.",
        font=("Segoe UI", 10), 
        bg="#FFFFFF", 
        fg="#282828"
    )
    desc.pack(pady=(0,15))

    # --- Estilo uniforme de botones ---
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        'TButton', 
        background='#ECD925', 
        foreground='#282828', 
        font=('Segoe UI', 11, 'bold'), 
        borderwidth=0, 
        padding=(5,5)
    )
    style.map(
        'TButton', 
        background=[('active', '#D8C600')], 
        foreground=[('active', '#282828')]
    )

    # --- Frame para botones en grid ---
    frame_buttons = tk.Frame(frame, bg="#FFFFFF")
    frame_buttons.pack(expand=True, fill="both", pady=10)

    # --- Barra de progreso (inicialmente oculta) ---
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
    progress_label = tk.Label(frame, text="", bg="#FFFFFF", fg="#282828", font=("Segoe UI", 10, "bold"))
    percent_label = tk.Label(frame, text="", bg="#FFFFFF", fg="#282828", font=("Segoe UI", 10, "bold"))

    def iniciar_barra_progreso():
        progress_bar.pack(fill="x", padx=20, pady=(10,0))
        progress_label.pack(pady=(5,0))
        percent_label.pack(pady=(0,10))
        progress_var.set(0)
        progress_label.config(text="Procesando...")
        percent_label.config(text="0%")
        frame.update()

    def actualizar_barra(valor):
        progress_var.set(valor)
        percent_label.config(text=f"{int(valor)}%")
        frame.update()

    def finalizar_barra_progreso():
        progress_var.set(100)
        percent_label.config(text="100%")
        progress_label.config(text="¡Completado!")
        frame.update()
        def remove_widgets():
            progress_bar.pack_forget()
            progress_label.pack_forget()
            percent_label.pack_forget()
        frame.after(500, remove_widgets)

    # Lista de botones (texto y función), usando lambda para pasar frame
    botones = [
        ("📂 REPORTE DE MERCANCIA", seleccionar_reporte),
        ("🔄 ACTUALIZAR CODIGOS CUMPLE", lambda: actualizar_codigos(frame)),  # Pasamos frame
        ("📦 EXPORTAR CONCENTRADO CODIGOS", lambda: exportar_concentrado_codigos(frame)),  # <-- aquí
        ("❌ Salir", root.quit)
    ]
    # Configurar grid con 2 columnas
    columnas = 2
    for i, (texto, comando) in enumerate(botones):
        btn = ttk.Button(frame_buttons, text=texto, command=comando, style='TButton')
        row = i // columnas
        col = i % columnas
        btn.grid(row=row, column=col, padx=20, pady=20, ipadx=10, ipady=10, sticky="nsew")

    # Ajustar tamaño de columnas para que se expandan igual
    for col in range(columnas):
        frame_buttons.grid_columnconfigure(col, weight=1)

    root.mainloop()
