import tkinter as tk
from tkinter import filedialog, messagebox
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
import os
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.utils import ImageReader

# ---------------- Configuración ---------------- #
ARCHIVO_JSON = "resources/codigos_cumple.json"
archivos_procesados = []

COL_BG = "#FFFFFF"
COL_TEXT = "#282828"
COL_BTN = "#ECD925"
COL_LIST_BG = "#d8d8d8"
COL_BAR = "#ECD925"
COL_BTN_CERRAR = "#282828"

# ---------------- Funciones ---------------- #

def leer_datos():
    total_codigos = 0
    codigos_cumple = 0
    codigos_revisados = 0
    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            codigos_data = json.load(f)
        for d in codigos_data:
            if not isinstance(d, dict) or "ITEM" not in d:
                continue
            total_codigos += 1
            obs = str(d.get("OBSERVACIONES", "")).upper()
            if obs == "CUMPLE":
                codigos_cumple += 1
            else:
                codigos_revisados += 1
    except Exception as e:
        print(f"Error leyendo JSON: {e}")
    return total_codigos, codigos_cumple, codigos_revisados

def dibujar_grafica(canvas, lbl_totales):
    canvas.delete("all")
    total_codigos, codigos_cumple, codigos_revisados = leer_datos()
    lbl_totales["text"] = f"Total: {total_codigos}  |  Cumple: {codigos_cumple}  |  No cumple: {codigos_revisados}"

    datos = [
        ("Total de Códigos", total_codigos),
        ("Códigos Cumple", codigos_cumple),
        ("Códigos No cumple", codigos_revisados)
    ]

    ancho, alto = int(canvas["width"]), int(canvas["height"])
    margen = 50
    ancho_barra = 80
    espacio = 60
    altura_max = alto - 2 * margen
    max_valor = max([v for _, v in datos], default=1)
    if max_valor == 0:
        max_valor = 1

    # Ejes
    canvas.create_line(margen, altura_max + margen, ancho - margen, altura_max + margen, fill=COL_TEXT, width=2)
    canvas.create_line(margen, margen, margen, altura_max + margen, fill=COL_TEXT, width=2)

    # Barras
    x_inicio = margen + espacio
    for i, (nombre, valor) in enumerate(datos):
        altura_barra = (valor / max_valor) * altura_max if valor > 0 else 0
        x1 = x_inicio + i * (ancho_barra + espacio)
        y1 = altura_max + margen - altura_barra
        x2 = x1 + ancho_barra
        y2 = altura_max + margen
        canvas.create_rectangle(x1, y1, x2, y2, fill=COL_BAR, outline=COL_TEXT, width=1.5)
        canvas.create_text((x1 + x2) / 2, y1 - 15, text=str(valor), font=("INTER", 10, "bold"), fill=COL_TEXT)
        canvas.create_text((x1 + x2) / 2, altura_max + margen + 20, text=nombre, font=("INTER", 10, "bold"), fill=COL_TEXT)

    # Auto-refresh cada 2 segundos
    canvas.after(2000, lambda: dibujar_grafica(canvas, lbl_totales))

def actualizar_archivos(lst_archivos):
    global archivos_procesados
    archivos = filedialog.askopenfilenames(title="Seleccionar archivos procesados", filetypes=[("JSON", "*.json"), ("Excel", "*.xlsx")])
    if archivos:
        archivos_procesados.extend(archivos)
        lst_archivos.delete(0, tk.END)
        for f in archivos_procesados:
            lst_archivos.insert(tk.END, os.path.basename(f))
        messagebox.showinfo("Actualizar", f"{len(archivos)} archivos agregados.")

def limpiar_lista(lst_archivos):
    global archivos_procesados
    archivos_procesados = []
    lst_archivos.delete(0, tk.END)

