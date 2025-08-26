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

if getattr(sys, 'frozen', False):
    # Cuando está compilado en .exe
    BASE_PATH = sys._MEIPASS
else:
    # Cuando se ejecuta desde Python
    BASE_PATH = os.path.dirname(__file__)

# Configuración de rutas y archivos
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_PATH, "config.json")

# 👈 NUEVO: SISTEMA DE CONTADOR DE ARCHIVOS PROCESADOS
ARCHIVOS_PROCESADOS_FILE = os.path.join(BASE_PATH, "archivos_procesados.json")

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
            
            print(f"✅ Archivo registrado: {nombre_archivo}")
        else:
            print(f"ℹ️ Archivo ya registrado: {nombre_archivo}")
            
    except Exception as e:
        print(f"❌ Error registrando archivo: {e}")

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
        print(f"❌ Error obteniendo estadísticas: {e}")
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
                print(f"✅ Convertido a JSON: {json_path}")
                messagebox.showinfo("Conversión exitosa", f"Archivo convertido a JSON para mejor rendimiento:\n{os.path.basename(json_path)}")
            except Exception as e:
                print(f"❌ Error convirtiendo a JSON: {e}")
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
        df_codigos_cumple = pd.DataFrame(columns=["ITEM", "OBSERVACIONES", "CRITERIO"])
else:
    print(f"Archivo no encontrado: {ARCHIVO_CODIGOS}")
    df_codigos_cumple = pd.DataFrame(columns=["ITEM", "OBSERVACIONES", "CRITERIO"])


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
            df_codigos_cumple = pd.DataFrame(columns=["ITEM", "OBSERVACIONES", "CRITERIO"])
    except Exception as e:
        print(f"Error al cargar los datos: {str(e)}")
        messagebox.showerror("Error", f"Error al cargar los datos: {str(e)}")
        df_codigos_cumple = pd.DataFrame(columns=["ITEM", "OBSERVACIONES", "CRITERIO"])
    
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

        df_codigos_cumple.drop(df_codigos_cumple[df_codigos_cumple["ITEM"] == int(item_id)].index, inplace=True)
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
            if item_val in df_codigos_cumple["ITEM"].values:
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

        # Concatenamos lo nuevo con lo existente
        global df_codigos_cumple
        df_codigos_cumple = pd.concat(
            [df_codigos_cumple, df_subido[columnas_necesarias]],
            ignore_index=True
        )

        # Guardamos directamente en la ubicación del archivo original
        try:
            df_codigos_cumple.to_excel(ARCHIVO_CODIGOS, index=False)
            df_codigos_cumple.to_json(ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)
            messagebox.showinfo("Éxito", "Datos importados y guardados correctamente")
            cargar_tabla()  # Actualizar la tabla con los nuevos datos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los cambios: {str(e)}")


    # Guardar Excel + JSON
    def guardar_cambios():
        df_codigos_cumple.to_excel(ARCHIVO_CODIGOS, index=False)
        df_codigos_cumple.to_json(ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)

    # Botones
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    tk.Button(frame_botones, text="✏️ Editar", command=editar_item,
             bg="#ECD925", fg="#282828", activebackground="#f3e55b",
             activeforeground="#282828").pack(side="left", padx=5)
    tk.Button(frame_botones, text="🗑️ Eliminar", command=eliminar_item,
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
        item_data = df_codigos_cumple[df_codigos_cumple["ITEM"] == item_num].iloc[0]
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
        fila = df_codigos_cumple[df_codigos_cumple["ITEM"] == item_num]
        if not fila.empty:
            obs_actual = str(fila.iloc[0]["OBSERVACIONES"])

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
        command=lambda: exportar_concentrado_codigos(frame),  # Pasamos el frame como argumento
        style='TButton'
    )
    btn_exportar.pack(pady=10, ipadx=10, ipady=5)
    return btn_exportar

# --- Función para generar el tipo de proceso ---
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
            'NOM004TEXX', 'NOM020INS', 'NOM-020-SCFI-1997'
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
            if 'NOM020INS' in tipo or 'NOM-020-SCFI-1997' in norma_val:
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

        messagebox.showinfo("Catálogo actualizado", "El catálogo fue cargado correctamente.")

    except Exception as e:
        if barra:
            barra.finalizar()
        messagebox.showerror("Error", f"No se pudo actualizar el catálogo:\n{e}")

def exportar_concentrado_catalogo(frame_principal):
    try:
        # Detectar ruta base (para .exe y script)
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
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
        messagebox.showinfo("Exportar Catálogo", f"✅ Se exportó correctamente el concentrado a:\n{ruta_guardado}")

    except Exception as e:
        try:
            barra.finalizar()
        except:
            pass
        messagebox.showerror("Error", f"No se pudo exportar el catálogo:\n{e}")

