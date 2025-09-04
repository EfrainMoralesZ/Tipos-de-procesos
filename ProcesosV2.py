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
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.utils import ImageReader

if getattr(sys, 'frozen', False):
    # Cuando está compilado en .exe
    BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
else:
    # Cuando se ejecuta desde Python
    BASE_PATH = os.path.dirname(__file__)

# Configuración de rutas y archivos
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_PATH, "config.json")

# 👈 NUEVO: SISTEMA DE CONTADOR DE ARCHIVOS PROCESADOS
ARCHIVOS_PROCESADOS_FILE = os.path.join(BASE_PATH, "archivos_procesados.json")
CODIGOS_CUMPLE = "codigos_cumple.xlsx"   # Ruta del Excel
CODIGOS_JSON = "codigos_cumple.json"     # Ruta del respaldo JSON


def registrar_archivo_procesado(nombre_archivo, fecha_proceso):
    """Registra un archivo procesado en el sistema de estadísticas"""
    try:
        if os.path.exists(ARCHIVOS_PROCESADOS_FILE):
            with open(ARCHIVOS_PROCESADOS_FILE, 'r', encoding='utf-8') as f:
                archivos = json.load(f)
        else:
            archivos = []
        
        # Agregar nuevo archivo
        archivo_info = {
            "nombre": nombre_archivo,
            "fecha_proceso": fecha_proceso,
            "fecha_archivo": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Verificar si ya existe para no duplicar
        if not any(a["nombre"] == nombre_archivo for a in archivos):
            archivos.append(archivo_info)
            
            # Guardar archivo actualizado
            with open(ARCHIVOS_PROCESADOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(archivos, f, indent=4, ensure_ascii=False)
            
            print(f"[OK] Archivo registrado: {nombre_archivo}")
        else:
            print(f"[INFO] Archivo ya registrado: {nombre_archivo}")
            
    except Exception as e:
        print(f"[ERROR] Error registrando archivo: {e}")

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

def cargar_configuracion():
    """Carga la configuración desde el archivo JSON"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            config_default = {
                "rutas": {
                    "base_general": "",
                    "codigos_cumple": "",
                    "historial": ""
                }
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_default, f, indent=4)
            return config_default
    except Exception as e:
        print(f"Error al cargar configuración: {str(e)}")
        return None

def guardar_configuracion(config):
    """Guarda la configuración en el archivo JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {str(e)}")
        return False

def configurar_rutas():
    """Permite al usuario configurar las rutas necesarias"""
    config = cargar_configuracion()
    if config is None:
        config = {"rutas": {}}
    
    # Crear ventana de selección
    ventana = tk.Toplevel()
    ventana.title("Configurar Rutas")
    ventana.geometry("500x400")
    ventana.configure(bg="#FFFFFF")
    ventana.grab_set()  # Hacer la ventana modal
    
    def seleccionar_archivo(tipo):
        archivo = filedialog.askopenfilename(
            title=f"Seleccionar {tipo}",
            filetypes=[("Archivos Excel", "*.xlsx")]
        )
        if archivo:
            config["rutas"][tipo] = archivo
            
            # 👈 CONVERSIÓN AUTOMÁTICA A JSON PARA MEJOR RENDIMIENTO
            try:
                df = pd.read_excel(archivo)
                json_path = archivo.replace(".xlsx", ".json")
                df.to_json(json_path, orient="records", force_ascii=False, indent=4)
                print(f"[OK] Convertido a JSON: {json_path}")
                messagebox.showinfo("Conversión exitosa", f"Archivo convertido a JSON para mejor rendimiento:\n{os.path.basename(json_path)}")
            except Exception as e:
                print(f"[ERROR] Error convirtiendo a JSON: {e}")
                messagebox.showwarning("Advertencia", f"No se pudo convertir a JSON:\n{str(e)}\nLa aplicación funcionará con Excel (más lento)")
            
            if tipo == "codigos_cumple":
                lbl_codigos.config(text=f"Códigos de cumplimiento: {os.path.basename(archivo)}")
            elif tipo == "base_general":
                lbl_base.config(text=f"Base general: {os.path.basename(archivo)}")
            elif tipo == "historial":
                lbl_historial.config(text=f"Historial: {os.path.basename(archivo)}")
            guardar_configuracion(config)
    
    # Etiquetas y botones
    tk.Label(ventana, text="Configuración de Rutas", font=("Segoe UI", 12, "bold"), 
             bg="#FFFFFF", fg="#282828").pack(pady=20)
    
    # Frame para códigos de cumplimiento
    frame_codigos = tk.Frame(ventana, bg="#FFFFFF")
    frame_codigos.pack(fill="x", padx=20, pady=10)
    lbl_codigos = tk.Label(frame_codigos, text="Códigos de cumplimiento: No seleccionado", 
                          bg="#FFFFFF", fg="#282828", anchor="w")
    lbl_codigos.pack(side="left")
    tk.Button(frame_codigos, text="Seleccionar", command=lambda: seleccionar_archivo("codigos_cumple"),
             bg="#ECD925", fg="#282828").pack(side="right")
    
    # Frame para base general
    frame_base = tk.Frame(ventana, bg="#FFFFFF")
    frame_base.pack(fill="x", padx=20, pady=10)
    lbl_base = tk.Label(frame_base, text="Base general: No seleccionado", 
                       bg="#FFFFFF", fg="#282828", anchor="w")
    lbl_base.pack(side="left")
    tk.Button(frame_base, text="Seleccionar", command=lambda: seleccionar_archivo("base_general"),
             bg="#ECD925", fg="#282828").pack(side="right")
    
    # Frame para historial
    frame_historial = tk.Frame(ventana, bg="#FFFFFF")
    frame_historial.pack(fill="x", padx=20, pady=10)
    lbl_historial = tk.Label(frame_historial, text="Historial: No seleccionado", 
                            bg="#FFFFFF", fg="#282828", anchor="w")
    lbl_historial.pack(side="left")
    tk.Button(frame_historial, text="Seleccionar", command=lambda: seleccionar_archivo("historial"),
             bg="#ECD925", fg="#282828").pack(side="right")
    
    # Actualizar etiquetas con rutas existentes
    if "codigos_cumple" in config["rutas"] and config["rutas"]["codigos_cumple"]:
        lbl_codigos.config(text=f"Códigos de cumplimiento: {os.path.basename(config['rutas']['codigos_cumple'])}")
    if "base_general" in config["rutas"] and config["rutas"]["base_general"]:
        lbl_base.config(text=f"Base general: {os.path.basename(config['rutas']['base_general'])}")
    if "historial" in config["rutas"] and config["rutas"]["historial"]:
        lbl_historial.config(text=f"Historial: {os.path.basename(config['rutas']['historial'])}")
    
    # Botón cerrar
    tk.Button(ventana, text="Cerrar", command=ventana.destroy,
             bg="#ECD925", fg="#282828").pack(pady=20)
    
    ventana.wait_window()  # Esperar a que se cierre la ventana
    return config["rutas"]

# Cargar configuración inicial
config = cargar_configuracion()
RUTAS = config.get("rutas", {}) if config else {}

# Si no hay rutas configuradas, pedir al usuario que las configure
if not all(RUTAS.values()):
    if messagebox.askyesno("Configuración", "No se han configurado todas las rutas necesarias. ¿Desea configurarlas ahora?"):
        RUTAS = configurar_rutas()

# Definir variables globales para las rutas
ARCHIVO_CODIGOS = RUTAS.get("codigos_cumple", "")
ARCHIVO_JSON = ARCHIVO_CODIGOS.replace(".xlsx", ".json") if ARCHIVO_CODIGOS else ""
BASE_GENERAL = RUTAS.get("base_general", "")
HISTORIAL = RUTAS.get("historial", "")
if os.path.exists(ARCHIVO_CODIGOS):
    try:
        df_codigos_cumple = pd.read_excel(ARCHIVO_CODIGOS)
        print(f"Archivo cargado: {ARCHIVO_CODIGOS}")
        print(f"Número de registros: {len(df_codigos_cumple)}")
    except Exception as e:
        print(f"Error al cargar {ARCHIVO_CODIGOS}: {str(e)}")
        df_codigos_cumple = pd.DataFrame({"ITEM": [], "OBSERVACIONES": [], "CRITERIO": []})
else:
    print(f"Archivo no encontrado: {ARCHIVO_CODIGOS}")
    df_codigos_cumple = pd.DataFrame({"ITEM": [], "OBSERVACIONES": [], "CRITERIO": []})


def abrir_editor_codigos(parent=None):
    global df_codigos_cumple
    
    # Recargar datos del archivo
    try:
        if os.path.exists(ARCHIVO_CODIGOS):
            df_codigos_cumple = pd.read_excel(ARCHIVO_CODIGOS)
            print(f"Abriendo editor - Registros cargados: {len(df_codigos_cumple)}")
        elif os.path.exists(ARCHIVO_JSON):
            df_codigos_cumple = pd.read_json(ARCHIVO_JSON)
            print(f"Abriendo editor - Registros cargados desde JSON: {len(df_codigos_cumple)}")
        else:
            print(f"No se encontró ningún archivo de datos en: {ARCHIVO_CODIGOS}")
            df_codigos_cumple = pd.DataFrame({"ITEM": [], "OBSERVACIONES": [], "CRITERIO": []})
    except Exception as e:
        print(f"Error al cargar los datos: {str(e)}")
        messagebox.showerror("Error", f"Error al cargar los datos: {str(e)}")
        df_codigos_cumple = pd.DataFrame({"ITEM": [], "OBSERVACIONES": [], "CRITERIO": []})
    
    ventana = tk.Toplevel(parent) if parent else tk.Toplevel()
    ventana.title("Editor de Códigos")
    ventana.geometry("800x500")
    ventana.grab_set()


    # --- Buscador con autocompletado ---
    frame_search = tk.Frame(ventana, bg="#FFFFFF")
    frame_search.pack(fill="x", pady=(10, 0))

    tk.Label(frame_search, text="Buscar:").pack(side="left", padx=(5, 2))
    search_var = tk.StringVar()
    entry_search = tk.Entry(frame_search, textvariable=search_var, width=30)
    entry_search.pack(side="left", padx=(0, 5))

    # Listbox para sugerencias
    listbox_suggest = tk.Listbox(frame_search, height=5, width=40,
                               bg="#FFFFFF", fg="#282828", selectbackground="#ECD925",
                               selectforeground="#282828")
    listbox_suggest.pack(side="left", padx=(0, 5))
    listbox_suggest.pack_forget()

    # Crear frame contenedor para la tabla y scrollbar
    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Tabla con los datos
    columnas = ["ITEM", "OBSERVACIONES", "CRITERIO"]
    tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15, style="Custom.Treeview")
    
    # Configurar columnas
    tree.heading("ITEM", text="ITEM")
    tree.heading("OBSERVACIONES", text="OBSERVACIONES")
    tree.heading("CRITERIO", text="CRITERIO")
    
    # Ajustar anchos de columnas
    tree.column("ITEM", width=100)
    tree.column("OBSERVACIONES", width=400)
    tree.column("CRITERIO", width=250)
    
    # Scrollbar vertical
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Empaquetar tabla y scrollbar
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Cargar datos en la tabla
    if not df_codigos_cumple.empty:
        print("Cargando datos en la tabla...")
        for index, row in df_codigos_cumple.iterrows():
            values = [str(row["ITEM"]), str(row["OBSERVACIONES"]), str(row.get("CRITERIO", ""))]
            tree.insert("", "end", values=values)
        print(f"Se cargaron {len(df_codigos_cumple)} registros en la tabla")
    
    # Llenar la tabla con datos existentes
    for index, row in df_codigos_cumple.iterrows():
        values = [row["ITEM"], row["OBSERVACIONES"], row.get("CRITERIO", "")]
        tree.insert("", "end", values=values)
    tree.pack(fill="both", expand=True, pady=10)

    # Llenar tabla
    def cargar_tabla(filtrado=None):
        for row in tree.get_children():
            tree.delete(row)
        df = filtrado if filtrado is not None else df_codigos_cumple
        for _, fila in df.iterrows():
            tree.insert("", "end", values=list(fila))
    cargar_tabla()

    # --- Funciones de autocompletado ---
    def update_suggestions(event=None):
        text = search_var.get().lower()
        if not text:
            listbox_suggest.pack_forget()
            cargar_tabla()
            return
        # Buscar coincidencias en ITEM y OBSERVACIONES
        suggestions = []
        for _, row in df_codigos_cumple.iterrows():
            item_str = str(row["ITEM"])
            obs_str = str(row["OBSERVACIONES"]) if "OBSERVACIONES" in row else ""
            if text in item_str.lower() or text in obs_str.lower():
                suggestions.append(f"{item_str} | {obs_str}")
        if suggestions:
            listbox_suggest.delete(0, tk.END)
            for s in suggestions:
                listbox_suggest.insert(tk.END, s)
            listbox_suggest.pack(side="left", padx=(0, 5))
        else:
            listbox_suggest.pack_forget()
        # Filtrar tabla
        mask = df_codigos_cumple.apply(lambda r: text in str(r["ITEM"]).lower() or text in str(r["OBSERVACIONES"]).lower(), axis=1)
        cargar_tabla(df_codigos_cumple[mask])

    def on_suggestion_select(event):
        if listbox_suggest.curselection():
            value = listbox_suggest.get(listbox_suggest.curselection())
            item_val = value.split("|")[0].strip()
            # Seleccionar en la tabla
            for row in tree.get_children():
                vals = tree.item(row, "values")
                if str(vals[0]) == item_val:
                    tree.selection_set(row)
                    tree.see(row)
                    break
            entry_search.delete(0, tk.END)
            entry_search.insert(0, item_val)
            listbox_suggest.pack_forget()

    entry_search.bind("<KeyRelease>", update_suggestions)
    listbox_suggest.bind("<<ListboxSelect>>", on_suggestion_select)

    # --- Botones de navegación ---
    frame_nav = tk.Frame(ventana)
    frame_nav.pack(fill="x", pady=(0, 5))
    def ir_al_principio():
        children = tree.get_children()
        if children:
            tree.selection_set(children[0])
            tree.see(children[0])

    def ir_al_final():
        children = tree.get_children()
        if children:
            tree.selection_set(children[-1])
            tree.see(children[-1])

    tk.Button(frame_nav, text="⏮ Ir al principio", command=ir_al_principio,
             bg="#ECD925", fg="#282828", activebackground="#f3e55b",
             activeforeground="#282828").pack(side="left", padx=5)
    tk.Button(frame_nav, text="Ir al final ⏭", command=ir_al_final,
             bg="#ECD925", fg="#282828", activebackground="#f3e55b",
             activeforeground="#282828").pack(side="left", padx=5)

    # Editar item seleccionado
    def editar_item():
        seleccion = tree.focus()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un ITEM para editar.")
            return
        valores = tree.item(seleccion, "values")
        item_id = valores[0]

        actualizar_observacion_interactiva(item_id)

        cargar_tabla()

    # Eliminar item
    def eliminar_item():
        seleccion = tree.focus()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un ITEM para eliminar.")
            return
        valores = tree.item(seleccion, "values")
        item_id = valores[0]

        global df_codigos_cumple
        mask = df_codigos_cumple["ITEM"] == int(item_id)
        df_codigos_cumple = df_codigos_cumple[~mask]
        guardar_cambios()
        cargar_tabla()

    # Agregar item nuevo
    def agregar_item():
        ventana_add = tk.Toplevel(ventana)
        ventana_add.title("➕ Agregar ITEM")
        ventana_add.geometry("400x250")
        ventana_add.grab_set()
        ventana_add.configure(bg="#FFFFFF")

        tk.Label(ventana_add, text="ITEM:", bg="#FFFFFF", fg="#282828").pack(pady=5)
        entry_item = tk.Entry(ventana_add, bg="#FFFFFF", fg="#282828", insertbackground="#282828")
        entry_item.pack()

        tk.Label(ventana_add, text="Observación:", bg="#FFFFFF", fg="#282828").pack(pady=5)
        entry_obs = tk.Entry(ventana_add, width=40, bg="#FFFFFF", fg="#282828", insertbackground="#282828")
        entry_obs.pack()

        tk.Label(ventana_add, text="CRITERIO:", bg="#FFFFFF", fg="#282828").pack(pady=5)
        entry_criterio = tk.Entry(ventana_add, width=40, bg="#FFFFFF", fg="#282828", insertbackground="#282828")
        entry_criterio.pack()

        def guardar_nuevo():
            try:
                item_val = int(entry_item.get())
            except:
                messagebox.showerror("Error", "El ITEM debe ser numérico.")
                return

            obs_val = entry_obs.get()
            criterio_val = entry_criterio.get()  # 👈 Ahora sí lo leemos antes

            # Verificar duplicado
            if item_val in df_codigos_cumple["ITEM"].tolist():
                messagebox.showwarning("Duplicado", "Ese ITEM ya existe. Se actualizará la observación y criterio.")
                df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item_val, "OBSERVACIONES"] = obs_val
                df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item_val, "CRITERIO"] = criterio_val
            else:
                # Agregar nuevo registro
                df_codigos_cumple.loc[len(df_codigos_cumple)] = {
                    "ITEM": item_val,
                    "OBSERVACIONES": obs_val,
                    "CRITERIO": criterio_val
                }

            guardar_cambios()   # tu función para guardar el Excel
            cargar_tabla()      # tu función para refrescar la tabla en la UI
            ventana_add.destroy()

        tk.Button(ventana_add, text="Guardar", command=guardar_nuevo, 
                bg="#ECD925", fg="#282828", activebackground="#f3e55b",
                activeforeground="#282828").pack(pady=10)

    # Subir Excel y fusionar
    def subir_excel():
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        try:
            df_subido = pd.read_excel(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {str(e)}")
            return

        # Verificamos que existan las columnas necesarias
        columnas_necesarias = ["ITEM", "OBSERVACIONES", "CRITERIO"]
        for col in columnas_necesarias:
            if col not in df_subido.columns:
                messagebox.showerror("Error", f"Falta la columna '{col}' en el archivo")
                return

        # 🔎 Forzar que ITEM sea numérico
        df_subido["ITEM"] = pd.to_numeric(df_subido["ITEM"], errors="coerce")

        # 🔎 Limpiar duplicados en el archivo nuevo
        df_subido = df_subido.drop_duplicates(subset=["ITEM", "OBSERVACIONES", "CRITERIO"])

        global df_codigos_cumple
        # 🔎 Convertir también los existentes a número
        df_codigos_cumple["ITEM"] = pd.to_numeric(df_codigos_cumple["ITEM"], errors="coerce")

        items_existentes = set(df_codigos_cumple["ITEM"].tolist())
        nuevos_items = []

        # 🔄 Recorrer cada fila del Excel subido
        for _, row in df_subido.iterrows():
            item = row["ITEM"]
            obs_nueva = str(row.get("OBSERVACIONES", "")).strip()
            criterio_nuevo = str(row.get("CRITERIO", "")).strip()

            # Verificar si el item es válido
            if item is None or str(item).strip() == '' or str(item).lower() == 'nan':
                continue  # saltar filas sin item

            if item in items_existentes:
                try:
                    # Usar método más directo para evitar errores de tipo
                    mask = df_codigos_cumple["ITEM"] == item
                    fila_base = df_codigos_cumple[mask]
                    if len(fila_base) > 0:
                        try:
                            # Usar método más directo - verificar si es DataFrame
                            if hasattr(fila_base, 'iloc') and len(fila_base) > 0:
                                obs_actual = str(fila_base.iloc[0]["OBSERVACIONES"]).strip()
                                criterio_actual = str(fila_base.iloc[0]["CRITERIO"]).strip()
                            else:
                                obs_actual = ""
                                criterio_actual = ""
                        except:
                            obs_actual = ""
                            criterio_actual = ""
                    else:
                        obs_actual = ""
                        criterio_actual = ""
                except:
                    obs_actual = ""
                    criterio_actual = ""

                # Si la observación difiere → preguntar al usuario
                if obs_actual != obs_nueva:
                    msg = (f"El ITEM '{item}' ya existe.\n\n"
                        f"- Observación actual: {obs_actual}\n"
                        f"- Nueva observación: {obs_nueva}\n\n"
                        "¿Quieres actualizarla?")
                    if messagebox.askyesno("Actualizar Observación", msg):
                        df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item, "OBSERVACIONES"] = obs_nueva

                # Si el criterio estaba vacío y el nuevo trae algo → actualizar
                if not criterio_actual and criterio_nuevo:
                    df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item, "CRITERIO"] = criterio_nuevo
            else:
                nuevos_items.append({
                    "ITEM": item,
                    "OBSERVACIONES": obs_nueva,
                    "CRITERIO": criterio_nuevo
                })

        # ➕ Agregar nuevos registros sin duplicar
        if nuevos_items:
            df_codigos_cumple = pd.concat([df_codigos_cumple, pd.DataFrame(nuevos_items)], ignore_index=True)

        # 💾 Guardar cambios
        try:
            # Asegurar que ITEM siga siendo numérico antes de guardar
            df_codigos_cumple["ITEM"] = pd.to_numeric(df_codigos_cumple["ITEM"], errors="coerce")

            df_codigos_cumple.to_excel(ARCHIVO_CODIGOS, index=False)
            df_codigos_cumple.to_json(ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)
            messagebox.showinfo("Éxito", f"Se importaron {len(nuevos_items)} ITEMS nuevos y se actualizaron los existentes.")
            cargar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los cambios: {str(e)}")



    # Guardar Excel + JSON
    def guardar_cambios():
        df_codigos_cumple.to_excel(ARCHIVO_CODIGOS, index=False)
        df_codigos_cumple.to_json(ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)

    # Botones
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    tk.Button(frame_botones, text="Editar", command=editar_item,
             bg="#ECD925", fg="#282828", activebackground="#f3e55b",
             activeforeground="#282828").pack(side="left", padx=5)
    tk.Button(frame_botones, text="Eliminar", command=eliminar_item,
             bg="#ECD925", fg="#282828", activebackground="#f3e55b",
             activeforeground="#282828").pack(side="left", padx=5)
    tk.Button(frame_botones, text="➕ Agregar", command=agregar_item,
             bg="#ECD925", fg="#282828", activebackground="#f3e55b",
             activeforeground="#282828").pack(side="left", padx=5)
    tk.Button(frame_botones, text="📤 Subir Excel", command=subir_excel,
             bg="#ECD925", fg="#282828", activebackground="#f3e55b",
             activeforeground="#282828").pack(side="left", padx=5)

    ventana.mainloop()

