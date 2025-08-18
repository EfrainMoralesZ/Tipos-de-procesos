import os
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from data_manager import DataManager
from item_dialog import ItemDialog, BatchItemDialog
from database_manager_dialog import DatabaseManagerDialog

# Inicializar el gestor de datos
data_manager = DataManager()

def procesar_reporte(reporte_path):
    try:
        # Crear ventana de progreso
        progress_win = tk.Toplevel()
        progress_win.title("Progreso")
        progress_win.geometry("350x120")
        progress_win.resizable(False, False)
        progress_win.transient(root)  # Hacer dependiente de la ventana principal
        progress_win.grab_set()  # Hacer modal
        progress_win.focus_set()  # Dar foco
        progress_win.lift()  # Traer al frente
        progress_win.attributes('-topmost', True)  # Mantener siempre enfrente
        progress_label = tk.Label(progress_win, text="Procesando...", font=("Segoe UI", 12))
        progress_label.pack(pady=10)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_win, variable=progress_var, maximum=100, length=250)
        progress_bar.pack(pady=10)
        percent_label = tk.Label(progress_win, text="0%", font=("Segoe UI", 10))
        percent_label.pack()
        progress_win.update()

        # Obtener datos desde el gestor (en lugar de leer Excel)
        df_base = data_manager.get_base_general_df()
        df_inspeccion = data_manager.get_inspeccion_df()
        df_reporte = pd.read_excel(reporte_path)  # Solo el reporte sigue siendo Excel

        # Verificar que los datos base estén disponibles
        if df_base.empty:
            messagebox.showerror("Error", "No se encontraron datos de base general. Ejecuta la migración primero.")
            progress_win.destroy()
            return
        
        if df_inspeccion.empty:
            messagebox.showerror("Error", "No se encontraron datos de inspección. Ejecuta la migración primero.")
            progress_win.destroy()
            return

        # 1. Columna ITEM (solo números, desde REPORTE DE MERCANCIA columna D "Num.Parte")
        items = pd.to_numeric(df_reporte['Num.Parte'], errors='coerce').dropna().astype(int).unique()
        total = len(items)
        
        # Optimización: Si hay muchos ítems, procesar en lotes
        batch_size = 1000  # Procesar 1000 ítems a la vez
        if total > batch_size:
            print(f"Procesando {total} ítems en lotes de {batch_size}")
        
        # Detectar ítems nuevos
        new_items = data_manager.get_new_items_from_report(items)
        
        # Si hay ítems nuevos, preguntar al usuario si desea agregarlos
        if new_items:
            response = messagebox.askyesno(
                "Ítems Nuevos Detectados", 
                f"Se encontraron {len(new_items)} ítem(s) nuevo(s) que no están en la base de datos.\n\n" +
                f"Ítems: {', '.join(map(str, new_items))}\n\n" +
                "¿Deseas agregar estos ítems a la base de datos?"
            )
            
            if response:
                # Mostrar diálogo para procesar ítems nuevos
                batch_dialog = BatchItemDialog(progress_win, new_items, df_reporte)
                new_items_results = batch_dialog.get_results()
                
                # Agregar ítems nuevos a la base de datos
                for item, item_info in new_items_results.items():
                    data_manager.add_new_item_to_base(
                        item_info['item'],
                        item_info['tipo_proceso'],
                        item_info['norma'],
                        item_info['descripcion']
                    )
                    
                    data_manager.add_new_item_to_inspeccion(
                        item_info['item'],
                        item_info['criterio']
                    )
                
                # Mostrar resumen
                if new_items_results:
                    messagebox.showinfo(
                        "Ítems Agregados", 
                        f"Se agregaron {len(new_items_results)} ítem(s) a la base de datos:\n" +
                        f"{', '.join(map(str, new_items_results.keys()))}"
                    )
                
                # Recargar datos después de agregar nuevos ítems
                df_base = data_manager.get_base_general_df()
                df_inspeccion = data_manager.get_inspeccion_df()
            else:
                # Si el usuario no quiere agregar ítems nuevos, continuar solo con los existentes
                items = [item for item in items if data_manager.item_exists_in_base(str(item))]
                total = len(items)

        # 2. TIPO DE PROCESO (buscar en BASE GENERAL usando índices optimizados)
        tipo_proceso = []
        update_frequency = max(1, total // 20)  # Actualizar cada 5% del progreso
        
        for idx, item in enumerate(items):
            # Usar búsqueda optimizada O(1)
            record = data_manager.get_base_general_record_by_ean(str(item))
            if record and 'CODIGO FORMATO' in record:
                tipo = record['CODIGO FORMATO']
            else:
                tipo = ''
            tipo_proceso.append(tipo)
            
            # Actualizar progreso con menor frecuencia
            if idx % update_frequency == 0 or idx == total - 1:
                progress = ((idx + 1) / total) * 20
                progress_var.set(progress)
                percent_label.config(text=f"{int(progress)}%")
                progress_win.update()

        # 3. NORMA (REPORTE DE MERCANCIA columna D "Num.Parte" a columna P "NOMs")
        norma = []
        for idx, item in enumerate(items):
            match = df_reporte[df_reporte['Num.Parte'].astype(str) == str(item)]
            if not match.empty and 'NOMs' in match.columns:
                n = match.iloc[0]['NOMs']
            else:
                n = ''
            norma.append(n)
            
            # Actualizar progreso con menor frecuencia
            if idx % update_frequency == 0 or idx == total - 1:
                progress = 20 + ((idx + 1) / total) * 20
                progress_var.set(progress)
                percent_label.config(text=f"{int(progress)}%")
                progress_win.update()

        # 4. DESCRIPCION (obtener del reporte para ítems nuevos, de la base para existentes)
        descripcion = []
        for idx, item in enumerate(items):
            # Primero intentar obtener de la base de datos usando búsqueda optimizada
            record = data_manager.get_base_general_record_by_ean(str(item))
            if record and 'DESCRIPTION' in record:
                desc = record['DESCRIPTION']
            else:
                # Si no está en la base, obtener del reporte
                match_reporte = df_reporte[df_reporte['Num.Parte'].astype(str) == str(item)]
                if not match_reporte.empty:
                    # Buscar descripción en múltiples columnas del reporte
                    desc = ''
                    descripcion_columns = [
                        'DESCRIPCION', 'DESCRIPCIÓN', 'DESCRIPTION', 'DESCRIP', 'PRODUCTO', 'NOMBRE',
                        'NOMBRE PRODUCTO', 'DESCRIPCIÓN DEL PRODUCTO', 'NOMBRE DEL PRODUCTO', 
                        'TITULO', 'TÍTULO', 'NOMBRE ARTICULO', 'DESCRIPCION ARTICULO',
                        'Descripción Agente Aduanal'  # Agregar esta columna específica
                    ]
                    
                    for col in descripcion_columns:
                        if col in match_reporte.columns and pd.notna(match_reporte.iloc[0][col]) and str(match_reporte.iloc[0][col]).strip():
                            desc_value = str(match_reporte.iloc[0][col]).strip()
                            if desc_value and desc_value != 'nan' and desc_value != 'None' and len(desc_value) > 2:
                                desc = desc_value
                                break
                else:
                    desc = ''
            descripcion.append(desc)
            
            # Actualizar progreso con menor frecuencia
            if idx % update_frequency == 0 or idx == total - 1:
                progress = 40 + ((idx + 1) / total) * 20
                progress_var.set(progress)
                percent_label.config(text=f"{int(progress)}%")
                progress_win.update()

        # 5. CRITERIO (INSPECCION: ITEM a INFORMACION FALTANTE usando búsqueda optimizada)
        criterio = []
        for idx, item in enumerate(items):
            # Usar búsqueda optimizada O(1)
            record = data_manager.get_inspeccion_record_by_item(str(item))
            if record and 'INFORMACION FALTANTE' in record:
                crit = record['INFORMACION FALTANTE']
            else:
                crit = ''
            criterio.append(crit)
            
            # Actualizar progreso con menor frecuencia
            if idx % update_frequency == 0 or idx == total - 1:
                progress = 60 + ((idx + 1) / total) * 20
                progress_var.set(progress)
                percent_label.config(text=f"{int(progress)}%")
                progress_win.update()

        # Crear DataFrame final
        df_result = pd.DataFrame({
            'ITEM': items,
            'TIPO DE PROCESO': tipo_proceso,
            'NORMA': norma,
            'DESCRIPCION': descripcion,
            'CRITERIO': criterio
        })
        # Actualizar progreso a 80%
        progress_var.set(80)
        percent_label.config(text="80%")
        progress_win.update()

        # Modificaciones finales
        normas_adherible = [
            '015', '050', '004-SE', '024', '141',
            'NOM-015-SCFI-2007', 'NOM-050-SCFI-2004', 'NOM-004-SE-2021', 'NOM-024-SCFI-2013', 'NOM-141-SSA1/SCFI-2012',
            'NOM004TEXX', 'NOM020INS'
        ]
        normas_costura = ['004', '020', 'NOM004', 'NOM020']

        def contiene_numero(texto, lista_numeros):
            texto = str(texto)
            for n in lista_numeros:
                if n in texto:
                    return True
            return False

        def modificar_tipo_proceso(row):
            norma = str(row['NORMA'])
            tipo = str(row['TIPO DE PROCESO'])
            
            # Verificar si los campos están vacíos o son valores nulos
            if (norma == '' or norma == 'nan' or norma == 'None' or norma == '0' or 
                tipo == '' or tipo == 'nan' or tipo == 'None' or tipo == '0'):
                return 'SIN NORMA'
            
            if 'NOM004TEXX' in tipo:
                return 'COSTURA'
            if 'NOM004' in tipo:
                return 'COSTURA'
            if 'NOM-004-SE-2021' in norma:
                return 'COSTURA'
            if 'NOM020INS' in norma:
                return 'ADHERIBLE'
            if contiene_numero(norma, ['015', '050', '004-SE', '024', '141']) or any(n in norma for n in normas_adherible):
                return 'ADHERIBLE'
            if contiene_numero(norma, ['004', '020']) and not ('NOM004TEXX' in tipo or 'NOM020INS' in norma):
                return 'COSTURA'
            if any(n in norma for n in normas_costura) and not ('NOM004TEXX' in tipo or 'NOM020INS' in norma):
                return 'COSTURA'
            if norma == 'N/D':
                return ''
            return row['TIPO DE PROCESO']
        df_result['TIPO DE PROCESO'] = df_result.apply(modificar_tipo_proceso, axis=1)

        def modificar_norma(norma):
            norma_str = str(norma)
            if (norma_str == '0' or norma_str == '' or norma_str == 'nan' or 
                norma_str == 'None' or pd.isna(norma)):
                return 'SIN NORMA'
            elif norma_str == 'N/D':
                return ''
            return norma_str
        df_result['NORMA'] = df_result['NORMA'].apply(modificar_norma)

        def modificar_criterio(criterio):
            crit = str(criterio).strip().upper()
            # Si contiene 'NO CUMPLE' no modificar
            if 'NO CUMPLE' in crit:
                return criterio
            # Si contiene 'CUMPLE', 'C', 'REVISADO', 'CUMPLE NOM-050', etc.
            palabras_cumple = ['CUMPLE', 'C', 'REVISADO']
            for palabra in palabras_cumple:
                if palabra in crit:
                    return 'CUMPLE'
            return criterio
        df_result['CRITERIO'] = df_result['CRITERIO'].apply(modificar_criterio)

        # Verificación final: si cualquiera de los campos está vacío, ambos deben ser "SIN NORMA"
        for idx, row in df_result.iterrows():
            tipo = str(row['TIPO DE PROCESO']).strip() if not pd.isna(row['TIPO DE PROCESO']) else ''
            norma = str(row['NORMA']).strip() if not pd.isna(row['NORMA']) else ''
            
            # Si cualquiera de los dos campos está vacío o es "SIN NORMA", ambos deben ser "SIN NORMA"
            # PERO NO BORRAR LA DESCRIPCIÓN
            if (tipo == '' or norma == '' or tipo == '0' or norma == '0' or 
                tipo == 'nan' or norma == 'nan' or tipo == 'None' or norma == 'None' or
                tipo == 'SIN NORMA' or norma == 'SIN NORMA'):
                df_result.at[idx, 'TIPO DE PROCESO'] = 'SIN NORMA'
                df_result.at[idx, 'NORMA'] = 'SIN NORMA'
                # La descripción se mantiene intacta
        # Actualizar progreso a 90%
        progress_var.set(100)
        percent_label.config(text="100%")
        progress_win.update()

        # Guardar archivo final
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar archivo TIPO DE PROCESO",
            initialfile="TIPO DE PROCESO.xlsx"
        )

        if save_path:
            # Usar el gestor de datos para exportar
            data_manager.export_to_excel(df_result, save_path)

            # Actualizar historial usando el gestor de datos
            data_manager.add_to_historial(df_result.to_dict('records'))

            # Actualizar progreso a 100%
            progress_var.set(100)
            percent_label.config(text="100%")
            progress_label.config(text="¡Completado!")
            progress_win.update()
            progress_win.after(1200, progress_win.destroy)

            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{save_path}\nHistorial actualizado.")
        else:
            progress_win.destroy()
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