# --- Función para generar el PDF con plantilla ---
def exportar_pdf(stats, stats_archivos):
    try:
        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar Reporte de Estadísticas"
        )
        if not ruta:
            return

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

        # --- Estadísticas ---
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "ESTADÍSTICAS PRINCIPALES")
        y -= 30

        c.setFont("Helvetica", 12)
        c.drawString(70, y, f"• Total de códigos: {stats['total_codigos']}")
        y -= 20
        c.drawString(70, y, f"• Códigos que cumplen: {stats['codigos_cumple']} ({stats['porcentaje_cumple']:.1f}%)")
        y -= 20
        c.drawString(70, y, f"• Códigos revisados: {stats['codigos_no_cumple']}")
        y -= 20
        c.drawString(70, y, f"• Total de procesos: {stats['total_procesos']}")
        y -= 20
        c.drawString(70, y, f"• Items en catálogo: {stats['total_items']}")
        y -= 30

        # --- Archivos procesados ---
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "ARCHIVOS PROCESADOS")
        y -= 30

        c.setFont("Helvetica", 12)
        c.drawString(70, y, f"• Total de archivos: {stats_archivos['total_archivos']}")
        y -= 20
        c.drawString(70, y, f"• Último archivo: {stats_archivos['ultimo_proceso']}")
        y -= 30

        if stats_archivos['archivos_recientes']:
            c.drawString(70, y, "Archivos recientes:")
            y -= 15
            for archivo in stats_archivos['archivos_recientes'][-3:]:
                c.drawString(90, y, f"• {archivo['nombre']} ({archivo['fecha_proceso']})")
                y -= 15
            y -= 10

        # --- Pie de página ---
        c.setFillColor("#282828")
        c.rect(0, 0, ancho, 30, fill=1, stroke=0)
        c.setFillColor("#FFFFFF")
        c.setFont("Helvetica", 8)
        c.drawString(50, 10, "Generado por Sistema de Procesos")

        c.save()
        messagebox.showinfo("Éxito", f"PDF generado correctamente en:\n{ruta}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")
        print(f"Error detallado: {e}")

# --- Nueva función para exportar PDF simple ---
def exportar_pdf_simple():
    """Genera un PDF simple con estadísticas"""
    try:
        # Obtener estadísticas actuales
        total_codigos, codigos_cumple, codigos_no_cumple = leer_datos()
        porcentaje_cumple = (codigos_cumple / total_codigos * 100) if total_codigos > 0 else 0
        
        # Preparar datos para el PDF
        stats = {
            'total_codigos': total_codigos,
            'codigos_cumple': codigos_cumple,
            'porcentaje_cumple': porcentaje_cumple,
            'codigos_no_cumple': codigos_no_cumple,
            'total_procesos': len(archivos_procesados),
            'total_items': total_codigos  # Asumiendo que es lo mismo para este ejemplo
        }
        
        # Preparar información de archivos
        stats_archivos = {
            'total_archivos': len(archivos_procesados),
            'ultimo_proceso': os.path.basename(archivos_procesados[-1]) if archivos_procesados else "Ninguno",
            'archivos_recientes': [{'nombre': os.path.basename(f), 'fecha_proceso': datetime.now().strftime('%d/%m/%Y')} 
                                  for f in archivos_procesados[-3:]]  # Últimos 3 archivos
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
        c.rect(0, alto - 80, ancho, 80, fill=1, stroke=0)

        # Agregar logo empresarial en la parte derecha del encabezado
        try:
            # Ajusta la ruta según la ubicación de tu logo
            logo_path = "img/logo_empresarial.png"  # o "img/logo_empresarial.jpg"
            if os.path.exists(logo_path):
                logo = ImageReader(logo_path)
                # Dibujar el logo en la parte derecha (posición X: ancho - 100, Y: alto - 130)
                c.drawImage(logo, ancho - 100, alto - 130, width=50, height=50, preserveAspectRatio=True)
            else:
                print(f"Logo no encontrado en: {logo_path}")
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

        c.setFillColor("#282828")
        c.setFont("Helvetica-Bold", 20)
        # Título centrado o a la izquierda
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
        c.drawString(70, y, f"• Códigos que no cumplen: {stats['codigos_no_cumple']}")
        y -= 20
        c.drawString(70, y, f"• Total de procesos: {stats['total_procesos']}")
        y -= 20
        c.drawString(70, y, f"• Items en catálogo: {stats['total_items']}")
        y -= 30

        # Archivos procesados
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "ARCHIVOS PROCESADOS")
        y -= 30

        c.setFont("Helvetica", 10)
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

        # --- Crear gráfica con las 3 columnas como en el dashboard ---
        nombres = ["Total de Códigos", "Códigos Cumple", "Códigos No cumple"]
        valores = [total_codigos, codigos_cumple, codigos_no_cumple]
        colores = ["#ECD925", "#ECD925", "#ECD925"]  # Mismo color para todas las barras

        # Configurar la gráfica
        plt.figure(figsize=(8, 5))
        bars = plt.bar(nombres, valores, color=colores, edgecolor="#282828", linewidth=1.5)

        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=12, fontweight='bold', color="#282828")

        plt.title("Estadísticas de Códigos", fontsize=14, fontweight='bold', color="#282828", pad=20)
        plt.ylabel("Cantidad", fontsize=12, color="#282828")
        plt.xticks(rotation=0, fontsize=10, color="#282828")
        plt.yticks(color="#282828")
        
        # Ajustar el diseño para que no se corten las etiquetas
        plt.tight_layout()

        # Guardar la gráfica en un buffer
        buf = BytesIO()
        plt.savefig(buf, format="PNG", dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)

        # Añadir la gráfica al PDF
        imagen_grafica = ImageReader(buf)
        c.drawImage(imagen_grafica, 50, y - 250, width=500, height=250)

        # --- Pie de página ---
        c.setFillColor("#282828")
        c.rect(0, 0, ancho, 30, fill=1, stroke=0)
        c.setFillColor("#FFFFFF")
        c.setFont("Helvetica", 8)
        c.drawString(50, 10, "Generado por Sistema de Procesos  vyc.com.mx")

        # Guardar PDF
        c.save()
        messagebox.showinfo("Éxito", f"PDF generado correctamente en:\n{ruta}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")
        print(f"Error detallado: {e}")