def actualizar_observacion_interactiva(item):
    global df_codigos_cumple

    ventana = tk.Toplevel()
    ventana.title(f"Actualizar ITEM {item}")
    ventana.geometry("500x350")
    ventana.grab_set()
    ventana.configure(bg="#FFFFFF")

    try:
        item_num = int(item)
        # Obtener valores actuales
        try:
            mask = df_codigos_cumple["ITEM"] == item_num
            item_data = df_codigos_cumple[mask]
            if len(item_data) > 0:
                try:
                    # Usar método más directo - verificar si es DataFrame
                    if hasattr(item_data, 'iloc'):
                        item_data = item_data.iloc[0]
                    else:
                        raise IndexError("Item not found")
                except:
                    raise IndexError("Item not found")
            else:
                raise IndexError("Item not found")
        except:
            raise IndexError("Item not found")
        obs_actual = item_data["OBSERVACIONES"]
        criterio_actual = item_data.get("CRITERIO", "")
    except ValueError:
        messagebox.showerror("Error", "El ITEM debe ser un número válido")
        ventana.destroy()
        return
    except IndexError:
        messagebox.showerror("Error", f"No se encontró el ITEM {item}")
        ventana.destroy()
        return
        
        # Crear campos de entrada
        tk.Label(ventana, text="ITEM:", bg="#FFFFFF", fg="#282828").pack(pady=5)
        tk.Label(ventana, text=str(item_num), bg="#FFFFFF", fg="#282828", font=("Arial", 10, "bold")).pack()

        tk.Label(ventana, text="Observación:", bg="#FFFFFF", fg="#282828").pack(pady=5)
        entry_obs = tk.Entry(ventana, width=50, bg="#FFFFFF", fg="#282828")
        entry_obs.insert(0, obs_actual)
        entry_obs.pack(pady=5)

        tk.Label(ventana, text="Criterio:", bg="#FFFFFF", fg="#282828").pack(pady=5)
        entry_criterio = tk.Entry(ventana, width=50, bg="#FFFFFF", fg="#282828")
        entry_criterio.insert(0, criterio_actual)
        entry_criterio.pack(pady=5)

        def guardar_cambios():
            nueva_obs = entry_obs.get()
            nuevo_criterio = entry_criterio.get()
            
            if not nueva_obs.strip():
                messagebox.showwarning("Advertencia", "La observación no puede estar vacía")
                return
                
            # Actualizar DataFrame
            df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item_num, "OBSERVACIONES"] = nueva_obs
            df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item_num, "CRITERIO"] = nuevo_criterio
            
            # Guardar cambios en archivos
            df_codigos_cumple.to_excel(ARCHIVO_CODIGOS, index=False)
            df_codigos_cumple.to_json(ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)
            
            messagebox.showinfo("Éxito", "Cambios guardados correctamente")
            ventana.destroy()

        tk.Button(ventana, text="Guardar Cambios", command=guardar_cambios,
                 bg="#ECD925", fg="#282828", activebackground="#f3e55b",
                 activeforeground="#282828").pack(pady=20)

        def guardar_cambios():
            nueva_obs = entry_obs.get()
            nuevo_criterio = entry_criterio.get()
            
            # Actualizar DataFrame
            df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item_num, "OBSERVACIONES"] = nueva_obs
            df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item_num, "CRITERIO"] = nuevo_criterio
            
            # Guardar cambios en archivos
            df_codigos_cumple.to_excel(ARCHIVO_CODIGOS, index=False)
            df_codigos_cumple.to_json(ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)
            
            messagebox.showinfo("Éxito", "Cambios guardados correctamente")
            ventana.destroy()

    obs_actual = ""
    if "OBSERVACIONES" in df_codigos_cumple.columns:
        try:
            mask = df_codigos_cumple["ITEM"] == item_num
            fila = df_codigos_cumple[mask]
            if len(fila) > 0:
                try:
                    # Usar método más directo - verificar si es DataFrame
                    if hasattr(fila, 'iloc') and len(fila) > 0:
                        obs_actual = str(fila.iloc[0]["OBSERVACIONES"])
                    else:
                        obs_actual = ""
                except:
                    obs_actual = ""
            else:
                obs_actual = ""
        except:
            obs_actual = ""

    tk.Label(ventana, text=f"ITEM: {item_num}", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
    tk.Label(ventana, text="Observación actual:").pack()
    entrada = tk.Entry(ventana, width=50)
    entrada.insert(0, obs_actual)
    entrada.pack(pady=10)

    def guardar():
        nueva_obs = entrada.get()
        df_codigos_cumple.loc[df_codigos_cumple["ITEM"] == item_num, "OBSERVACIONES"] = nueva_obs
        df_codigos_cumple.to_excel(ARCHIVO_CODIGOS, index=False)
        df_codigos_cumple.to_json(ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar, bg="#ECD925").pack(pady=10)

    ventana.wait_window()

# FUNCION PARA ACTUALIZAR CODIGOS
def actualizar_codigos(frame_principal):
    try:
        # Seleccionar archivo nuevo
        nuevo_file = filedialog.askopenfilename(
            title="Selecciona el archivo con nuevos códigos",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if not nuevo_file:
            return

        # Si ya existe el concentrado, lo cargamos, si no creamos uno vacío
        if os.path.exists(ARCHIVO_CODIGOS):
            df_base = pd.read_excel(ARCHIVO_CODIGOS)
        else:
            df_base = pd.DataFrame({"ITEM": [], "OBSERVACIONES": [], "CRITERIO": []})

        df_nuevo = pd.read_excel(nuevo_file)

        # Validar columnas obligatorias
        if "ITEM" not in df_nuevo.columns:
            messagebox.showerror("Error", "El archivo nuevo no contiene la columna 'ITEM'")
            return

        # Asegurar que tenga las 3 columnas
        for col in ["OBSERVACIONES", "CRITERIO"]:
            if col not in df_nuevo.columns:
                df_nuevo[col] = ""

        # Eliminar duplicados por ITEM
        df_nuevo = df_nuevo.drop_duplicates(subset=["ITEM"])

        items_existentes = set(df_base["ITEM"].astype(str))
        nuevos_items = []

        # Barra de progreso
        barra = BarraProgreso(frame_principal, "Actualizando items...")

        for idx, row in df_nuevo.iterrows():
            item = str(row["ITEM"])
            obs_nueva = str(row.get("OBSERVACIONES", ""))
            criterio_nuevo = str(row.get("CRITERIO", ""))

            if item in items_existentes:
                fila_base = df_base[df_base["ITEM"].astype(str) == item].iloc[0]
                obs_actual = str(fila_base.get("OBSERVACIONES", ""))

                # Si la observación cambió → preguntar al usuario
                if obs_actual != obs_nueva:
                    # Preguntar al usuario qué hacer
                    msg = (f"El ITEM '{item}' ya existe.\n\n"
                          f"- Observación actual: {obs_actual}\n"
                          f"- Nueva observación: {obs_nueva}\n\n"
                          "¿Quieres actualizarla?")
                    if messagebox.askyesno("Actualizar Observación", msg):
                        df_base.loc[df_base["ITEM"].astype(str) == item, "OBSERVACIONES"] = obs_nueva
            else:
                nuevos_items.append({
                    "ITEM": item,
                    "OBSERVACIONES": obs_nueva,
                    "CRITERIO": criterio_nuevo
                })

            try:
                barra.actualizar(100)  # Simplificar para evitar errores de tipo
            except:
                pass

        # Agregar nuevos registros
        if nuevos_items:
            df_base = pd.concat([df_base, pd.DataFrame(nuevos_items)], ignore_index=True)

        # Guardar concentrado actualizado
        df_base.to_excel(ARCHIVO_CODIGOS, index=False)
        barra.finalizar()

        messagebox.showinfo(
            "Actualizar ITEMS",
            f"[OK] Se actualizaron OBSERVACIONES y se agregaron {len(nuevos_items)} ITEMS nuevos.\nTotal ahora: {len(df_base)}"
        )

    except Exception as e:
        barra.finalizar()
        messagebox.showerror("Error", f"Ocurrió un problema al actualizar:\n{e}")

# FUNCION PARA GENERAR EL TIPO DE REPORTE
def procesar_reporte(reporte_path):
    global frame

    # 👈 NUEVO: REGISTRAR ARCHIVO PROCESADO
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

# CATALOGO DE DECATHLON
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

# FUNCION PARA EXPORTAR EL CATALOGO DE DECATHLON
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





#VENTANA DEL DASHBOARD MEJORADO
def mostrar_estadisticas():
    """Muestra un dashboard mejorado con estadísticas avanzadas de la aplicación"""
    try:
        # Crear ventana del dashboard (más grande para acomodar botones)
        ventana = tk.Toplevel()
        ventana.title("Dashboard de Estadísticas")
        ventana.geometry("1000x600")  # Aumentado para acomodar botones
        ventana.configure(bg="#FFFFFF")
        ventana.grab_set()
        
        # Configurar el estilo de la ventana
        style = ttk.Style()
        style.theme_use('clam')
        
        # Título principal más compacto
        header_frame = tk.Frame(ventana, bg="#ecd925", height=50)  # Reducido de 80
        header_frame.pack(fill="x", pady=(0, 10))  # Reducido de 20
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="DASHBOARD DE ESTADÍSTICAS", 
                font=("INTER", 14, "bold"), bg="#ecd925", fg="#282828").pack(expand=True)  # Reducido de 18
        
        # Frame principal más compacto
        frame_main = tk.Frame(ventana, bg="#FFFFFF")
        frame_main.pack(pady=10, padx=20, fill="both", expand=True)  # Reducido de 20,40
        
        # Frame superior para métricas principales (más compacto)
        frame_metrics = tk.Frame(frame_main, bg="#FFFFFF")
        frame_metrics.pack(fill="x", pady=(0, 10))  # Reducido de 20
        
        # Frame inferior con dos columnas
        frame_content = tk.Frame(frame_main, bg="#FFFFFF")
        frame_content.pack(fill="both", expand=True)
        
        # Frame izquierdo para estadísticas detalladas
        frame_stats = tk.Frame(frame_content, bg="#FFFFFF")
        frame_stats.pack(side="left", fill="both", expand=True, padx=(0, 10))  # Reducido de 20
        
        # Frame derecho para gráficas
        frame_graph = tk.Frame(frame_content, bg="#FFFFFF")
        frame_graph.pack(side="right", fill="both", expand=True)
        
        # Función mejorada para obtener estadísticas avanzadas
        def obtener_stats_avanzadas():
            stats = {}
            
            # Estadísticas de códigos con análisis detallado
            try:
                if os.path.exists(ARCHIVO_CODIGOS):
                    df_codigos = pd.read_excel(ARCHIVO_CODIGOS)
                    stats['total_codigos'] = len(df_codigos)
                    
                    # Análisis de cumplimiento
                    if 'OBSERVACIONES' in df_codigos.columns:
                        cumple_count = df_codigos['OBSERVACIONES'].str.contains('CUMPLE', case=False, na=False).sum()
                        no_cumple_count = df_codigos['OBSERVACIONES'].str.contains('NO CUMPLE', case=False, na=False).sum()
                        stats['codigos_cumple'] = cumple_count
                        stats['codigos_no_cumple'] = no_cumple_count
                        stats['porcentaje_cumple'] = (cumple_count / len(df_codigos) * 100) if len(df_codigos) > 0 else 0
                    else:
                        stats['codigos_cumple'] = 0
                        stats['codigos_no_cumple'] = 0
                        stats['porcentaje_cumple'] = 0
                    
                    # Códigos activos
                    if 'ESTADO' in df_codigos.columns:
                        stats['codigos_activos'] = len(df_codigos[df_codigos['ESTADO'] == 'ACTIVO'])
                    else:
                        stats['codigos_activos'] = len(df_codigos)
                else:
                    stats.update({
                        'total_codigos': 0, 'codigos_activos': 0, 'codigos_cumple': 0,
                        'codigos_no_cumple': 0, 'porcentaje_cumple': 0
                    })
            except Exception as e:
                print(f"Error leyendo códigos: {e}")

                stats.update({
                    'total_codigos': 0, 'codigos_activos': 0, 'codigos_cumple': 0,
                    'codigos_no_cumple': 0, 'porcentaje_cumple': 0
                })
            
            # Estadísticas del catálogo con análisis de tipos
            try:
                if os.path.exists(BASE_GENERAL):
                    df_catalogo = pd.read_excel(BASE_GENERAL)
                    stats['total_items'] = len(df_catalogo)
                    stats['catalogo_size'] = f"{os.path.getsize(BASE_GENERAL) / 1024 / 1024:.2f} MB"
                    
                    # Análisis de tipos de proceso si existe la columna
                    if 'CODIGO FORMATO' in df_catalogo.columns:
                        tipos_proceso = df_catalogo['CODIGO FORMATO'].value_counts()
                        stats['tipos_proceso'] = tipos_proceso.to_dict()
                    else:
                        stats['tipos_proceso'] = {}
                else:
                    stats.update({'total_items': 0, 'catalogo_size': '0 MB', 'tipos_proceso': {}})
            except Exception as e:
                print(f"Error leyendo catálogo: {e}")
                stats.update({'total_items': 0, 'catalogo_size': '0 MB', 'tipos_proceso': {}})

                stats['total_codigos'] = 0


            
            # Estadísticas del historial con análisis temporal
            try:
                if os.path.exists(HISTORIAL):
                    df_hist = pd.read_excel(HISTORIAL)
                    stats['total_procesos'] = len(df_hist)
                    stats['historial_size'] = f"{os.path.getsize(HISTORIAL) / 1024 / 1024:.2f} MB"
                    
                    # Análisis temporal
                    if 'FECHA_PROCESO' in df_hist.columns:
                        df_hist['FECHA_PROCESO'] = pd.to_datetime(df_hist['FECHA_PROCESO'], errors='coerce')
                        ultima_fecha = df_hist['FECHA_PROCESO'].max()
                        primera_fecha = df_hist['FECHA_PROCESO'].min()
                        # Simplificar verificaciones de fechas
                        stats['ultimo_proceso'] = ultima_fecha.strftime('%d/%m/%Y %H:%M') if ultima_fecha is not None and str(ultima_fecha).strip() != '' and str(ultima_fecha).lower() != 'nat' else 'N/A'
                        stats['primer_proceso'] = primera_fecha.strftime('%d/%m/%Y') if primera_fecha is not None and str(primera_fecha).strip() != '' and str(primera_fecha).lower() != 'nat' else 'N/A'
                        
                        # Procesos por mes (últimos 6 meses)
                        df_hist['MES'] = df_hist['FECHA_PROCESO'].dt.to_period('M')
                        procesos_por_mes = df_hist['MES'].value_counts().sort_index().tail(6)
                        stats['procesos_por_mes'] = {str(k): v for k, v in procesos_por_mes.items()}
                    else:
                        stats.update({
                            'ultimo_proceso': 'N/A', 'primer_proceso': 'N/A', 'procesos_por_mes': {}
                        })
                else:
                    stats.update({
                        'total_procesos': 0, 'historial_size': '0 MB', 'ultimo_proceso': 'N/A',
                        'primer_proceso': 'N/A', 'procesos_por_mes': {}
                    })
            except Exception as e:
                print(f"Error leyendo historial: {e}")
                stats.update({
                    'total_procesos': 0, 'historial_size': '0 MB', 'ultimo_proceso': 'N/A',
                    'primer_proceso': 'N/A', 'procesos_por_mes': {}
                })
            
            return stats
        
        # Obtener estadísticas avanzadas
        stats = obtener_stats_avanzadas()
        
        # Crear tarjetas de métricas principales (más compactas)
        def crear_tarjeta_metrica(parent, titulo, valor, color="#ecd925", icono="[INFO]"):
            tarjeta = tk.Frame(parent, bg=color, relief="raised", bd=1)
            tarjeta.pack(side="left", fill="both", expand=True, padx=3, pady=3)  # Reducido de 5
            
            # Icono y título más compactos
            tk.Label(tarjeta, text=icono, font=("INTER", 12), bg=color, fg="#282828").pack(pady=(5, 2))  # Reducido de 16, 10,5
            tk.Label(tarjeta, text=titulo, font=("INTER", 8, "bold"), bg=color, fg="#282828").pack()  # Reducido de 10
            
            # Valor principal más compacto
            tk.Label(tarjeta, text=str(valor), font=("INTER", 14, "bold"), bg=color, fg="#282828").pack(pady=(2, 5))  # Reducido de 20, 5,10
            
            return tarjeta
        
        # Variables para las gráficas
        notebook = None
        
        # Crear widgets de estadísticas detalladas
        row = 0
        
        # Sección: CÓDIGOS DE CUMPLIMIENTO (más compacta)
        tk.Label(frame_stats, text="🔑 CÓDIGOS DE CUMPLIMIENTO", 
                font=("INTER", 10, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", pady=(10,5))  # Reducido de 12, 20,10
        row += 1

        tk.Label(frame_stats, text="Total códigos:", font=("INTER", 9), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(15,5))  # Reducido de 10, 20,10
        tk.Label(frame_stats, text=str(stats['total_codigos']), font=("INTER", 9, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=1, sticky="w")
        row += 1
        

        tk.Label(frame_stats, text="Cumplen:", font=("INTER", 9), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(15,5))
        tk.Label(frame_stats, text=f"{stats['codigos_cumple']} ({stats['porcentaje_cumple']:.1f}%)", 
                font=("INTER", 9, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=1, sticky="w")  # Cambiado a color original
        row += 1
        
        tk.Label(frame_stats, text="No cumplen:", font=("INTER", 9), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(15,5))
        tk.Label(frame_stats, text=str(stats['codigos_no_cumple']), 
                font=("INTER", 9, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=1, sticky="w")  # Cambiado a color original
        row += 1
        
        # ESTADISTICAS DE ARCHIVOS PROCESADOS (más compacta)

        # ESTADISTICAS DE ARCHIVOS PROCESADOS

        tk.Label(frame_stats, text="📁 ARCHIVOS PROCESADOS", 
                font=("INTER", 10, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", pady=(10,5))  # Reducido de 12, 20,10
        row += 1
        
        # Obtener estadísticas de archivos
        stats_archivos = obtener_estadisticas_archivos()
        
        tk.Label(frame_stats, text="Total archivos:", font=("INTER", 9), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(15,5))  # Reducido de 10, 20,10
        tk.Label(frame_stats, text=str(stats_archivos['total_archivos']), font=("INTER", 9, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=1, sticky="w")
        row += 1

        tk.Label(frame_stats, text="Último archivo:", font=("INTER", 9), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(15,5))
        tk.Label(frame_stats, text=str(stats_archivos['ultimo_proceso']), font=("INTER", 9, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=1, sticky="w")
        row += 1
        
        # Información temporal del historial (más compacta)
        if stats.get('primer_proceso', 'N/A') != 'N/A':
            tk.Label(frame_stats, text="Primer proceso:", font=("INTER", 9), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(15,5))
            tk.Label(frame_stats, text=str(stats['primer_proceso']), font=("INTER", 9, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=1, sticky="w")
        row += 1
        
        # Lista de archivos recientes (más compacta)
        if stats_archivos['archivos_recientes']:
            tk.Label(frame_stats, text="Archivos recientes:", font=("INTER", 9), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", padx=(15,5), pady=(5,2))  # Reducido
            row += 1
            
            # Frame para la lista de archivos
            frame_archivos = tk.Frame(frame_stats, bg="#FFFFFF")
            frame_archivos.grid(row=row, column=0, columnspan=2, sticky="ew", padx=(15,0))
            
            for i, archivo in enumerate(stats_archivos['archivos_recientes'][-2:]):  # Solo los últimos 2 para ahorrar espacio
                nombre_corto = archivo['nombre'][:25] + "..." if len(archivo['nombre']) > 25 else archivo['nombre']  # Reducido de 30
                fecha_corta = archivo['fecha_proceso'].split(' ')[0]  # Solo la fecha
                
                tk.Label(frame_archivos, text=f"• {nombre_corto}", font=("INTER", 7), 
                        bg="#FFFFFF", fg="#282828").grid(row=i, column=0, sticky="w")  # Reducido de 8
                tk.Label(frame_archivos, text=fecha_corta, font=("INTER", 7), 
                        bg="#FFFFFF", fg="#282828").grid(row=i, column=1, sticky="w", padx=(5,0))  # Reducido de 8, 10
                row += 1

        
        # GRÁFICAS AVANZADAS CON MATPLOTLIB (más compactas)
        tk.Label(frame_graph, text="VISUALIZACIONES", 
                font=("INTER", 10, "bold"), bg="#FFFFFF", fg="#282828").pack(pady=(0,5))  # Reducido de 12, 10

        # Frame para las gráficas
        frame_graficas = tk.Frame(frame_graph, bg="#FFFFFF")
        frame_graficas.pack(fill="both", expand=True)
        
        # Notebook para pestañas de gráficas (más compacto)
        notebook = ttk.Notebook(frame_graficas)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)  # Reducido de 10
        
        
        # Pestaña 2: Códigos Cumple general
        frame_codigos_cumple = tk.Frame(notebook, bg="#FFFFFF")
        notebook.add(frame_codigos_cumple, text="Códigos Cumple")


        # GRÁFICA DE BARRAS MEJORADA
        tk.Label(frame_graph, text="VISUALIZACIÓN", 
                font=("INTER", 12, "bold"), bg="#FFFFFF", fg="#ffffff").pack(pady=(0,20))

        canvas_width = 500
        canvas_height = 220
        canvas = tk.Canvas(frame_graph, width=canvas_width, height=canvas_height, bg="#FFFFFF", highlightthickness=0)
        canvas.pack()

        def dibujar_grafica():
            canvas.delete("all")
            
            # --- Leer codigos_cumple.json para calcular los códigos que cumplen ---
            try:
                with open("resources/codigos_cumple.json", "r", encoding="utf-8") as f:
                    codigos_data = json.load(f)

                # Total de códigos que cumplen según OBSERVACION
                total_cumple = sum(
                    1 for d in codigos_data
                    if isinstance(d, dict) and "OBSERVACION" in d and "CUMPLE" in str(d["OBSERVACION"]).upper()
                )
                # Códigos que no cumplen
                total_no_cumple = stats['total_codigos'] - total_cumple
                if total_no_cumple < 0:
                    total_no_cumple = 0
            except Exception as e:
                print(f"Error leyendo codigos_cumple.json: {e}")
                total_cumple = 0
                total_no_cumple = 0

            # --- Datos de la gráfica: 4 columnas ---
            datos = [
                ("Total Códigos", stats['total_codigos']),
                ("Códigos Ingresados", stats['total_procesos']),
                ("Códigos cumplen", total_cumple),
                ("Códigos no cumplen", total_no_cumple),
            ]

            margen = 40
            ancho_barra = 60
            espacio = 40
            altura_max = 150
            
            max_valor = max([d[1] for d in datos if isinstance(d[1], (int, float))], default=1)
            if max_valor == 0:
                max_valor = 1

            # Dibujar ejes con ticks
            canvas.create_line(margen, altura_max + margen, canvas_width - margen, altura_max + margen, fill="#282828", width=2)
            canvas.create_line(margen, margen, margen, altura_max + margen, fill="#282828", width=2)
            for i in range(0, max_valor + 1, max(1, max_valor // 5)):
                y_tick = altura_max + margen - (i / max_valor) * altura_max
                canvas.create_line(margen-5, y_tick, margen, y_tick, fill="#282828", width=1)
                canvas.create_text(margen-10, y_tick, text=str(i), font=("Segoe UI", 8), fill="#282828", anchor="e")
            
            # Dibujar barras
            x_inicio = margen + espacio
            for i, (nombre, valor) in enumerate(datos):
                altura_barra = (valor / max_valor) * altura_max if valor > 0 else 0
                x1 = x_inicio + i * (ancho_barra + espacio)
                y1 = altura_max + margen - altura_barra
                x2 = x1 + ancho_barra
                y2 = altura_max + margen

                # Barra
                canvas.create_rectangle(x1, y1, x2, y2, fill="#ECD925", outline="#282828", width=1.5)
                
                # Valor sobre la barra
                canvas.create_text((x1 + x2)/2, y1 - 10, text=str(valor), font=("INTER", 9, "bold"), fill="#282828")
                
                # Nombre debajo
                canvas.create_text((x1 + x2)/2, altura_max + margen + 20, text=nombre, font=("INTER", 9), fill="#282828")


        def crear_grafica_codigos_cumple():
            """Crear gráfica general de códigos cumple sin división por normas"""
            try:
                # Crear gráfica de códigos cumple general
                fig, ax = plt.subplots(figsize=(6, 3))
                fig.patch.set_facecolor('#FFFFFF')
                
                # Datos de códigos cumple
                categorias = ['Total Códigos', 'Códigos Cumple', 'Códigos No Cumple']
                valores = [stats['total_codigos'], stats['codigos_cumple'], stats['codigos_no_cumple']]
                colores = ['#ecd925', '#4CAF50', '#F44336']
                
                # Crear gráfica de barras
                bars = ax.bar(categorias, valores, color=colores, alpha=0.8)
                ax.set_title('Resumen General de Códigos Cumple', fontsize=10, fontweight='bold', color='#282828')
                ax.set_ylabel('Cantidad', color='#282828', fontsize=9)
                
                # Agregar valores en las barras
                for bar, valor in zip(bars, valores):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{valor}', ha='center', va='bottom', fontweight='bold', fontsize=8)
                
                # Rotar etiquetas del eje X si es necesario
                plt.xticks(rotation=45, fontsize=8)
                plt.tight_layout()
                
                # Convertir a imagen para tkinter
                canvas_codigos = tk.Canvas(frame_codigos_cumple, bg="#FFFFFF", highlightthickness=0)
                canvas_codigos.pack(fill="both", expand=True, padx=5, pady=5)
                
                # Guardar figura en buffer
                buf = BytesIO()
                plt.savefig(buf, format='PNG', dpi=80, bbox_inches='tight', facecolor='#FFFFFF')
                buf.seek(0)
                plt.close()
                
                # Mostrar en canvas
                img = Image.open(buf)
                img_tk = ImageTk.PhotoImage(img)
                canvas_codigos.create_image(0, 0, anchor="nw", image=img_tk)
                # Mantener referencia a la imagen para evitar garbage collection
                setattr(canvas_codigos, '_image_ref', img_tk)
                    
            except Exception as e:
                print(f"Error creando gráfica de códigos cumple: {e}")
                tk.Label(frame_codigos_cumple, text="Error al cargar gráfica de códigos cumple", 
                        bg="#FFFFFF", fg="#282828").pack(expand=True)


        # Botones DIRECTAMENTE en la ventana (SIN FRAMES)
        # Crear botones directamente en la ventana principal
        
        # Botón para limpiar historial de archivos
        def limpiar_historial_archivos():
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar el historial de archivos procesados?\nEsta acción no se puede deshacer."):
                try:
                    if os.path.exists(ARCHIVOS_PROCESADOS_FILE):
                        os.remove(ARCHIVOS_PROCESADOS_FILE)
                        messagebox.showinfo("Éxito", "Historial de archivos limpiado correctamente.")
                        # Actualizar dashboard
                        ventana.destroy()
                        mostrar_estadisticas()  # Reabrir dashboard
                    else:
                        messagebox.showinfo("Info", "No hay historial de archivos para limpiar.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo limpiar el historial:\n{e}")
        
        btn_limpiar = tk.Button(ventana, text="LIMPIAR", 
                               command=limpiar_historial_archivos,
                               font=("Arial", 10, "bold"), bg="#ecd925", fg="#282828", 
                               relief="raised", padx=15, pady=8, bd=2)
        btn_limpiar.place(x=50, y=600, width=120, height=40)
        

        def exportar_pdf_simple():
            """Genera un PDF simple con estadísticas"""
            try:
                ruta = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("Archivos PDF", "*.pdf")],
                    title="Guardar Reporte de Estadísticas"
                )
                if not ruta:
                    return

                # Crear PDF simple
                c = pdf_canvas.Canvas(ruta, pagesize=letter)
                ancho, alto = letter

                # Encabezado
                c.setFillColor("#ecd925")
                c.rect(0, alto - 80, ancho, 80, fill=1, stroke=0)

                c.setFillColor("#282828")
                c.setFont("Helvetica-Bold", 20)
                c.drawString(50, alto - 50, "REPORTE DE ESTADÍSTICAS")

                c.setFont("Helvetica", 10)
                c.drawString(50, alto - 70, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

                y = alto - 120

                # Estadísticas principales
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, "ESTADÍSTICAS PRINCIPALES")
                y -= 30

                c.setFont("Helvetica", 12)
                c.drawString(70, y, f"• Total de códigos: {stats['total_codigos']}")
                y -= 20
                c.drawString(70, y, f"• Códigos que cumplen: {stats['codigos_cumple']} ({stats['porcentaje_cumple']:.1f}%)")
                y -= 20
                c.drawString(70, y, f"• Códigos que no cumplen: {stats['codigos_no_cumple']}")
                y -= 20
                c.drawString(70, y, f"• Total de procesos: {stats['total_procesos']}")
                y -= 20
                c.drawString(70, y, f"• Items en catálogo: {stats['total_items']}")
                y -= 30

                # Archivos procesados
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y, "ARCHIVOS PROCESADOS")
                y -= 30

                c.setFont("Helvetica", 12)
                c.drawString(70, y, f"• Total de archivos: {stats_archivos['total_archivos']}")
                y -= 20
                c.drawString(70, y, f"• Último archivo: {stats_archivos['ultimo_proceso']}")
                y -= 30


                # Pie de página

                if stats_archivos['archivos_recientes']:
                    c.drawString(70, y, "Archivos recientes:")
                    y -= 15
                    for archivo in stats_archivos['archivos_recientes'][-3:]:
                        c.drawString(90, y, f"• {archivo['nombre']} ({archivo['fecha_proceso']})")
                        y -= 15
                    y -= 10

                # --- Preparar datos para la gráfica desde JSON ---
                with open("resources/codigos_cumple.json", "r", encoding="utf-8") as f:
                    codigos_data = json.load(f)

                # Contar los códigos que cumplen
                total_cumple = sum(1 for d in codigos_data if d.get("OBSERVACION", "").lower() == "cumple")
                total_items = stats.get('total_codigos', 0)

                nombres = ["Total de códigos", "Códigos que cumplen"]
                valores = [total_items, total_cumple]

                # --- Gráfica ---
                ancho_figura = 6
                plt.figure(figsize=(ancho_figura, 4))
                bars = plt.bar(nombres, valores, color="#ecd925")

                for bar in bars:
                    plt.text(bar.get_x() + bar.get_width()/2,
                            bar.get_height(),
                            str(bar.get_height()),
                            ha="center", va="bottom", fontsize=10, color="#282828")

                plt.title("Visualización de Estadísticas", color="#282828")
                plt.ylabel("Cantidad", color="#282828")
                plt.xticks(color="#282828")
                plt.yticks(color="#282828")
                plt.tight_layout()

                buf = BytesIO()
                plt.savefig(buf, format="PNG")
                plt.close()
                buf.seek(0)

                imagen_grafica = ImageReader(buf)
                c.drawImage(imagen_grafica, 100, y - 300, width=400, height=250)

                # --- Pie de página ---

                c.setFillColor("#282828")
                c.rect(0, 0, ancho, 30, fill=1, stroke=0)
                c.setFillColor("#FFFFFF")
                c.setFont("Helvetica", 8)
                c.drawString(50, 10, "Generado por Sistema de Procesos")

                # Guardar PDF
                c.save()
                messagebox.showinfo("Éxito", f"PDF generado correctamente en:\n{ruta}")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")
                print(f"Error detallado: {e}")

        # --- Botones mejorados del dashboard ---
        btn_pdf = tk.Button(ventana, text="📄 PDF", 
                            command=exportar_pdf_simple,
                            font=("Arial", 10, "bold"), bg="#ecd925", fg="#282828", 
                            relief="raised", padx=15, pady=8, bd=2)
        btn_pdf.place(x=190, y=600, width=120, height=40)
        
        # Botón para exportar datos a Excel
        def exportar_excel_estadisticas():
            """Exporta las estadísticas a un archivo Excel"""
            try:
                ruta = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Archivos Excel", "*.xlsx")],
                    title="Guardar Estadísticas en Excel"
                )
                if not ruta:
                    return
                
                # Crear DataFrame con estadísticas
                df_stats = pd.DataFrame({
                    "Métrica": ["Total Códigos", "Códigos que Cumplen", "Códigos que No Cumplen", 
                               "Porcentaje de Cumplimiento", "Total Procesos", "Total Items Catálogo",
                               "Tamaño Catálogo", "Tamaño Historial", "Último Proceso", "Primer Proceso"],
                    "Valor": [stats['total_codigos'], stats['codigos_cumple'], stats['codigos_no_cumple'],
                             f"{stats['porcentaje_cumple']:.1f}%", stats['total_procesos'], stats['total_items'],
                             stats['catalogo_size'], stats['historial_size'], stats['ultimo_proceso'], 
                             stats.get('primer_proceso', 'N/A')]
                })
                
                # Crear archivo Excel con múltiples hojas
                with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
                    df_stats.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    # Hoja de archivos procesados
                    if stats_archivos['archivos_recientes']:
                        df_archivos = pd.DataFrame(stats_archivos['archivos_recientes'])
                        df_archivos.to_excel(writer, sheet_name='Archivos Procesados', index=False)
                    
                    # Hoja de procesos por mes
                    if stats.get('procesos_por_mes'):
                        df_meses = pd.DataFrame({
                            'Mes': list(stats['procesos_por_mes'].keys()),
                            'Cantidad': list(stats['procesos_por_mes'].values())
                        })
                        df_meses.to_excel(writer, sheet_name='Procesos por Mes', index=False)
                
                messagebox.showinfo("Éxito", f"Estadísticas exportadas a Excel:\n{ruta}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar a Excel:\n{e}")
        
        btn_excel = tk.Button(ventana, text="EXCEL", 
                             command=exportar_excel_estadisticas,
                             font=("Arial", 10, "bold"), bg="#ecd925", fg="#282828",
                             relief="raised", padx=15, pady=8, bd=2)
        btn_excel.place(x=330, y=600, width=120, height=40)

        # Botón de actualizar estadísticas
        def actualizar_estadisticas():
            """Actualiza las estadísticas y regenera las gráficas"""
            try:
                # Cerrar la ventana actual y abrir una nueva
                ventana.destroy()
                mostrar_estadisticas()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar estadísticas:\n{e}")

        btn_actualizar = tk.Button(ventana, text="🔄 ACTUALIZAR", 
                                 command=actualizar_estadisticas,
                                 font=("Arial", 10, "bold"), bg="#ecd925", fg="#282828",
                                 relief="raised", padx=15, pady=8, bd=2)
        btn_actualizar.place(x=470, y=600, width=120, height=40)

        # Botón de cerrar
        btn_cerrar = tk.Button(ventana, text="CERRAR", 
                             command=ventana.destroy,
                             font=("Arial", 10, "bold"), bg="#282828", fg="#FFFFFF", 
                             relief="raised", padx=15, pady=8, bd=2)
        btn_cerrar.place(x=610, y=600, width=120, height=40)

        # Crear las gráficas DESPUÉS de los botones
        crear_grafica_codigos_cumple()



    except Exception as e:
        messagebox.showerror("Error", f"Error al mostrar estadísticas:\n{e}")
        print(f"Error en dashboard: {e}")













# FUNCION PARA LA BARRA DE PROGRESO
class   BarraProgreso:
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
        
# Verificar rutas al inicio
def verificar_rutas():
    """Verifica si todas las rutas necesarias están configuradas"""
    config = cargar_configuracion()
    if not config or not all(config.get("rutas", {}).values()):
        if messagebox.askyesno("Configuración", 
                             "No se han configurado todas las rutas necesarias. ¿Desea configurarlas ahora?"):
            return configurar_rutas()
    return config.get("rutas", {}) if config else {}

# VENTANA PRINCIPAL
root = tk.Tk()
root.title("GENERADOR DE TIPO DE PROCESO")
root.geometry("1100x570")
root.configure(bg="#FFFFFF")

# Verificar rutas al iniciar la aplicación
RUTAS = verificar_rutas()

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
            logo_img_raw = Image.open(logo_path).resize((150, 90), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(logo_img_raw)
            logo_label = tk.Label(frame_left, image=logo_img, bg="#FFFFFF")
            # Mantener referencia a la imagen para evitar garbage collection
            setattr(logo_label, '_image_ref', logo_img)
            logo_label.pack(pady=(20, 20))
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    # --- Barra de progreso TIPO DE PROCESO (abajo a la izquierda) ---
    progress_var_tipo = tk.DoubleVar()
    progress_bar_tipo = ttk.Progressbar(frame_left, variable=progress_var_tipo, maximum=100, length=250)
    progress_label_tipo = tk.Label(frame_left, text="", bg="#FFFFFF", fg="#282828", font=("INTER", 10, "bold"))
    percent_label_tipo = tk.Label(frame_left, text="", bg="#FFFFFF", fg="#282828", font=("INTER", 10, "bold"))

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
    # --- FRAME DE BOTONES CENTRADOS ---
    # --- Encabezado en dos niveles ---
    header_frame = tk.Frame(frame_left, bg="#FFFFFF")
    header_frame.pack(pady=(10,10), fill="x")

    # Línea superior amarilla (decorativa)
    linea = tk.Frame(header_frame, bg="#ecd925", height=5)
    linea.pack(fill="x", pady=(0,10))

    # Título principal
    label_titulo = tk.Label(
        header_frame, 
        text="INSPECCIÓN DE CUMPLIMIENTO\nNORMATIVO AL ARRIBO",
        font=("INTER", 30, "bold"), 
        fg="#282828", 
        bg="#FFFFFF", 
        justify="center"
    )
    label_titulo.pack(pady=(0,10))

    # Subtítulo
    label_sub = tk.Label(
        header_frame, 
        text="Sube el reporte de mercancía para generar el TIPO DE PROCESO",
        font=("INTER", 12, "bold"), 
        fg="#4d4d4d", 
        bg="#FFFFFF",
        justify="center"
    )
    label_sub.pack()

    # --- Botones debajo del título ---
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        'TButton', 
        background='#ecd925', 
        foreground='#282828', 
        font=('INTER', 10, 'bold'), 
        borderwidth=0, 
        padding=(2,2)
    )
    style.map(
        'TButton', 
        background=[('active', "#B8AA00")], 
        foreground=[('active', '#282828')]
    )

    # Contenedor de botones debajo del header
    frame_buttons = tk.Frame(frame_left, bg="#FFFFFF")
    frame_buttons.pack(pady=(5,5), fill="x")

    botones = [
        ("CONFIGURAR RUTAS", configurar_rutas),
        ("REPORTE DE MERCANCIA", seleccionar_reporte),
        ("EDITOR DE CÓDIGOS", lambda: abrir_editor_codigos(frame_left)),
        ("DASHBOARD", mostrar_estadisticas),
        ("ACTUALIZAR CATALOGO", lambda: actualizar_catalogo(frame_left)),
        ("EXPORTAR CATALOGO", lambda: exportar_concentrado_catalogo(frame_left)),
    ]
    # Ahora los botones se organizan en 4 columnas
    cols = 4
    for i, (texto, comando) in enumerate(botones):
        btn = ttk.Button(frame_buttons, text=texto, command=comando, style='TButton', width=25)
        btn.grid(row=i // cols, column=i % cols, padx=10, pady=10, ipadx=10, ipady=10, sticky="nsew")
    
    # Configurar las columnas para que se expandan de forma proporcional
    for col in range(cols):
        frame_buttons.grid_columnconfigure(col, weight=1)

    root.mainloop()

