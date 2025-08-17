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

# ---------- FUNCIÓN PARA MOSTRAR GIF DE ÉXITO ----------
def mostrar_gif_exitoso(root):
    try:
        gif_path = "resources/imagen_carga.gif"  # 👈 coloca aquí tu gif
        if os.path.exists(gif_path):
            gif = Image.open(gif_path)
            frames = []
            try:
                while True:
                    frame = gif.copy().resize((400, 320), Image.LANCZOS)
                    frames.append(ImageTk.PhotoImage(frame))
                    gif.seek(len(frames))
            except EOFError:
                pass

            overlay = tk.Toplevel(root)
            overlay.title("Guardado exitosamente")
            overlay.geometry("400x220")
            overlay.resizable(False, False)
            overlay.configure(bg="#F7F7F7")

            # Centrar sobre root
            x = root.winfo_x() + int(root.winfo_width()/2) - 200
            y = root.winfo_y() + int(root.winfo_height()/2) - 110
            overlay.geometry(f"400x220+{x}+{y}")

            content_frame = tk.Frame(overlay, bg='#F7F7F7')
            content_frame.pack(expand=True, fill='both')

            gif_label_gif = tk.Label(content_frame, bg='#F7F7F7')
            gif_label_gif.pack(pady=(10, 0))

            msg_label_gif = tk.Label(content_frame,
                                     text="GUARDADO EXITOSAMENTE",
                                     font=("Segoe UI", 14, "bold"),
                                     bg='#F7F7F7',
                                     fg='#228B22')
            msg_label_gif.pack(pady=(10, 10))

            running = {'active': True}
            after_id = None

            def animate(index=0):
                if running['active'] and overlay.winfo_exists():
                    gif_label_gif.config(image=frames[index])
                    nonlocal after_id
                    after_id = overlay.after(70, animate, (index+1) % len(frames))

            animate()

            def stop_and_destroy():
                running['active'] = False
                if after_id:
                    overlay.after_cancel(after_id)
                overlay.destroy()

            # Cierra automáticamente después de 10 segundos
            overlay.after(10000, stop_and_destroy)

    except Exception as e:
        print(f"No se pudo mostrar el gif de éxito: {e}")

