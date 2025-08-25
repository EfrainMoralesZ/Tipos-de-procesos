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

# --- Función para generar el tipo de proceso ---
def procesar_reporte(reporte_path):
    global frame

    # SE CREA LA BARRA DE PROGRESO EN EL FRAME PRINCIPAL (LADO DERECHO)
    try:
        global progress_label, progress_var, progress_bar, percent_label
        try:
            progress_label.destroy()
            progress_bar.destroy()
            percent_label.destroy()
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
            norma_val = str(row['NORMA'])
            tipo = str(row['TIPO DE PROCESO'])
            if 'NOM004TEXX' in tipo or 'TEXX' in norma_val:
                return 'ADHERIBLE'
            if 'NOM004' in tipo or '004' in norma_val:
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
        normas_validas = ['003','004','NOM-004-SE-2021','008','015','020','NOM-020-SCFI-1997',
                          '024','NOM-024-SCFI-2013','035','050','051','116','141','142','173','185','186','189','192','199','235']

        # REGLAS ADICIONALES
        for idx, row in df_result.iterrows():
            tipo = str(row['TIPO DE PROCESO']).strip() if not pd.isna(row['TIPO DE PROCESO']) else ''
            norma_val = str(row['NORMA']).strip() if not pd.isna(row['NORMA']) else ''
            criterio_val = str(row['CRITERIO']).strip().upper() if not pd.isna(row['CRITERIO']) else ''

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
            progress_label.destroy()
            progress_bar.destroy()
            percent_label.destroy()
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

            if Path(HISTORIAL).exists():
                df_hist = pd.read_excel(HISTORIAL)
                df_final = pd.concat([df_hist, df_result]).drop_duplicates(subset=["ITEM"])
            else:
                df_final = df_result.copy()
            df_final.to_excel(HISTORIAL, index=False)
            messagebox.showinfo("Éxito", "GUARDADO EXITOSAMENTE")
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
            base_path = sys._MEIPASS
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

        messagebox.showinfo("Catálogo actualizado", "El archivo fue cargado y guardado como JSON correctamente.")

    except Exception as e:
        if barra:
            barra.finalizar()
        messagebox.showerror("Error", f"No se pudo actualizar el catálogo:\n{e}")
        
