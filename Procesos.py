import os
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sys
import json
from Formato import exportar_excel




if getattr(sys, 'frozen', False):
    # Cuando está compilado en .exe
    BASE_PATH = sys._MEIPASS
else:
    # Cuando se ejecuta desde Python
    BASE_PATH = os.path.dirname(__file__)

# Archivos fijos
BASE_GENERAL = os.path.join(BASE_PATH, "archivos","BASE DECATHLON GENERAL ADVANCE II.xlsx")
INSPECCION = os.path.join(BASE_PATH, "archivos","INSPECCION.xlsx")
HISTORIAL = os.path.join(BASE_PATH, "archivos","HISTORIAL_PROCESOS.xlsx")

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
            df_inspeccion = cargar_json("inspeccion.json")
            df_reporte = pd.read_excel(reporte_path)  # El reporte sigue siendo cargado por el usuario

            # 1. Columna ITEM
            items = pd.to_numeric(df_reporte['Num.Parte'], errors='coerce').dropna().astype(int).unique()
            total = len(items)

            # 2. TIPO DE PROCESO
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

            # 3. NORMA
            norma = []
            for idx, item in enumerate(items):
                match = df_reporte[df_reporte['Num.Parte'].astype(str) == str(item)]
                n = match.iloc[0]['NOMs'] if not match.empty and 'NOMs' in match.columns else ''
                norma.append(n)
                progress = 20 + ((idx + 1) / total) * 20
                progress_var.set(progress)
                percent_label.config(text=f"{int(progress)}%")
                frame.update()

            # 4. DESCRIPCION
            descripcion = []
            for idx, item in enumerate(items):
                match = df_base[df_base['EAN'] == str(item)]
                desc = match.iloc[0]['DESCRIPTION'] if not match.empty and 'DESCRIPTION' in match.columns else ''
                descripcion.append(desc)
                progress = 40 + ((idx + 1) / total) * 20
                progress_var.set(progress)
                percent_label.config(text=f"{int(progress)}%")
                frame.update()

            # 5. CRITERIO
            criterio = []
            for idx, item in enumerate(items):
                match = df_inspeccion[df_inspeccion['ITEM'].astype(str) == str(item)]
                crit = match.iloc[0]['INFORMACION FALTANTE'] if not match.empty and 'INFORMACION FALTANTE' in match.columns else ''
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

            # Reglas de modificación
            normas_adherible = [
                '015', '050', '004-SE', '024', '141',
                'NOM-015-SCFI-2007', 'NOM-050-SCFI-2004', 'NOM-004-SE-2021',
                'NOM-024-SCFI-2013', 'NOM-141-SSA1/SCFI-2012',
                'NOM004TEXX', 'NOM020INS'
            ]
            normas_costura = ['004', '020', 'NOM004', 'NOM020','NOM004TEXX','NOM0004TEXX']

            def contiene_numero(texto, lista_numeros):
                texto = str(texto)
                return any(n in texto for n in lista_numeros)

            def modificar_tipo_proceso(row):
                norma = str(row['NORMA'])
                tipo = str(row['TIPO DE PROCESO'])
                if 'NOM004TEXX' in tipo or 'NOM004' in tipo or 'NOM-004-SE-2021' in norma:
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
                if any(palabra in crit for palabra in ['CUMPLE', 'C', 'REVISADO']):
                    return 'CUMPLE'
                return criterio
            df_result['CRITERIO'] = df_result['CRITERIO'].apply(modificar_criterio)

            for idx, row in df_result.iterrows():
                tipo = str(row['TIPO DE PROCESO']).strip() if not pd.isna(row['TIPO DE PROCESO']) else ''
                norma = str(row['NORMA']).strip() if not pd.isna(row['NORMA']) else ''
                if (norma == '' and tipo != '') or ((tipo == '' and norma == '') or (tipo == '0' and norma == '0')):
                    df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                    df_result.at[idx, 'NORMA'] = 'SIN NORMA'
                elif norma in ['NOM-050-SCFI-2004', 'NOM-015-SCFI-2007']:
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

    btn_cargar = ttk.Button(frame, text="📂 Subir REPORTE DE MERCANCIA", command=seleccionar_reporte, style='TButton')
    btn_cargar.pack(pady=10, ipadx=10, ipady=5)

    btn_salir = ttk.Button(frame, text="❌ Salir", command=root.quit, style='TButton')
    btn_salir.pack(pady=20, ipadx=5, ipady=3)

    root.mainloop()