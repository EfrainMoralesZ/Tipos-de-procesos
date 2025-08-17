
import os
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Archivos fijos
BASE_GENERAL = "BASE DECATHLON GENERAL ADVANCE II.xlsx"
INSPECCION = "INSPECCION.xlsx"
HISTORIAL = "HISTORIAL_PROCESOS.xlsx"

def procesar_reporte(reporte_path):
    try:
        # Procesamiento de datos y guardado de archivo
        # Leer archivos base
        df_base = pd.read_excel(BASE_GENERAL)
        df_inspeccion = pd.read_excel(INSPECCION)
        df_reporte = pd.read_excel(reporte_path)

        # 1. Columna ITEM (solo números, desde REPORTE DE MERCANCIA columna D "Num.Parte")
        items = pd.to_numeric(df_reporte['Num.Parte'], errors='coerce').dropna().astype(int).unique()

        # 2. TIPO DE PROCESO (buscar en BASE GENERAL DE DECATHLON columna A "EAN" y X "CODIGO FORMATO")
        df_base['EAN'] = df_base['EAN'].astype(str)
        tipo_proceso = []
        for item in items:
            match = df_base[df_base['EAN'] == str(item)]
            if not match.empty:
                tipo = match.iloc[0]['CODIGO FORMATO'] if 'CODIGO FORMATO' in match.columns else ''
            else:
                tipo = ''
            tipo_proceso.append(tipo)

        # 3. NORMA (REPORTE DE MERCANCIA columna D "Num.Parte" a columna P "NOMs")
        norma = []
        for item in items:
            match = df_reporte[df_reporte['Num.Parte'].astype(str) == str(item)]
            if not match.empty and 'NOMs' in match.columns:
                n = match.iloc[0]['NOMs']
            else:
                n = ''
            norma.append(n)

        # 4. DESCRIPCION (BASE GENERAL DE DECATHLON columna A "EAN" a B "DESCRIPTION")
        descripcion = []
        for item in items:
            match = df_base[df_base['EAN'] == str(item)]
            if not match.empty and 'DESCRIPTION' in match.columns:
                desc = match.iloc[0]['DESCRIPTION']
            else:
                desc = ''
            descripcion.append(desc)

        # 5. CRITERIO (INSPECCION: ITEM a INFORMACION FALTANTE)
        criterio = []
        for item in items:
            match = df_inspeccion[df_inspeccion['ITEM'].astype(str) == str(item)]
            if not match.empty and 'INFORMACION FALTANTE' in match.columns:
                crit = match.iloc[0]['INFORMACION FALTANTE']
            else:
                crit = ''
            criterio.append(crit)

        # Crear DataFrame final
        df_result = pd.DataFrame({
            'ITEM': items,
            'TIPO DE PROCESO': tipo_proceso,
            'NORMA': norma,
            'DESCRIPCION': descripcion,
            'CRITERIO': criterio
        })

        # Modificaciones finales
        normas_adherible = ['NOM050', 'NOM024', 'NOM0141', 'NOM0189', 'NOM015', 'NOM004TEXX', 'NOM020INS']
        normas_costura = ['NOM004', 'NOM020']
        def modificar_tipo_proceso(row):
            if row['NORMA'] in normas_adherible:
                return 'ADHERIBLE'
            elif row['NORMA'] in normas_costura:
                return 'COSTURA'
            elif str(row['NORMA']) == '0':
                return 'SIN NORMA'
            elif str(row['NORMA']) == 'N/D':
                return ''
            return row['TIPO DE PROCESO']
        df_result['TIPO DE PROCESO'] = df_result.apply(modificar_tipo_proceso, axis=1)

        def modificar_norma(norma):
            if str(norma) == '0':
                return 'SIN NORMA'
            elif str(norma) == 'N/D':
                return ''
            return norma
        df_result['NORMA'] = df_result['NORMA'].apply(modificar_norma)

        def modificar_criterio(criterio):
            if str(criterio).strip().upper() in ['C', 'CUMPLE', 'REVISADO']:
                return 'CUMPLE'
            return criterio
        df_result['CRITERIO'] = df_result['CRITERIO'].apply(modificar_criterio)

        # Guardar archivo final
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar archivo TIPO DE PROCESO",
            initialfile="TIPO DE PROCESO.xlsx"
        )

        if save_path:
            df_result.to_excel(save_path, index=False)

            # Actualizar historial
            if Path(HISTORIAL).exists():
                df_hist = pd.read_excel(HISTORIAL)
                df_final = pd.concat([df_hist, df_result]).drop_duplicates(subset=["ITEM"])
            else:
                df_final = df_result.copy()
            df_final.to_excel(HISTORIAL, index=False)

            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{save_path}\nHistorial actualizado.")
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

# Crear ventana principal con fondo blanco, botones dorados y letras oscuras
root = tk.Tk()
root.title("Generador TIPO DE PROCESO")
root.geometry("520x360")
root.configure(bg="#FFFFFF")


if __name__ == "__main__":
    # Frame principal
    frame = tk.Frame(root, bg="#FFFFFF")
    frame.pack(expand=True, fill="both")

    # Frame superior para logo y título
    frame_top = tk.Frame(frame, bg="#FFFFFF")
    frame_top.pack(pady=(30, 0), fill="x")

    logo_label = None
    try:
        logo_path = "resources/logo.png"  # Cambia esto si tu logo tiene otro nombre o ruta
        if os.path.exists(logo_path):
            logo_img_raw = Image.open(logo_path)
            logo_img_raw = logo_img_raw.resize((100, 100), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(logo_img_raw)
            logo_label = tk.Label(frame_top, image=logo_img, bg="#FFFFFF")
            logo_label.image = logo_img  # Mantener referencia
            logo_label.pack(side="top", pady=(0, 10))
        else:
            print(f"Logo no encontrado en la ruta: {logo_path}")
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    try:
        logo_img_raw = Image.open("resources/Logo.png")
        logo_img_raw = logo_img_raw.resize((100, 100), Image.ANTIALIAS)
        logo_img = ImageTk.PhotoImage(logo_img_raw)
        logo_label = tk.Label(frame_top, image=logo_img, bg="#FFFFFF")
        logo_label.image = logo_img
        logo_label.pack(pady=30, padx=10)
    except Exception:
        pass

    label = tk.Label(frame_top, text="Generador de archivo TIPO DE PROCESO", font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#282828")
    label.pack(pady=0, padx=10)

    desc = tk.Label(frame, text="Sube el archivo REPORTE DE MERCANCIA y genera el archivo Tipo de proceso.", font=("Segoe UI", 9), bg="#FFFFFF", fg="#282828")
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
