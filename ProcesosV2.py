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

def actualizar_codigos():
    try:
        # Abrir diálogo para seleccionar nuevo archivo con códigos
        root = tk.Tk()
        root.withdraw()
        nuevo_file = filedialog.askopenfilename(
            title="Selecciona el archivo con nuevos códigos",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if not nuevo_file:
            return

        # Cargar archivo base
        if os.path.exists(INSPECCION):
            df_base = pd.read_excel(INSPECCION)
        else:
            # Si no existe, se crea vacío con columna ITEM
            df_base = pd.DataFrame(columns=["ITEM"])

        # Cargar archivo nuevo
        df_nuevo = pd.read_excel(nuevo_file)

        # Validar que tenga columna ITEM
        if "ITEM" not in df_nuevo.columns:
            messagebox.showerror("Error", "El archivo nuevo no contiene la columna 'ITEM'")
            return

        # Quitar duplicados dentro del archivo nuevo
        df_nuevo = df_nuevo.drop_duplicates(subset=["ITEM"])

        # Columnas adicionales que queremos traer si existen
        columnas_extra = ["OBSERVACIONES", "CRITERIO"]
        for col in columnas_extra:
            if col not in df_nuevo.columns:
                df_nuevo[col] = ""  # Crear columna vacía si no existe

        # Filtrar solo ITEMS nuevos
        items_existentes = set(df_base["ITEM"].astype(str))
        df_filtrado = df_nuevo[~df_nuevo["ITEM"].astype(str).isin(items_existentes)]

        if df_filtrado.empty:
            messagebox.showinfo("Actualizar ITEMS", "No hay ITEMS nuevos para agregar.")
            return

        # Agregar solo ITEMS nuevos con sus columnas extra
        df_final = pd.concat([df_base, df_filtrado[["ITEM"] + columnas_extra]], ignore_index=True)

        # Guardar cambios
        df_final.to_excel(INSPECCION, index=False)

        messagebox.showinfo(
            "Actualizar ITEMS",
            f"✅ Se agregaron {len(df_filtrado)} ITEMS nuevos con columnas OBSERVACIONES y CRITERIO.\n📊 Total ahora: {len(df_final)}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema al actualizar los códigos:\n{e}")


def procesar_reporte(reporte_path):
    global frame
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


            # Leer archivos base
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
                    # ✅ Cualquier texto que NO sea vacío ni "N/D" se convierte en REVISADO
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
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', background='#ECD925', foreground='#282828', font=('Segoe UI', 11, 'bold'), borderwidth=0)
    style.map('TButton', background=[('active', '#ECD925')], foreground=[('active', '#282828')])

    btn_cargar = ttk.Button(frame, text="📂 SUBIR REPORTE DE MERCANCIA", command=seleccionar_reporte, style='TButton')
    btn_cargar.pack(pady=10, ipadx=10, ipady=5)

    btn_actualizar = ttk.Button(frame, text="🔄 ACTUALIZAR CODIGOS CUMPLE", command=actualizar_codigos, style='TButton')
    btn_actualizar.pack(pady=10, ipadx=10, ipady=5)

    btn_salir = ttk.Button(frame, text="❌ Salir", command=root.quit, style='TButton')
    btn_salir.pack(pady=20, ipadx=5, ipady=3)

    root.mainloop()