def mostrar_estadisticas():
    """Muestra un dashboard con estadísticas de la aplicación"""
    try:
        # Crear ventana del dashboard
        ventana = tk.Toplevel()
        ventana.title("📊 Dashboard de Estadísticas")
        ventana.geometry("800x600")
        ventana.configure(bg="#FFFFFF")
        ventana.grab_set()
        
        # Título principal
        tk.Label(ventana, text="📊 DASHBOARD DE ESTADÍSTICAS", 
                font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#282828").pack(pady=20)
        
        # Frame principal con dos columnas
        frame_main = tk.Frame(ventana, bg="#FFFFFF")
        frame_main.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Frame izquierdo para estadísticas
        frame_stats = tk.Frame(frame_main, bg="#FFFFFF")
        frame_stats.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Frame derecho para gráfica
        frame_graph = tk.Frame(frame_main, bg="#FFFFFF")
        frame_graph.pack(side="right", fill="both", expand=True)
        
        # Función para obtener estadísticas
        def obtener_stats():
            stats = {}
            
            # Estadísticas de códigos - ARREGLADO
            try:
                if os.path.exists(ARCHIVO_CODIGOS):
                    df_codigos = pd.read_excel(ARCHIVO_CODIGOS)
                    stats['total_codigos'] = len(df_codigos)
                    # Contar códigos activos (si no hay columna ESTADO, todos son activos)
                    if 'ESTADO' in df_codigos.columns:
                        stats['codigos_activos'] = len(df_codigos[df_codigos['ESTADO'] == 'ACTIVO'])
                    else:
                        stats['codigos_activos'] = len(df_codigos)  # Todos activos por defecto
                else:
                    stats['total_codigos'] = 0
                    stats['codigos_activos'] = 0
            except Exception as e:
                print(f"Error leyendo códigos: {e}")
                stats['total_codigos'] = 0
                stats['codigos_activos'] = 0
            
            # Estadísticas del catálogo
            try:
                if os.path.exists(BASE_GENERAL):
                    df_catalogo = pd.read_excel(BASE_GENERAL)
                    stats['total_items'] = len(df_catalogo)
                    stats['catalogo_size'] = f"{os.path.getsize(BASE_GENERAL) / 1024 / 1024:.2f} MB"
                else:
                    stats['total_items'] = 0
                    stats['catalogo_size'] = '0 MB'
            except Exception as e:
                print(f"Error leyendo catálogo: {e}")
                stats['total_items'] = 0
                stats['catalogo_size'] = '0 MB'
            
            # Estadísticas del historial
            try:
                if os.path.exists(HISTORIAL):
                    df_hist = pd.read_excel(HISTORIAL)
                    stats['total_procesos'] = len(df_hist)
                    stats['historial_size'] = f"{os.path.getsize(HISTORIAL) / 1024 / 1024:.2f} MB"
                    
                    # Última fecha de proceso
                    if 'FECHA_PROCESO' in df_hist.columns:
                        df_hist['FECHA_PROCESO'] = pd.to_datetime(df_hist['FECHA_PROCESO'], errors='coerce')
                        ultima_fecha = df_hist['FECHA_PROCESO'].max()
                        stats['ultimo_proceso'] = ultima_fecha.strftime('%d/%m/%Y %H:%M') if pd.notna(ultima_fecha) else 'N/A'
                    else:
                        stats['ultimo_proceso'] = 'N/A'
                else:
                    stats['total_procesos'] = 0
                    stats['historial_size'] = '0 MB'
                    stats['ultimo_proceso'] = 'N/A'
            except Exception as e:
                print(f"Error leyendo historial: {e}")
                stats['total_procesos'] = 0
                stats['historial_size'] = '0 MB'
                stats['ultimo_proceso'] = 'N/A'
            
            return stats
        
        # Obtener estadísticas
        stats = obtener_stats()
        
        # Crear widgets de estadísticas
        row = 0
        
        # Sección: CÓDIGOS
        tk.Label(frame_stats, text="🔑 CÓDIGOS DE CUMPLIMIENTO", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", pady=(20,10))
        row += 1
        
        tk.Label(frame_stats, text="Total de códigos:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats['total_codigos']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        tk.Label(frame_stats, text="Códigos activos:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats['codigos_activos']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        # Sección: CATÁLOGO
        tk.Label(frame_stats, text="📚 CATÁLOGO BASE", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", pady=(20,10))
        row += 1
        
        tk.Label(frame_stats, text="Total de items:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats['total_items']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        tk.Label(frame_stats, text="Tamaño del archivo:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats['catalogo_size']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        # Sección: HISTORIAL
        tk.Label(frame_stats, text="📊 HISTORIAL DE PROCESOS", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", pady=(20,10))
        row += 1
        
        tk.Label(frame_stats, text="Total de procesos:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats['total_procesos']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        tk.Label(frame_stats, text="Tamaño del archivo:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats['historial_size']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        tk.Label(frame_stats, text="Último proceso:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats['ultimo_proceso']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        # 👈 NUEVA SECCIÓN: ARCHIVOS PROCESADOS
        tk.Label(frame_stats, text="📁 ARCHIVOS PROCESADOS", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", pady=(20,10))
        row += 1
        
        # Obtener estadísticas de archivos
        stats_archivos = obtener_estadisticas_archivos()
        
        tk.Label(frame_stats, text="Total de archivos:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats_archivos['total_archivos']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        tk.Label(frame_stats, text="Último archivo:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, sticky="w", padx=(20,10))
        tk.Label(frame_stats, text=str(stats_archivos['ultimo_proceso']), font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#ECD925").grid(row=row, column=1, sticky="w")
        row += 1
        
        # Lista de archivos recientes
        if stats_archivos['archivos_recientes']:
            tk.Label(frame_stats, text="Archivos recientes:", font=("Segoe UI", 10), bg="#FFFFFF", fg="#282828").grid(row=row, column=0, columnspan=2, sticky="w", padx=(20,10), pady=(10,5))
            row += 1
            
            # Frame para la lista de archivos
            frame_archivos = tk.Frame(frame_stats, bg="#FFFFFF")
            frame_archivos.grid(row=row, column=0, columnspan=2, sticky="ew", padx=(20,0))
            
            for i, archivo in enumerate(stats_archivos['archivos_recientes'][-3:]):  # Solo los últimos 3
                nombre_corto = archivo['nombre'][:30] + "..." if len(archivo['nombre']) > 30 else archivo['nombre']
                fecha_corta = archivo['fecha_proceso'].split(' ')[0]  # Solo la fecha
                
                tk.Label(frame_archivos, text=f"• {nombre_corto}", font=("Segoe UI", 8), 
                        bg="#FFFFFF", fg="#282828").grid(row=i, column=0, sticky="w")
                tk.Label(frame_archivos, text=fecha_corta, font=("Segoe UI", 8), 
                        bg="#FFFFFF", fg="#ECD925").grid(row=i, column=1, sticky="w", padx=(10,0))
                row += 1
        
        # GRÁFICA DE BARRAS SIMPLE
        tk.Label(frame_graph, text="📈 VISUALIZACIÓN", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#282828").pack(pady=(0,20))
        
        # Crear canvas para la gráfica
        canvas_width = 300
        canvas_height = 200
        canvas = tk.Canvas(frame_graph, width=canvas_width, height=canvas_height, bg="#FFFFFF", highlightthickness=0)
        canvas.pack()
        
        # Dibujar gráfica de barras
        def dibujar_grafica():
            canvas.delete("all")
            
            # Datos para la gráfica
            datos = [
                ("Códigos", stats['total_codigos']),
                ("Catálogo", stats['total_items']),
                ("Historial", stats['total_procesos']),
                ("Archivos", stats_archivos['total_archivos'])
            ]
            
            # Configuración de la gráfica
            margen = 40
            ancho_barra = 50  # Reducido para que quepan 4 barras
            espacio = 15      # Reducido el espacio
            altura_max = 150
            
            # Encontrar el valor máximo para escalar
            max_valor = max([d[1] for d in datos if isinstance(d[1], (int, float))])
            if max_valor == 0:
                max_valor = 1
            
            # Dibujar ejes
            canvas.create_line(margen, altura_max + margen, canvas_width - margen, altura_max + margen, fill="#282828", width=2)
            canvas.create_line(margen, margen, margen, altura_max + margen, fill="#282828", width=2)
            
            # Dibujar barras
            x_inicio = margen + espacio
            for i, (nombre, valor) in enumerate(datos):
                if isinstance(valor, (int, float)) and valor > 0:
                    # Calcular altura de la barra
                    altura_barra = (valor / max_valor) * altura_max
                    
                    # Dibujar barra
                    x1 = x_inicio + (i * (ancho_barra + espacio))
                    y1 = altura_max + margen - altura_barra
                    x2 = x1 + ancho_barra
                    y2 = altura_max + margen
                    
                    canvas.create_rectangle(x1, y1, x2, y2, fill="#ECD925", outline="#282828", width=2)
                    
                    # Texto del valor
                    canvas.create_text(x1 + ancho_barra/2, y1 - 10, text=str(valor), 
                                     font=("Segoe UI", 9, "bold"), fill="#282828")
                    
                    # Texto del nombre
                    canvas.create_text(x1 + ancho_barra/2, altura_max + margen + 20, text=nombre, 
                                     font=("Segoe UI", 8), fill="#282828")
        
        # Dibujar gráfica inicial
        dibujar_grafica()
        
        # Botones en la parte inferior
        frame_botones = tk.Frame(ventana, bg="#FFFFFF")
        frame_botones.pack(pady=20)
        
        # Botón de actualizar
        btn_actualizar = tk.Button(frame_botones, text="🔄 ACTUALIZAR ESTADÍSTICAS", 
                                 command=lambda: [obtener_stats(), dibujar_grafica()],
                                 font=("Segoe UI", 10, "bold"), bg="#ECD925", fg="#282828", 
                                 relief="flat", padx=20, pady=10)
        btn_actualizar.pack(side="left", padx=10)
        
        # 👈 NUEVO: Botón para limpiar historial de archivos
        def limpiar_historial_archivos():
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar el historial de archivos procesados?\nEsta acción no se puede deshacer."):
                try:
                    if os.path.exists(ARCHIVOS_PROCESADOS_FILE):
                        os.remove(ARCHIVOS_PROCESADOS_FILE)
                        messagebox.showinfo("Éxito", "Historial de archivos limpiado correctamente.")
                        # Actualizar dashboard
                        obtener_stats()
                        dibujar_grafica()
                        ventana.destroy()
                        mostrar_estadisticas()  # Reabrir dashboard
                    else:
                        messagebox.showinfo("Info", "No hay historial de archivos para limpiar.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo limpiar el historial:\n{e}")
        
        btn_limpiar = tk.Button(frame_botones, text="🗑️ LIMPIAR HISTORIAL", 
                               command=limpiar_historial_archivos,
                               font=("Segoe UI", 10, "bold"), bg="#FF6B6B", fg="#FFFFFF", 
                               relief="flat", padx=20, pady=10)
        btn_limpiar.pack(side="left", padx=10)
        
        # Botón de cerrar
        btn_cerrar = tk.Button(frame_botones, text="❌ CERRAR", 
                             command=ventana.destroy,
                             font=("Segoe UI", 10, "bold"), bg="#282828", fg="#FFFFFF", 
                             relief="flat", padx=20, pady=10)
        btn_cerrar.pack(side="left", padx=10)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al mostrar estadísticas:\n{e}")
        print(f"Error en dashboard: {e}")

# --- Función unificada para la barra de progreso ---
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
    return config.get("rutas", {})

# VENTANA PRINCIPAL
root = tk.Tk()
root.title("GENERADOR DE TIPO DE PROCESO")
root.geometry("650x570")
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
            logo_img_raw = Image.open(logo_path).resize((150, 100), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(logo_img_raw)
            logo_label = tk.Label(frame_left, image=logo_img, bg="#FFFFFF")
            logo_label.image = logo_img
            logo_label.pack(pady=(20, 20))
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    label = tk.Label(
        frame_left, 
        text="GENERADOR DEL ARCHIVO TIPO DE PROCESO",
        font=("Segoe UI", 12, "bold"), 
        bg="#FFFFFF", 
        fg="#282828"
    )
    label.pack(pady=(0, 5))

    desc = tk.Label(
        frame_left,
        text="SUBE EL REPORTE DE MERCANCIA PARA EL TIPO DE PROCESO.",
        font=("Segoe UI", 8), 
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
        ("⚙️ CONFIGURAR RUTAS", configurar_rutas),
        ("📂 REPORTE DE MERCANCIA", seleccionar_reporte),
        ("📝 EDITOR DE CÓDIGOS", lambda: abrir_editor_codigos(frame_right)), 
        ("📊 DASHBOARD", mostrar_estadisticas),
        ("🔄 ACTUALIZAR CATALOGO", lambda: actualizar_catalogo(frame_right)),
        ("📦 EXPORTAR CATALOGO", lambda: exportar_concentrado_catalogo(frame_right)),
        ("❌ Salir", root.quit)
    ]

    max_width = 10  # ancho uniforme
    for texto, comando in botones:
        btn = ttk.Button(frame_buttons, text=texto.ljust(max_width), command=comando, style='TButton')
        btn.pack(pady=10, ipadx=10, ipady=10, fill="x")

    root.mainloop()

