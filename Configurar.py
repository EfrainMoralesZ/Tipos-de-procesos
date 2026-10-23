import os, sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import Estilos as E

# Carpeta de configuración persistente
CONFIG_DIR = os.path.join(os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath("."), "datos")
os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# -------------------------------
# FUNCIONES DE RUTAS
# -------------------------------
def recurso_path(ruta_relativa):
    """
    Devuelve la ruta correcta de recursos.
    - Para datos (JSON, Excel) => carpeta 'datos' junto al exe.
    - Para recursos estáticos (iconos, etc.) => usar sys._MEIPASS.
    """
    if getattr(sys, "frozen", False):
        # Cuando está en .exe
        base_path = os.path.dirname(sys.executable)  # Carpeta del .exe
    else:
        # Cuando está en .py
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
def cargar_configuracion():
    """Carga la configuración desde el archivo JSON"""
    config_default = {"rutas": {"base_general": "", "codigos_cumple": ""}}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Si falta la clave 'rutas', restaurar estructura
            if not isinstance(config, dict) or "rutas" not in config:
                config = config_default
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
            # Si existe 'historial' en rutas, eliminarlo
            if "rutas" in config and "historial" in config["rutas"]:
                del config["rutas"]["historial"]
                guardar_configuracion(config)
            return config
        except Exception:
            # Archivo corrupto o vacío, restaurar estructura
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_default, f, indent=4)
            return config_default
    else:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_default, f, indent=4)
        return config_default