def verificar_datos():
    """Verificar que los datos base estén disponibles"""
    info = data_manager.get_data_info()
    
    if not info['base_general']['exists'] or info['base_general']['records'] == 0:
        messagebox.showwarning(
            "Datos no encontrados", 
            "No se encontraron datos de base general.\n\nEjecuta 'python migrate_excel.py' para migrar los archivos Excel existentes."
        )
        return False
    
    if not info['inspeccion']['exists'] or info['inspeccion']['records'] == 0:
        messagebox.showwarning(
            "Datos no encontrados", 
            "No se encontraron datos de inspección.\n\nEjecuta 'python migrate_excel.py' para migrar los archivos Excel existentes."
        )
        return False
    
    return True

# Crear ventana principal con fondo blanco, botones dorados y letras oscuras
root = tk.Tk()
root.title("Generador TIPO DE PROCESO")
root.geometry("520x400")
root.configure(bg="#FFFFFF")

# Establecer ícono de la aplicación
try:
    icon_path = os.path.join("resources", "LogoX.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    else:
        print(f"Ícono no encontrado en la ruta: {icon_path}")
except Exception as e:
    print(f"Error cargando el ícono: {e}")

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
            logo_img_raw = logo_img_raw.resize((150, 100), Image.LANCZOS)
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

    # Verificar datos al inicio
    if not verificar_datos():
        # Si no hay datos, mostrar información adicional
        info_label = tk.Label(frame, text="⚠️ Ejecuta la migración primero", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#FF6B35")
        info_label.pack(pady=(0, 10))

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', background='#ECD925', foreground='#282828', font=('Segoe UI', 11, 'bold'), borderwidth=0)
    style.map('TButton', background=[('active', '#ECD925')], foreground=[('active', '#282828')])

    btn_cargar = ttk.Button(frame, text="📂 Subir REPORTE DE MERCANCIA", command=seleccionar_reporte, style='TButton')
    btn_cargar.pack(pady=10, ipadx=10, ipady=5)

    btn_gestor = ttk.Button(frame, text="🗄️ Gestor de Bases de Datos", command=lambda: DatabaseManagerDialog(root).show(), style='TButton')
    btn_gestor.pack(pady=5, ipadx=10, ipady=5)

    btn_salir = ttk.Button(frame, text="❌ Salir", command=root.quit, style='TButton')
    btn_salir.pack(pady=20, ipadx=5, ipady=3)

    root.mainloop()
