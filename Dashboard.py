import tkinter as tk
from tkinter import filedialog, messagebox
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.utils import ImageReader

# ---------------- Configuración ---------------- #
COL_BG = "#FFFFFF"  # Fondo blanco
COL_TEXT = "#282828"  # Texto oscuro
COL_BTN = "#ECD925"  # Amarillo para botones
COL_LIST_BG = "#d8d8d8"  # Gris claro para lista
COL_BAR = "#ECD925"  # Amarillo para barras
COL_BTN_CERRAR = "#282828"  # Oscuro para botón cerrar

# Colores para las tarjetas
COL_CARD_BG = "#FFFFFF"  # Fondo de tarjetas blanco
COL_BORDER = "#E2E8F0"  # Bordes grises suaves
COL_SUCCESS = "#4CAF50"  # Verde para "Cumple"
COL_DANGER = "#F44336"  # Rojo para "No cumple"
COL_TEXT_LIGHT = "#666666"  # Texto secundario

# ------------------ Rutas seguras para PyInstaller ------------------
def recurso_path(ruta_relativa):
    """Devuelve la ruta absoluta correcta dentro del ejecutable o desarrollo"""
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)

# Rutas de archivos
ARCHIVO_JSON = recurso_path("resources/codigos_cumple.json")
CONFIG_DIR = recurso_path("Guardar Archivos Generados")
ARCHIVOS_PROCESADOS_FILE = recurso_path("Guardar Archivos Generados/archivos_procesados.json")
LOGO_PATH = recurso_path("img/logo_empresarial.png")

# Crear directorios si no existen
os.makedirs(CONFIG_DIR, exist_ok=True)

# Lista global
archivos_procesados = []

# ---------------- Funciones ---------------- #