# ---------- FUNCIÓN PRINCIPAL ----------
def procesar_reporte(reporte_path):
    global frame
    try:
        # Limpiar barra de progreso previa si existe
        for widget in (globals().get("progress_label"),
                       globals().get("progress_bar"),
                       globals().get("percent_label")):
            try:
                widget.destroy()
            except Exception:
                pass

        # Crear barra de progreso
        global progress_label, progress_var, progress_bar, percent_label
        progress_label = tk.Label(frame, text="Procesando...", font=("Segoe UI", 12), bg="#FFFFFF")
        progress_label.pack(pady=(10, 0))
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100, length=250)
        progress_bar.pack(pady=5)
        percent_label = tk.Label(frame, text="0%", font=("Segoe UI", 10), bg="#FFFFFF")
        percent_label.pack()
        frame.update()

        # Leer archivos base
        df_base = pd.read_excel(BASE_GENERAL)
        df_inspeccion = pd.read_excel(INSPECCION)
        df_reporte = pd.read_excel(reporte_path)

        # --- Construcción del archivo final ---
        items = pd.to_numeric(df_reporte['Num.Parte'], errors='coerce').dropna().astype(int).unique()
        total = len(items)

        # 1. TIPO DE PROCESO
        df_base['EAN'] = df_base['EAN'].astype(str)
        tipo_proceso = []
        for idx, item in enumerate(items):
            match = df_base[df_base['EAN'] == str(item)]
            tipo = match.iloc[0]['CODIGO FORMATO'] if not match.empty and 'CODIGO FORMATO' in match.columns else ''
            tipo_proceso.append(tipo)
            progress_var.set(((idx + 1) / total) * 20); percent_label.config(text=f"{int(progress_var.get())}%"); frame.update()

        # 2. NORMA
        norma = []
        for idx, item in enumerate(items):
            match = df_reporte[df_reporte['Num.Parte'].astype(str) == str(item)]
            n = match.iloc[0]['NOMs'] if not match.empty and 'NOMs' in match.columns else ''
            norma.append(n)
            progress_var.set(20 + ((idx + 1) / total) * 20); percent_label.config(text=f"{int(progress_var.get())}%"); frame.update()

        # 3. DESCRIPCION
        descripcion = []
        for idx, item in enumerate(items):
            match = df_base[df_base['EAN'] == str(item)]
            desc = match.iloc[0]['DESCRIPTION'] if not match.empty and 'DESCRIPTION' in match.columns else ''
            descripcion.append(desc)
            progress_var.set(40 + ((idx + 1) / total) * 20); percent_label.config(text=f"{int(progress_var.get())}%"); frame.update()

        # 4. CRITERIO
        criterio = []
        for idx, item in enumerate(items):
            match = df_inspeccion[df_inspeccion['ITEM'].astype(str) == str(item)]
            crit = match.iloc[0]['INFORMACION FALTANTE'] if not match.empty and 'INFORMACION FALTANTE' in match.columns else ''
            criterio.append(crit)
            progress_var.set(60 + ((idx + 1) / total) * 20); percent_label.config(text=f"{int(progress_var.get())}%"); frame.update()

        # DataFrame final
        df_result = pd.DataFrame({
            'ITEM': items,
            'TIPO DE PROCESO': tipo_proceso,
            'NORMA': norma,
            'DESCRIPCION': descripcion,
            'CRITERIO': criterio
        })

        # ---- Normalizaciones ----
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
            if 'NOM004TEXX' in tipo or 'NOM004' in tipo or 'NOM-004-SE-2021' in norma:
                return 'COSTURA'
            if 'NOM020INS' in norma:
                return 'ADHERIBLE'
            if contiene_numero(norma, normas_adherible):
                return 'ADHERIBLE'
            if contiene_numero(norma, normas_costura):
                return 'COSTURA'
            if norma in ['0', '']:
                return 'SIN NORMA'
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
            if any(p in crit for p in ['CUMPLE', 'C', 'REVISADO']):
                return 'CUMPLE'
            return criterio
        df_result['CRITERIO'] = df_result['CRITERIO'].apply(modificar_criterio)

        # Reglas adicionales
        for idx, row in df_result.iterrows():
            tipo, norma = str(row['TIPO DE PROCESO']).strip(), str(row['NORMA']).strip()
            if norma == '' and tipo != '':
                df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                df_result.at[idx, 'NORMA'] = 'SIN NORMA'
            elif (tipo == '' and norma == '') or (tipo == '0' and norma == '0'):
                df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                df_result.at[idx, 'NORMA'] = 'SIN NORMA'
            elif norma in ['NOM-050-SCFI-2004', 'NOM-015-SCFI-2007']:
                df_result.at[idx, 'TIPO DE PROCESO'] = 'ADHERIBLE'

        # Progreso completo
        progress_var.set(100)
        percent_label.config(text="100%")
        progress_label.config(text="¡Completado!")
        frame.update()
        frame.after(1000, lambda: [progress_label.destroy(), progress_bar.destroy(), percent_label.destroy()])

        # Guardar archivo
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

            # 👇 Aquí muestro el GIF en vez del messagebox
            mostrar_gif_exitoso(root)

        else:
            messagebox.showwarning("Cancelado", "No se guardó el archivo.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")

# ---------- BOTONES Y VENTANA ----------
def seleccionar_reporte():
    ruta = filedialog.askopenfilename(
        title="Seleccionar REPORTE DE MERCANCIA",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if ruta:
        procesar_reporte(ruta)

# Ventana principal
root = tk.Tk()
root.title("Generador TIPO DE PROCESO")
root.geometry("650x480")
root.configure(bg="#FFFFFF")

if __name__ == "__main__":
    frame = tk.Frame(root, bg="#FFFFFF")
    frame.pack(expand=True, fill="both")

    frame_top = tk.Frame(frame, bg="#FFFFFF")
    frame_top.pack(pady=(30, 0), fill="x")

    # Logo
    try:
        logo_path = "resources/logo.png"
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
    label.pack()

    desc = tk.Label(frame, text="Sube el archivo REPORTE DE MERCANCIA y genera el archivo Tipo de proceso.",
                    font=("Segoe UI", 9), bg="#FFFFFF", fg="#282828")
    desc.pack(pady=(0, 15))

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', background='#ECD925', foreground='#282828',
                    font=('Segoe UI', 11, 'bold'), borderwidth=0)
    style.map('TButton', background=[('active', '#ECD925')], foreground=[('active', '#282828')])

    btn_cargar = ttk.Button(frame, text="📂 Subir REPORTE DE MERCANCIA",
                            command=seleccionar_reporte, style='TButton')
    btn_cargar.pack(pady=10, ipadx=10, ipady=5)

    btn_salir = ttk.Button(frame, text="❌ Salir", command=root.quit, style='TButton')
    btn_salir.pack(pady=20, ipadx=5, ipady=3)

    root.mainloop()