# --- Función unificada para la barra de progreso ---
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
        
        self.lbl = tk.Label(frame, text=texto, font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#282828")
        self.percent_lbl = tk.Label(frame, text="0%", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#282828")
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
        self.var.set(valor)
        if texto:
            self.lbl.config(text=texto)
        self.percent_lbl.config(text=f"{int(valor)}%")
        self.frame.update()

    def finalizar(self, mensaje="¡Completado!"):
        self.var.set(100)
        self.lbl.config(text=mensaje)
        self.percent_lbl.config(text="100%")
        self.frame.update()
        # Ocultar widgets después de un tiempo
        self.frame.after(800, self._ocultar)

    def _ocultar(self):
        self.bar.place_forget()
        self.lbl.place_forget()
        self.percent_lbl.place_forget()
        
# VENTANA PRINCIPAL
root = tk.Tk()
root.title("GENERADOR DE TIPO DE PROCESO")
root.geometry("800x550")
root.configure(bg="#FFFFFF")

# --- DISEÑO DE LA VENTANA ---
if __name__ == "__main__":
    frame = tk.Frame(root, bg="#FFFFFF")
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # --- Frame superior: logo + barra izquierda, botones derecha ---
    frame_top = tk.Frame(frame, bg="#FFFFFF")
    frame_top.pack(expand=True, fill="both")

    # --- Frame izquierdo: logo y barra de progreso ---
    frame_left = tk.Frame(frame_top, bg="#FFFFFF")
    frame_left.pack(side="left", fill="both", expand=True, padx=(0,20))

    # --- Logo ---
    try:
        logo_path = os.path.join(BASE_PATH, "img", "logo.png")
        if os.path.exists(logo_path):
            logo_img_raw = Image.open(logo_path).resize((350, 200), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(logo_img_raw)
            logo_label = tk.Label(frame_left, image=logo_img, bg="#FFFFFF")
            logo_label.image = logo_img
            logo_label.pack(pady=(10, 10))
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    label = tk.Label(
        frame_left, 
        text="GENERADOR DEL ARCHIVO TIPO DE PROCESO",
        font=("Segoe UI", 16, "bold"), 
        bg="#FFFFFF", 
        fg="#282828"
    )
    label.pack(pady=(0, 5))

    desc = tk.Label(
        frame_left,
        text="SUBE EL REPORTE DE MERCANCIA PARA EL TIPO DE PROCESO.",
        font=("Segoe UI", 10), 
        bg="#FFFFFF", 
        fg="#282828"
    )
    desc.pack(pady=(0,15))

    # --- Barra de progreso TIPO DE PROCESO (abajo a la izquierda) ---
    progress_var_tipo = tk.DoubleVar()
    progress_bar_tipo = ttk.Progressbar(frame_left, variable=progress_var_tipo, maximum=100, length=250)
    progress_label_tipo = tk.Label(frame_left, text="", bg="#FFFFFF", fg="#282828", font=("Segoe UI", 10, "bold"))
    percent_label_tipo = tk.Label(frame_left, text="", bg="#FFFFFF", fg="#282828", font=("Segoe UI", 10, "bold"))

    def iniciar_barra_progreso_tipo():
        """Muestra la barra de progreso del TIPO DE PROCESO abajo a la izquierda."""
        progress_var_tipo.set(0)
        progress_label_tipo.config(text="Procesando tipo de proceso...")
        percent_label_tipo.config(text="0%")

        progress_label_tipo.pack(side="bottom", anchor="w", pady=(0,0))
        progress_bar_tipo.pack(side="bottom", anchor="w", pady=(0,2))
        percent_label_tipo.pack(side="bottom", anchor="w", pady=(0,5))
        frame_left.update()

    def actualizar_barra_tipo(valor):
        """Actualiza la barra de progreso y el porcentaje del TIPO DE PROCESO."""
        progress_var_tipo.set(valor)
        percent_label_tipo.config(text=f"{int(valor)}%")
        frame_left.update()

    def finalizar_barra_progreso_tipo():
        """Completa y oculta la barra de progreso del TIPO DE PROCESO."""
        progress_var_tipo.set(100)
        progress_label_tipo.config(text="¡Completado!")
        percent_label_tipo.config(text="100%")
        frame_left.update()

        def remove_widgets():
            progress_bar_tipo.pack_forget()
            progress_label_tipo.pack_forget()
            percent_label_tipo.pack_forget()

        frame_left.after(500, remove_widgets)

    # --- Frame derecho: botones ---
    frame_right = tk.Frame(frame_top, bg="#FFFFFF")
    frame_right.pack(side="right", fill="y")

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

    frame_buttons = tk.Frame(frame_right, bg="#FFFFFF")
    frame_buttons.pack(expand=True, fill="y", pady=10)

    botones = [
        ("📂 REPORTE DE MERCANCIA", seleccionar_reporte),
        ("🔄 ACTUALIZAR CODIGOS", lambda: actualizar_codigos(frame_right)), 
        ("📦 EXPORTAR CODIGOS", lambda: exportar_concentrado_codigos(frame_right)),  
        ("📦 ACTUALIZAR CATALOGO", lambda: actualizar_catalogo(frame_right)),
        ("❌ Salir", root.quit)
    ]

    max_width = 20  # ancho uniforme
    for texto, comando in botones:
        btn = ttk.Button(frame_buttons, text=texto.ljust(max_width), command=comando, style='TButton')
        btn.pack(pady=10, ipadx=10, ipady=10, fill="x")

    root.mainloop()