def cargar_archivos_procesados():
    """Carga la lista de archivos procesados desde el JSON, crea el archivo si no existe"""
    global archivos_procesados
    try:
        if os.path.exists(ARCHIVOS_PROCESADOS_FILE):
            with open(ARCHIVOS_PROCESADOS_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if isinstance(datos, list):
                    archivos_procesados = datos
                else:
                    archivos_procesados = []
                    print("Formato inválido en archivo de procesados")
        else:
            archivos_procesados = []
            # Crear archivo vacío
            with open(ARCHIVOS_PROCESADOS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            print(f"Archivo {ARCHIVOS_PROCESADOS_FILE} no encontrado. Se creó uno nuevo.")
    except Exception as e:
        archivos_procesados = []
        print(f"Error cargando archivos procesados: {e}")
    
    return archivos_procesados

def guardar_archivos_procesados():
    """Guarda la lista de archivos procesados en el archivo JSON"""
    try:
        with open(ARCHIVOS_PROCESADOS_FILE, "w", encoding="utf-8") as f:
            json.dump(archivos_procesados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando archivos procesados: {e}")

def registrar_archivo_procesado(nombre_archivo, fecha_proceso):
    """Registra un archivo procesado en el JSON"""
    try:
        cargar_archivos_procesados()
        
        # Evitar duplicados
        if any(a["nombre"] == nombre_archivo for a in archivos_procesados):
            print(f"[INFO] Archivo ya registrado: {nombre_archivo}")
            return
        
        # Agregar nuevo archivo
        archivo_info = {
            "nombre": nombre_archivo,
            "fecha_proceso": fecha_proceso,
            "fecha_archivo": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        archivos_procesados.append(archivo_info)
        
        # Guardar cambios en el JSON
        guardar_archivos_procesados()
        
        print(f"[OK] Archivo registrado: {nombre_archivo}")
    
    except Exception as e:
        print(f"[ERROR] Error registrando archivo: {e}")

def borrar_archivo_procesados():
    """Elimina físicamente el archivo JSON de archivos procesados"""
    try:
        if os.path.exists(ARCHIVOS_PROCESADOS_FILE):
            os.remove(ARCHIVOS_PROCESADOS_FILE)
            return True
        return False
    except Exception as e:
        print(f"❌ Error al borrar archivo de procesados: {e}")
        return False

def actualizar_lista_archivos(lst_archivos):
    """Actualiza la lista visual con los archivos procesados"""
    lst_archivos.delete(0, tk.END)
    cargar_archivos_procesados()  # Asegurarse de tener datos actualizados
    
    for archivo in archivos_procesados:
        # Si el archivo es un string (solo nombre), mostrarlo tal cual
        if isinstance(archivo, str):
            lst_archivos.insert(tk.END, archivo)
        # Si es un diccionario, mostrar el nombre o información relevante
        elif isinstance(archivo, dict) and 'nombre' in archivo:
            lst_archivos.insert(tk.END, archivo['nombre'])
        else:
            # Mostrar representación string para otros tipos
            lst_archivos.insert(tk.END, str(archivo))

def limpiar_lista(lst_archivos):
    """Limpia la lista de archivos procesados y elimina el archivo JSON"""
    global archivos_procesados
    archivos_procesados = []

    # Intentar borrar el JSON
    if borrar_archivo_procesados():
        messagebox.showinfo("🗑️ Lista Limpiada", "Se han eliminado todos los archivos de la lista")
    else:
        # Si no se pudo borrar el archivo, al menos guardar lista vacía
        guardar_archivos_procesados()
        messagebox.showinfo("🗑️ Lista Limpiada", "Se han eliminado todos los archivos de la lista")

    # Actualizar visualización de la lista en la interfaz
    actualizar_lista_archivos(lst_archivos)

def leer_datos():
    """Lee los datos del archivo JSON y calcula estadísticas"""
    total_codigos = 0
    codigos_cumple = 0
    codigos_no_cumple = 0
    
    try:
        print(f"Leyendo archivo JSON desde: {ARCHIVO_JSON}")
        
        if not os.path.exists(ARCHIVO_JSON):
            print("❌ El archivo JSON no existe. Creando uno vacío...")
            # Crear archivo JSON vacío si no existe
            with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            return 0, 0, 0
        
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            codigos_data = json.load(f)
            print(f"Datos leídos: {len(codigos_data)} registros")
            
            # Verificar estructura de los datos
            if codigos_data and isinstance(codigos_data, list):
                print(f"Primer registro: {codigos_data[0]}")
            
        for d in codigos_data:
            if not isinstance(d, dict):
                continue
                
            total_codigos += 1
            obs = str(d.get("OBSERVACIONES", "")).upper().strip()
            
            print(f"Item: {d.get('ITEM', 'N/A')}, Observación: '{obs}'")
            
            if obs == "CUMPLE":
                codigos_cumple += 1
            else:
                codigos_no_cumple += 1
                
        print(f"Estadísticas: Total={total_codigos}, Cumple={codigos_cumple}, No Cumple={codigos_no_cumple}")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: El archivo JSON está corrupto o vacío: {e}")
        return 0, 0, 0
    except Exception as e:
        print(f"❌ Error leyendo JSON: {e}")
        return 0, 0, 0
        
    return total_codigos, codigos_cumple, codigos_no_cumple

def dibujar_grafica(canvas, lbl_totales, lst_archivos):
    """Dibuja la gráfica y actualiza las estadísticas"""
    try:
        canvas.delete("all")
        total_codigos, codigos_cumple, codigos_no_cumple = leer_datos()
        
        # --- Actualizar labels ---
        lbl_total_valor.config(text=f"{total_codigos}")
        lbl_cumple_valor.config(text=f"{codigos_cumple}")
        lbl_no_cumple_valor.config(text=f"{codigos_no_cumple}")
        
        porcentaje_cumple = (codigos_cumple / total_codigos * 100) if total_codigos > 0 else 0
        porcentaje_no_cumple = (codigos_no_cumple / total_codigos * 100) if total_codigos > 0 else 0
        
        lbl_cumple_porcentaje.config(text=f"{porcentaje_cumple:.1f}%")
        lbl_no_cumple_porcentaje.config(text=f"{porcentaje_no_cumple:.1f}%")
        
        lbl_totales["text"] = f"Total: {total_codigos}  |  Cumple: {codigos_cumple}  |  No cumple: {codigos_no_cumple}"

        # Solo dibujar gráfica si hay datos
        if total_codigos > 0:
            # --- Datos para las barras ---
            datos = [
                ("Total de Códigos", total_codigos),
                ("Códigos Cumple", codigos_cumple),
                ("Códigos No cumple", codigos_no_cumple)
            ]

            # --- Ajustes de espacio dinámicos ---
            ancho, alto = int(canvas["width"]), int(canvas["height"])
            margen_sup = 30
            margen_inf = 60
            margen_lat = 20
            ancho_barra = 80
            espacio = 60

            altura_max = alto - (margen_sup + margen_inf)
            max_valor = max([v for _, v in datos], default=1)

            # --- Dibujar ejes ---
            eje_x_y = alto - margen_inf
            canvas.create_line(margen_lat, eje_x_y, ancho - margen_lat, eje_x_y, fill=COL_TEXT, width=2)
            canvas.create_line(margen_lat, margen_sup, margen_lat, eje_x_y, fill=COL_TEXT, width=2)

            # --- Dibujar barras ---
            x_inicio = margen_lat + espacio
            for i, (nombre, valor) in enumerate(datos):
                altura_barra = (valor / max_valor) * altura_max if valor > 0 else 0
                x1 = x_inicio + i * (ancho_barra + espacio)
                y1 = eje_x_y - altura_barra
                x2 = x1 + ancho_barra
                y2 = eje_x_y
                
                # Color por categoría
                if nombre == "Códigos Cumple":
                    color = COL_SUCCESS
                elif nombre == "Códigos No cumple":
                    color = COL_DANGER
                else:
                    color = COL_BAR
                    
                # Barra
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=COL_TEXT, width=1.5)
                # Valor encima
                canvas.create_text((x1 + x2) / 2, y1 - 10, text=str(valor), font=("INTER", 9, "bold"), fill=COL_TEXT)
                # Etiqueta abajo
                canvas.create_text((x1 + x2) / 2, eje_x_y + 20, text=nombre, font=("INTER", 8, "bold"), 
                                  fill=COL_TEXT, width=100, justify='center')
        else:
            # Mostrar mensaje si no hay datos
            ancho, alto = int(canvas["width"]), int(canvas["height"])
            canvas.create_text(ancho/2, alto/2, text="No hay datos disponibles\nVerifique el archivo JSON", 
                              font=("INTER", 10), fill=COL_TEXT_LIGHT, justify='center')

        # --- Actualizar lista de archivos ---
        actualizar_lista_archivos(lst_archivos)

    except Exception as e:
        print(f"Error en dibujar_grafica: {e}")
    
    # --- Auto-refresh cada 2 segundos ---
    canvas.after(2000, lambda: dibujar_grafica(canvas, lbl_totales, lst_archivos))

def crear_tarjeta(parent, titulo, valor, porcentaje=None, color=COL_BAR):
    """Crea una tarjeta de estadística moderna"""
    frame = tk.Frame(parent, bg=COL_CARD_BG, relief="flat", bd=1, 
                    highlightbackground=COL_BORDER, highlightthickness=1)
    
    # Título
    lbl_titulo = tk.Label(frame, text=titulo, bg=COL_CARD_BG, fg=COL_TEXT_LIGHT, 
                         font=("INTER", 9))
    lbl_titulo.pack(pady=(8, 3))
    
    # Valor principal
    lbl_valor = tk.Label(frame, text=valor, bg=COL_CARD_BG, fg=color, 
                        font=("INTER", 14, "bold"))
    lbl_valor.pack(pady=3)
    
    # Porcentaje (opcional)
    if porcentaje:
        lbl_porcentaje = tk.Label(frame, text=porcentaje, bg=COL_CARD_BG, fg=COL_TEXT_LIGHT,
                                 font=("INTER", 8))
        lbl_porcentaje.pack(pady=(0, 8))
    
    return frame, lbl_valor, lbl_porcentaje if porcentaje else (frame, lbl_valor, None)



# ---------------- Exportar PDF ---------------- #
def exportar_pdf_simple():
    """Genera un PDF simple con estadísticas"""
    try:
        # Obtener estadísticas actuales
        total_codigos, codigos_cumple, codigos_no_cumple = leer_datos()
        porcentaje_cumple = (codigos_cumple / total_codigos * 100) if total_codigos > 0 else 0
        porcentaje_no_cumple = (codigos_no_cumple / total_codigos * 100) if total_codigos > 0 else 0
        
        # Preparar datos para el PDF
        stats = {
            'total_codigos': total_codigos,
            'codigos_cumple': codigos_cumple,
            'porcentaje_cumple': porcentaje_cumple,
            'codigos_no_cumple': codigos_no_cumple,
            'porcentaje_no_cumple': porcentaje_no_cumple,
            'total_procesos': len(archivos_procesados),
            'total_items': total_codigos
        }
        
        # Preparar información de archivos
        stats_archivos = {
            'total_archivos': len(archivos_procesados),
            'ultimo_proceso': archivos_procesados[-1] if archivos_procesados else "Ninguno",
            'archivos_recientes': archivos_procesados if archivos_procesados else []
        }
        
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

        # Encabezado con logo en la parte derecha
        c.setFillColor("#ecd925")
        c.rect(0, alto - 20, ancho, 20, fill=1, stroke=0)

        # Agregar logo empresarial en la parte derecha del encabezado
        try:
            if os.path.exists(LOGO_PATH):
                logo = ImageReader(LOGO_PATH)
                c.drawImage(logo, ancho - 100, alto - 70, width=50, height=50, preserveAspectRatio=True)
            else:
                print(f"Logo no encontrado en: {LOGO_PATH}")
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

        c.setFillColor("#282828")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, alto - 50, "REPORTE DE ESTADÍSTICAS")

        c.setFont("Helvetica", 10)
        c.drawString(50, alto - 70, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        y = alto - 120

        # Estadísticas principales
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "ESTADÍSTICAS PRINCIPALES")
        y -= 30

        c.setFont("Helvetica", 10)
        c.drawString(70, y, f"• Total de códigos: {stats['total_codigos']}")
        y -= 20
        c.drawString(70, y, f"• Códigos que cumplen: {stats['codigos_cumple']} ({stats['porcentaje_cumple']:.1f}%)")
        y -= 20
        c.drawString(70, y, f"• Códigos que no cumplen: {stats['codigos_no_cumple']} ({stats['porcentaje_no_cumple']:.1f}%)")
        y -= 20

        # Archivos procesados
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "ARCHIVOS PROCESADOS")
        y -= 30

        c.setFont("Helvetica", 10)
        c.drawString(70, y, f"• Total de archivos: {stats_archivos['total_archivos']}")
        y -= 20

        # Archivos recientes
        # Preparar información de archivos
        stats_archivos = {
            'total_archivos': len(archivos_procesados),
            'ultimo_proceso': archivos_procesados[-1] if archivos_procesados else "Ninguno",
            'archivos_recientes': archivos_procesados if archivos_procesados else []  # <-- todos los archivos
        }

        # Archivos recientes
        if stats_archivos['archivos_recientes']:
            c.drawString(70, y, "Archivos recientes:")
            y -= 15
            for archivo in stats_archivos['archivos_recientes']:
                nombre_archivo = archivo if isinstance(archivo, str) else archivo.get('nombre', str(archivo))
                c.drawString(90, y, f"• {nombre_archivo}")
                y -= 15
            y -= 10

        # --- Crear gráfica de pastel ---
        if total_codigos > 0:
            etiquetas = ["Códigos Cumple", "Códigos No Cumple"]
            valores = [codigos_cumple, codigos_no_cumple]
            colores = ["#ECD925", "#282828"]
            porcentajes = [porcentaje_cumple, porcentaje_no_cumple]

            plt.figure(figsize=(8, 6))
            wedges, texts, autotexts = plt.pie(valores, labels=etiquetas, colors=colores, autopct='%1.1f%%',
                                              startangle=90, textprops={'fontsize': 12, 'color': '#282828'})

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)

            for text in texts:
                text.set_fontsize(12)
                text.set_fontweight('bold')

            plt.title("Distribución de Códigos", fontsize=16, fontweight='bold', color="#282828", pad=20)
            plt.axis('equal')

            leyenda_labels = [f'{etiqueta}: {valor} ({porcentaje:.1f}%)' 
                             for etiqueta, valor, porcentaje in zip(etiquetas, valores, porcentajes)]
            plt.legend(wedges, leyenda_labels, title="Estadísticas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format="PNG", dpi=150, bbox_inches='tight')
            plt.close()
            buf.seek(0)

            imagen_grafica = ImageReader(buf)
            c.drawImage(imagen_grafica, 50, y - 280, width=500, height=280)

        # --- Pie de página con fondo #282828 ---
        c.setFillColor("#282828")
        c.rect(0, 0, ancho, 30, fill=1, stroke=0)
        c.setFillColor("#FFFFFF")
        c.setFont("Helvetica", 8)
        c.drawString(50, 15, "Sistema de Tipos de Procesos V&C")
        
        texto_centro = "www.vandc.com"
        ancho_texto_centro = c.stringWidth(texto_centro, "Helvetica", 8)
        c.drawString((ancho - ancho_texto_centro) / 2, 15, texto_centro)
        
        texto_derecho = f"Página 1"
        ancho_texto_derecho = c.stringWidth(texto_derecho, "Helvetica", 8)
        c.drawString(ancho - ancho_texto_derecho - 50, 15, texto_derecho)

        c.save()
        messagebox.showinfo("Éxito", f"PDF generado correctamente en:\n{ruta}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")
        print(f"Error detallado: {e}")

# ---------------- Ventana principal ---------------- #

def main():
    global lbl_total_valor, lbl_cumple_valor, lbl_cumple_porcentaje, lbl_no_cumple_valor, lbl_no_cumple_porcentaje

    root = tk.Tk()
    root.title("Dashboard de Códigos - V&C")
    root.geometry("1000x600")
    root.configure(bg=COL_BG)

    # Cargar archivos procesados al iniciar
    cargar_archivos_procesados()

    # Frame principal
    main_container = tk.Frame(root, bg=COL_BG)
    main_container.pack(fill="both", expand=True, padx=15, pady=15)

    # Header
    header_frame = tk.Frame(main_container, bg=COL_BG)
    header_frame.pack(fill="x", pady=(0, 10))

    lbl_titulo = tk.Label(header_frame, text="📊 Dashboard de Análisis de Códigos",
                          bg=COL_BG, fg=COL_TEXT, font=("INTER", 16, "bold"))
    lbl_titulo.pack(side="left")

    lbl_subtitulo = tk.Label(header_frame, text="Reporte de Mercancía - V&C",
                             bg=COL_BG, fg=COL_TEXT_LIGHT, font=("INTER", 10))
    lbl_subtitulo.pack(side="left", padx=(10, 0))

    # Tarjetas
    stats_frame = tk.Frame(main_container, bg=COL_BG)
    stats_frame.pack(fill="x", pady=(0, 10))

    tarjeta_total, lbl_total_valor, _ = crear_tarjeta(stats_frame, "TOTAL DE CÓDIGOS", "0", color=COL_BAR)
    tarjeta_total.pack(side="left", padx=(0, 10), fill="both", expand=True)

    tarjeta_cumple, lbl_cumple_valor, lbl_cumple_porcentaje = crear_tarjeta(stats_frame, "CÓDIGOS CUMPLEN", "0", "0%", color=COL_SUCCESS)
    tarjeta_cumple.pack(side="left", padx=(0, 10), fill="both", expand=True)

    tarjeta_no_cumple, lbl_no_cumple_valor, lbl_no_cumple_porcentaje = crear_tarjeta(stats_frame, "CÓDIGOS NO CUMPLEN", "0", "0%", color=COL_DANGER)
    tarjeta_no_cumple.pack(side="left", fill="both", expand=True)

    # Contenido principal
    content_frame = tk.Frame(main_container, bg=COL_BG)
    content_frame.pack(fill="both", expand=True, pady=10)

    # Frame izquierdo para la gráfica
    left_frame = tk.Frame(content_frame, bg=COL_BG)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    # Gráfica
    graph_card = tk.Frame(left_frame, bg=COL_CARD_BG, relief="flat", bd=1,
                          highlightbackground=COL_BORDER, highlightthickness=1)
    graph_card.pack(fill="both", expand=True)

    lbl_graph_title = tk.Label(graph_card, text="DISTRIBUCIÓN DE CÓDIGOS",
                               bg=COL_CARD_BG, fg=COL_TEXT, font=("INTER", 11, "bold"))
    lbl_graph_title.pack(pady=(10, 5))

    canvas_grafica = tk.Canvas(graph_card, width=400, height=250,
                               bg=COL_CARD_BG, highlightthickness=0)
    canvas_grafica.pack(pady=(0, 5), padx=10, fill="both", expand=True)

    lbl_totales = tk.Label(graph_card, text="", bg=COL_CARD_BG,
                           fg=COL_TEXT_LIGHT, font=("INTER", 9))
    lbl_totales.pack(pady=(0, 10))

    # Frame derecho para archivos
    right_frame = tk.Frame(content_frame, bg=COL_BG, width=400)
    right_frame.pack(side="right", fill="y")
    right_frame.pack_propagate(False)

    files_card = tk.Frame(right_frame, bg=COL_CARD_BG, relief="flat", bd=1,
                          highlightbackground=COL_BORDER, highlightthickness=1)
    files_card.pack(fill="both", expand=True)

    lbl_archivos = tk.Label(files_card, text="📁 ARCHIVOS PROCESADOS",
                            bg=COL_CARD_BG, fg=COL_TEXT, font=("INTER", 11, "bold"))
    lbl_archivos.pack(pady=(10, 5))

    list_frame = tk.Frame(files_card, bg=COL_CARD_BG)
    list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    lst_archivos = tk.Listbox(list_frame, bg=COL_LIST_BG, fg=COL_TEXT, font=("INTER", 9),
                              yscrollcommand=scrollbar.set, relief="flat", bd=0,
                              highlightthickness=0)
    lst_archivos.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=lst_archivos.yview)

    # Footer con botones
    footer_frame = tk.Frame(main_container, bg=COL_BG)
    footer_frame.pack(fill="x", pady=(10, 0))

    btn_limpiar = tk.Button(footer_frame, text="🗑️ Limpiar Lista",
                            command=lambda: limpiar_lista(lst_archivos),
                            bg=COL_TEXT_LIGHT, fg="white", font=("INTER", 9, "bold"),
                            relief="flat", padx=15, pady=6, cursor="hand2")
    btn_limpiar.pack(side="left", padx=(0, 5))

    btn_exportar = tk.Button(footer_frame, text="📊 Exportar PDF",
                             command=exportar_pdf_simple,
                             bg=COL_BTN, fg=COL_TEXT, font=("INTER", 9, "bold"),
                             relief="flat", padx=15, pady=6, cursor="hand2")
    btn_exportar.pack(side="left", padx=(0, 5))

    btn_cerrar = tk.Button(footer_frame, text="❌ Cerrar",
                           command=root.destroy,
                           bg=COL_BTN_CERRAR, fg="white", font=("INTER", 9, "bold"),
                           relief="flat", padx=15, pady=6, cursor="hand2")
    btn_cerrar.pack(side="right")

    # Dibujar gráfica inicial
    dibujar_grafica(canvas_grafica, lbl_totales, lst_archivos)

    # Centrar ventana
    root.eval('tk::PlaceWindow . center')
    root.mainloop()

if __name__ == "__main__":
    main()