def guardar_configuracion(config):
    """Guarda la configuración en el archivo JSON"""
    try:
        config["rutas"] = {
            "base_general": config["rutas"].get("base_general", ""),
            "codigos_cumple": config["rutas"].get("codigos_cumple", "")
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar configuración:\n{e}")
        return False

# -------------------------------
# INTERFAZ DE CONFIGURACIÓN
# -------------------------------
def configurar_rutas(parent=None):
    try:
        config = cargar_configuracion()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar configuración:\n{e}")
        return {}

    # Si no se pasa parent, crear un root oculto
    if parent is None:
        parent = ctk.CTk()
        parent.withdraw()

    ventana = E.nueva_ventana(parent, "Configuración de Rutas", 600, 590)

    # --- Funciones internas ---
    import shutil
    def seleccionar_archivo(tipo, label_widget, button_widget):
        archivo = filedialog.askopenfilename(
            title=f"Seleccionar {tipo.replace('_', ' ').title()}",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")],
            parent=ventana
        )
        if archivo:
            # Nombre destino estándar en carpeta Datos
            if tipo == "codigos_cumple":
                destino = os.path.abspath(os.path.join(CONFIG_DIR, "codigos_cumple.xlsx"))
            elif tipo == "base_general":
                destino = os.path.abspath(os.path.join(CONFIG_DIR, "base_general.xlsx"))
            else:
                destino = os.path.abspath(os.path.join(CONFIG_DIR, os.path.basename(archivo)))

            try:
                shutil.copy2(archivo, destino)
                df = pd.read_excel(destino, engine='openpyxl')
                # Convertir a JSON en carpeta Datos
                nombre_json = os.path.splitext(os.path.basename(destino))[0] + ".json"
                json_path = os.path.abspath(os.path.join(CONFIG_DIR, nombre_json))
                df.to_json(json_path, orient="records", force_ascii=False, indent=4)
                messagebox.showinfo("✅ Conversión exitosa", f"Archivo copiado y convertido a JSON:\n{os.path.basename(json_path)}", parent=ventana)
                # Guardar ruta absoluta en config
                config["rutas"][tipo] = destino
            except Exception as e:
                messagebox.showwarning("⚠ Advertencia", f"No se pudo copiar o convertir a JSON:\n{str(e)}", parent=ventana)

            # Actualizar interfaz
            nombre_archivo = os.path.basename(destino)
            if len(nombre_archivo) > 30:
                nombre_archivo = nombre_archivo[:27] + "..."
            mostrar_archivo(label_widget, button_widget, nombre_archivo)
            guardar_configuracion(config)
            actualizar_estado()

    def mostrar_archivo(label_widget, button_widget, nombre_archivo):
        """Refleja en la sección si hay archivo seleccionado o no."""
        if nombre_archivo:
            label_widget.configure(text=f"  {nombre_archivo}", text_color=E.COLOR_TEXTO, image=icono_ok)
            button_widget.configure(text="Cambiar")
            E.estilo_boton(button_widget, "oscuro", "carpeta")
        else:
            label_widget.configure(text="  No seleccionado", text_color=E.COLOR_TEXTO_TENUE, image=icono_vacio)
            button_widget.configure(text="Seleccionar")
            E.estilo_boton(button_widget, "primario", "carpeta")

    def limpiar_configuracion():
        if messagebox.askyesno("🗑️ Limpiar Configuración", "¿Estás seguro de que quieres limpiar toda la configuración?", parent=ventana):
            config["rutas"] = {"base_general": "", "codigos_cumple": ""}
            mostrar_archivo(lbl_codigos, btn_codigos, "")
            mostrar_archivo(lbl_base, btn_base, "")
            guardar_configuracion(config)
            actualizar_estado()
            messagebox.showinfo("✅ Configuración limpiada", "Se han borrado todas las rutas seleccionadas.", parent=ventana)

    def actualizar_estado():
        rutas_configuradas = sum(1 for ruta in config["rutas"].values() if ruta)
        if rutas_configuradas == 2:
            estado_frame.configure(fg_color=E.COLOR_VERDE_FONDO)
            lbl_estado.configure(text="  Configuración completa · Listo para cerrar",
                                 text_color=E.COLOR_VERDE, image=icono_estado_ok)
        elif rutas_configuradas == 1:
            estado_frame.configure(fg_color=E.COLOR_ICONO_FONDO)
            lbl_estado.configure(text="  Falta 1 archivo por configurar", text_color=E.COLOR_TEXTO, image=icono_estado_falta)
        else:
            estado_frame.configure(fg_color=E.COLOR_GRIS)
            lbl_estado.configure(text="  No hay archivos configurados", text_color=E.COLOR_TEXTO_SEC, image=icono_estado_vacio)

    icono_ok = E.crear_icono("check", tam=14, circulo=False, color=E.COLOR_VERDE)
    icono_vacio = E.crear_icono("reporte", tam=14, circulo=False, color=E.COLOR_TEXTO_TENUE)
    icono_estado_ok = E.crear_icono("check", tam=16, circulo=False, color=E.COLOR_VERDE)
    icono_estado_falta = E.crear_icono("reporte", tam=16, circulo=False, color=E.COLOR_TEXTO)
    icono_estado_vacio = E.crear_icono("x", tam=16, circulo=False, color=E.COLOR_TEXTO_SEC)

    # Frame principal
    main_frame = ctk.CTkFrame(ventana, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=32, pady=26)

    # Header
    header, _ = E.encabezado(main_frame, "configurar", "Configuración de Rutas",
                             "Selecciona los archivos necesarios para iniciar el sistema")
    header.pack(fill="x", pady=(0, 20))

    def crear_seccion(icono, titulo, descripcion, tipo):
        seccion = E.card(main_frame)
        seccion.pack(fill="x", pady=(0, 14))

        fila = ctk.CTkFrame(seccion, fg_color="transparent")
        fila.pack(fill="x", padx=20, pady=(18, 12))
        ctk.CTkLabel(fila, text="", image=E.crear_icono(icono, tam=40)).pack(side="left", padx=(0, 12))
        textos = ctk.CTkFrame(fila, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(textos, text=titulo, font=E.fuente(14, "bold"), text_color=E.COLOR_TEXTO,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(textos, text=descripcion, font=E.fuente(11), text_color=E.COLOR_TEXTO_SEC,
                     anchor="w").pack(anchor="w")

        archivo_frame = ctk.CTkFrame(seccion, fg_color=E.COLOR_SUPERFICIE, corner_radius=10)
        archivo_frame.pack(fill="x", padx=20, pady=(0, 18))
        lbl = ctk.CTkLabel(archivo_frame, text="", font=E.fuente(12), anchor="w", compound="left")
        lbl.pack(side="left", padx=14, pady=10)
        btn = E.boton(archivo_frame, "", None, height=32, width=120)
        btn.configure(command=lambda: seleccionar_archivo(tipo, lbl, btn))
        btn.pack(side="right", padx=8, pady=8)

        ruta_actual = config["rutas"].get(tipo, "")
        mostrar_archivo(lbl, btn, os.path.basename(ruta_actual) if ruta_actual else "")
        return lbl, btn

    lbl_codigos, btn_codigos = crear_seccion(
        "reporte", "Códigos de cumplimiento",
        "Archivo Excel con los códigos y criterios de evaluación", "codigos_cumple")
    lbl_base, btn_base = crear_seccion(
        "base", "Base general de datos",
        "Archivo Excel principal con los datos del sistema", "base_general")

    # Estado
    estado_frame = ctk.CTkFrame(main_frame, corner_radius=10)
    estado_frame.pack(fill="x", pady=(4, 18))
    lbl_estado = ctk.CTkLabel(estado_frame, text="", font=E.fuente(12, "bold"), compound="left")
    lbl_estado.pack(pady=9)

    # Botones de acción
    btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    btn_frame.pack(fill="x")
    E.boton(btn_frame, "Cerrar", ventana.destroy, "oscuro", "x", width=130).pack(side="right")
    E.boton(btn_frame, "Limpiar configuración", limpiar_configuracion, "secundario", "basura").pack(side="right", padx=(0, 10))

    # Actualizar estado inicial
    actualizar_estado()

    ventana.wait_window()
    return config["rutas"]

# --- PROGRAMA PRINCIPAL ---
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    configurar_rutas()