# ---------------- Ventana principal ---------------- #

root = tk.Tk()
root.title("Dashboard de Códigos")
root.geometry("1000x600")
root.configure(bg=COL_BG)

# Título
lbl_titulo = tk.Label(root, text="📊 Dashboard de Códigos", font=("INTER", 16, "bold"), bg=COL_BG, fg=COL_TEXT)
lbl_titulo.pack(pady=10)

# ---------------- Frame principal ---------------- #
frame_main = tk.Frame(root, bg=COL_BG)
frame_main.pack(fill="both", expand=True, padx=10, pady=10)

# Columna izquierda (totales y lista)
frame_izq = tk.Frame(frame_main, bg=COL_BG)
frame_izq.pack(side="left", fill="y", padx=(0, 20))

# Totales
lbl_totales = tk.Label(frame_izq, text="", bg=COL_BG, font=("INTER", 12, "bold"), fg=COL_TEXT)
lbl_totales.pack(pady=5)

# Lista archivos
lbl_archivos = tk.Label(frame_izq, text="Archivos Procesados:", bg=COL_BG, font=("INTER", 12, "bold"), fg=COL_TEXT)
lbl_archivos.pack(anchor="w", pady=(20, 5))

lst_archivos = tk.Listbox(frame_izq, bg=COL_LIST_BG, fg=COL_TEXT, font=("INTER", 11))
lst_archivos.pack(fill="both", expand=True, pady=5)

# Columna derecha (gráfica)
frame_der = tk.Frame(frame_main, bg=COL_BG)
frame_der.pack(side="left", fill="both", expand=True)

canvas_grafica = tk.Canvas(frame_der, width=600, height=400, bg=COL_BG, highlightthickness=0)
canvas_grafica.pack(pady=10, padx=10)

# ---------------- Botones inferiores ---------------- #
frame_botones = tk.Frame(root, bg=COL_BG)
frame_botones.pack(pady=10)

btn_limpiar = tk.Button(frame_botones, text="Limpiar Lista", command=lambda: limpiar_lista(lst_archivos),
                        bg=COL_BTN, fg=COL_TEXT, font=("INTER", 11, "bold"), relief="flat", padx=20, pady=8)
btn_limpiar.pack(side="left", padx=10)

btn_exportar = tk.Button(frame_botones, text="Exportar PDF", command=exportar_pdf_simple,
                         bg=COL_BTN, fg=COL_TEXT, font=("INTER", 11, "bold"), relief="flat", padx=20, pady=8)
btn_exportar.pack(side="left", padx=10)

btn_cerrar = tk.Button(frame_botones, text="Cerrar", command=root.destroy,
                       bg=COL_BTN_CERRAR, fg="#FFFFFF", font=("INTER", 11, "bold"), relief="flat", padx=20, pady=8)
btn_cerrar.pack(side="left", padx=10)

# Iniciar grafica
dibujar_grafica(canvas_grafica, lbl_totales)

root.mainloop()