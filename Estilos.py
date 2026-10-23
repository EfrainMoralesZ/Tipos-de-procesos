"""Paleta, iconos y componentes de customtkinter compartidos por todas las ventanas."""
import math
import os
import sys
from tkinter import ttk

import customtkinter as ctk
from PIL import Image, ImageDraw

#  PALETA DE COLORES
COLOR_FONDO = "#F4F5F7"
COLOR_CARD = "#FFFFFF"
COLOR_SUPERFICIE = "#F8F9FA"
COLOR_BORDE = "#E6E7EB"
COLOR_BORDE_FUERTE = "#D1D5DB"
COLOR_AMARILLO = "#ECD925"
COLOR_AMARILLO_HOVER = "#D6BC00"
COLOR_ICONO_FONDO = "#FBF0A8"
COLOR_TEXTO = "#1F1F1F"
COLOR_TEXTO_SEC = "#4B5563"
COLOR_TEXTO_TENUE = "#6B7280"
COLOR_OSCURO = "#282828"
COLOR_OSCURO_HOVER = "#1A1A1A"
COLOR_GRIS = "#E6E7EB"
COLOR_GRIS_HOVER = "#D5D7DC"
COLOR_ROJO = "#E5484D"
COLOR_ROJO_HOVER = "#C93C40"
COLOR_VERDE = "#2E9E5B"
COLOR_VERDE_FONDO = "#E7F6EC"
COLOR_AZUL = "#2563EB"
COLOR_AZUL_FONDO = "#E8EFFD"
COLOR_FILA_ALTERNA = "#FAFAFB"

FUENTE = "Inter"

if getattr(sys, "frozen", False):
    _BASE_RECURSOS = sys._MEIPASS
else:
    _BASE_RECURSOS = os.path.dirname(os.path.abspath(__file__))
ICONO_APP = os.path.join(_BASE_RECURSOS, "img", "icono.ico")


def fuente(tam=12, peso="normal"):
    return ctk.CTkFont(FUENTE, tam, peso)


#  ICONOS DIBUJADOS CON PIL
def crear_icono(tipo, tam=64, circulo=True, color=COLOR_TEXTO, escala=4):
    """Dibuja un icono de línea y lo devuelve como CTkImage.

    circulo=True lo coloca dentro de un círculo amarillo pálido (iconos de encabezado);
    circulo=False dibuja solo el trazo, ampliado para ocupar el tamaño (iconos de botón).
    """
    S = tam * escala
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fondo = COLOR_ICONO_FONDO if circulo else (0, 0, 0, 0)
    if circulo:
        d.ellipse((0, 0, S - 1, S - 1), fill=COLOR_ICONO_FONDO)

    c = S / 2
    k = 1.0 if circulo else 1.75  # sin círculo el trazo ocupa casi todo el lienzo
    w = max(1, int(S * 0.045 * k))  # grosor de línea
    tinta = color

    def p(x, y):
        """Convierte coordenadas relativas al centro (fracción de S) a píxeles."""
        return (c + x * S * k, c + y * S * k)

    def caja(x1, y1, x2, y2):
        return (*p(x1, y1), *p(x2, y2))

    def circulo_en(cx, cy, r, **kw):
        d.ellipse(caja(cx - r, cy - r, cx + r, cy + r), **kw)

    def linea(*puntos):
        d.line([p(x, y) for x, y in puntos], fill=tinta, width=w, joint="curve")

    if tipo == "configurar":
        # Engrane: dientes + anillo, luego se vacía el centro
        for i in range(8):
            a = i * math.pi / 4
            ancho = 0.055
            pts = []
            for dx, dy in ((-ancho, 0.0), (ancho, 0.0), (ancho, 0.27), (-ancho, 0.27)):
                x = dx * math.cos(a) + dy * math.sin(a)
                y = dx * math.sin(a) - dy * math.cos(a)
                pts.append(p(x, y))
            d.polygon(pts, fill=tinta)
        circulo_en(0, 0, 0.21, fill=tinta)
        circulo_en(0, 0, 0.165, fill=fondo)
        circulo_en(0, 0, 0.085, outline=tinta, width=w)

    elif tipo == "reporte":
        # Hoja con renglones
        d.rounded_rectangle(caja(-0.17, -0.23, 0.17, 0.23), radius=int(S * 0.05 * k), outline=tinta, width=w)
        for y, largo in ((-0.10, 0.20), (0.0, 0.20), (0.10, 0.12)):
            linea((-0.09, y), (-0.09 + largo, y))

    elif tipo == "editor":
        # Lápiz en diagonal (abajo-izquierda a arriba-derecha)
        a = -math.pi / 4

        def rot(x, y):
            return p(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
        cuerpo = [rot(-x, y) for x, y in [(-0.14, -0.075), (0.27, -0.075), (0.27, 0.075), (-0.14, 0.075)]]
        punta = [rot(-x, y) for x, y in [(-0.14, -0.075), (-0.27, 0.0), (-0.14, 0.075)]]
        d.polygon(cuerpo, outline=tinta, width=w)
        d.line(punta + [punta[0]], fill=tinta, width=w, joint="curve")
        d.line((*rot(-0.17, -0.075), *rot(-0.17, 0.075)), fill=tinta, width=w)

    elif tipo == "dashboard":
        # Tres barras ascendentes
        for x, alto in ((-0.15, 0.14), (0.0, 0.26), (0.15, 0.38)):
            d.rounded_rectangle(caja(x - 0.045, 0.20 - alto, x + 0.045, 0.20),
                                radius=int(S * 0.025 * k), outline=tinta, width=w)

    elif tipo == "cerrar":
        # Botón de encendido
        r = 0.20
        d.arc(caja(-r, -r, r, r), start=300, end=240, fill=tinta, width=w)
        linea((0, -0.25), (0, -0.02))

    elif tipo == "reglas":
        # Controles deslizantes (parámetros ajustables)
        for y, x in ((-0.14, 0.09), (0.0, -0.08), (0.14, 0.03)):
            linea((-0.22, y), (0.22, y))
            circulo_en(x, y, 0.055, fill=tinta)

    elif tipo == "mas":
        linea((-0.2, 0), (0.2, 0))
        linea((0, -0.2), (0, 0.2))

    elif tipo == "x":
        linea((-0.16, -0.16), (0.16, 0.16))
        linea((-0.16, 0.16), (0.16, -0.16))

    elif tipo == "check":
        linea((-0.19, 0.01), (-0.06, 0.14), (0.2, -0.14))

    elif tipo == "basura":
        linea((-0.21, -0.14), (0.21, -0.14))
        d.rectangle(caja(-0.07, -0.22, 0.07, -0.14), outline=tinta, width=w)
        d.polygon([p(-0.15, -0.14), p(0.15, -0.14), p(0.12, 0.23), p(-0.12, 0.23)], outline=tinta, width=w)
        linea((-0.045, -0.06), (-0.045, 0.15))
        linea((0.045, -0.06), (0.045, 0.15))

    elif tipo in ("subir", "descargar"):
        if tipo == "subir":
            linea((0, 0.08), (0, -0.22))
            linea((-0.11, -0.11), (0, -0.22), (0.11, -0.11))
        else:
            linea((0, -0.22), (0, 0.08))
            linea((-0.11, -0.03), (0, 0.08), (0.11, -0.03))
        linea((-0.21, 0.04), (-0.21, 0.2), (0.21, 0.2), (0.21, 0.04))

    elif tipo == "lupa":
        circulo_en(-0.04, -0.04, 0.15, outline=tinta, width=w)
        linea((0.07, 0.07), (0.22, 0.22))

    elif tipo == "carpeta":
        d.polygon([p(-0.23, -0.16), p(-0.07, -0.16), p(-0.02, -0.10), p(0.23, -0.10),
                   p(0.23, 0.18), p(-0.23, 0.18)], outline=tinta, width=w)

    elif tipo == "base":
        # Base de datos: cilindro
        d.ellipse(caja(-0.19, -0.23, 0.19, -0.11), outline=tinta, width=w)
        linea((-0.19, -0.17), (-0.19, 0.17))
        linea((0.19, -0.17), (0.19, 0.17))
        d.arc(caja(-0.19, -0.06, 0.19, 0.06), start=0, end=180, fill=tinta, width=w)
        d.arc(caja(-0.19, 0.11, 0.19, 0.23), start=0, end=180, fill=tinta, width=w)

    elif tipo == "guardar":
        d.rounded_rectangle(caja(-0.2, -0.2, 0.2, 0.2), radius=int(S * 0.03 * k), outline=tinta, width=w)
        d.rectangle(caja(-0.1, -0.2, 0.08, -0.07), outline=tinta, width=w)
        d.rectangle(caja(-0.12, 0.05, 0.12, 0.2), outline=tinta, width=w)

    img = img.resize((tam, tam), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(tam, tam))


#  BOTONES
_VARIANTES = {
    "primario": (COLOR_AMARILLO, COLOR_AMARILLO_HOVER, COLOR_TEXTO),
    "oscuro": (COLOR_OSCURO, COLOR_OSCURO_HOVER, "#FFFFFF"),
    "peligro": (COLOR_ROJO, COLOR_ROJO_HOVER, "#FFFFFF"),
    "secundario": (COLOR_GRIS, COLOR_GRIS_HOVER, COLOR_TEXTO),
}


def estilo_boton(boton, variante, icono=None):
    """Aplica (o cambia) la variante de color de un CTkButton."""
    fg, hover, texto = _VARIANTES[variante]
    opciones = dict(fg_color=fg, hover_color=hover, text_color=texto)
    if icono:
        opciones["image"] = crear_icono(icono, tam=16, circulo=False, color=texto)
    boton.configure(**opciones)


def boton(parent, texto, comando, variante="primario", icono=None, **kw):
    opciones = dict(height=36, corner_radius=8, font=fuente(12, "bold"), compound="left")
    opciones.update(kw)
    b = ctk.CTkButton(parent, text=texto, command=comando, **opciones)
    estilo_boton(b, variante, icono)
    return b


#  CONTENEDORES
def card(parent, **kw):
    opciones = dict(fg_color=COLOR_CARD, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    opciones.update(kw)
    return ctk.CTkFrame(parent, **opciones)


def encabezado(parent, icono, titulo, subtitulo=None, tam_icono=52):
    """Encabezado con icono en círculo, título y subtítulo. Devuelve (frame, label_subtitulo)."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(frame, text="", image=crear_icono(icono, tam=tam_icono)).pack(side="left", padx=(0, 14))
    textos = ctk.CTkFrame(frame, fg_color="transparent")
    textos.pack(side="left", fill="x", expand=True)
    ctk.CTkLabel(textos, text=titulo, font=fuente(20, "bold"), text_color=COLOR_TEXTO,
                 anchor="w").pack(anchor="w")
    lbl_sub = None
    if subtitulo is not None:
        lbl_sub = ctk.CTkLabel(textos, text=subtitulo, font=fuente(12), text_color=COLOR_TEXTO_SEC, anchor="w")
        lbl_sub.pack(anchor="w")
    return frame, lbl_sub


#  VENTANAS
def centrar(win, ancho, alto):
    """Centra la ventana; CTk escala el tamaño pero no la posición."""
    win.update_idletasks()
    try:
        escala = win._get_window_scaling()
    except Exception:
        escala = 1
    x = int((win.winfo_screenwidth() - ancho * escala) / 2)
    y = int((win.winfo_screenheight() - alto * escala) / 2)
    win.geometry(f"{ancho}x{alto}+{max(x, 0)}+{max(y, 0)}")


def _poner_icono(win):
    try:
        if win.winfo_exists() and os.path.exists(ICONO_APP):
            win.iconbitmap(ICONO_APP)
    except Exception:
        pass


def nueva_ventana(parent, titulo, ancho, alto, modal=True, redimensionable=False):
    """Crea una CTkToplevel centrada, al frente y (opcionalmente) modal."""
    win = ctk.CTkToplevel(parent)
    win.title(titulo)
    win.configure(fg_color=COLOR_FONDO)
    win.resizable(redimensionable, redimensionable)
    centrar(win, ancho, alto)
    # transient sobre una ventana oculta (withdraw) también oculta la nueva en Windows
    if parent is not None and parent.winfo_toplevel().state() != "withdrawn":
        win.transient(parent.winfo_toplevel())
    # CTkToplevel reemplaza el icono a los ~200 ms; se vuelve a poner después
    win.after(250, lambda: _poner_icono(win))
    win.lift()
    win.focus_force()
    if modal:
        # grab_set falla si la ventana aún no es visible
        win.after(150, lambda: win.grab_set() if win.winfo_exists() else None)
    return win


#  TABLAS (ttk.Treeview con estilo plano)
def estilo_tabla(widget):
    """Configura el estilo 'Tabla.Treeview' y devuelve su nombre."""
    try:
        escala = ctk.ScalingTracker.get_widget_scaling(widget)
    except Exception:
        escala = 1
    style = ttk.Style(widget)
    style.theme_use("clam")
    style.configure("Tabla.Treeview", font=(FUENTE, 10), rowheight=int(28 * escala),
                    background=COLOR_CARD, fieldbackground=COLOR_CARD, foreground=COLOR_TEXTO,
                    borderwidth=0, relief="flat")
    style.configure("Tabla.Treeview.Heading", font=(FUENTE, 10, "bold"), background=COLOR_AMARILLO,
                    foreground=COLOR_TEXTO, relief="flat", borderwidth=0, padding=(8, 7))
    style.map("Tabla.Treeview.Heading", background=[("active", COLOR_AMARILLO_HOVER)])
    style.map("Tabla.Treeview", background=[("selected", COLOR_ICONO_FONDO)],
              foreground=[("selected", COLOR_TEXTO)])
    style.layout("Tabla.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    return "Tabla.Treeview"


def tabla(parent, columnas, horizontal=True, **kw):
    """Crea una Treeview con scrollbars de CTk. Devuelve (frame_contenedor, tree)."""
    cont = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=0)
    tree = ttk.Treeview(cont, columns=columnas, show="headings", style=estilo_tabla(parent), **kw)
    sv = ctk.CTkScrollbar(cont, orientation="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sv.set)
    tree.grid(row=0, column=0, sticky="nsew")
    sv.grid(row=0, column=1, sticky="ns")
    if horizontal:
        sh = ctk.CTkScrollbar(cont, orientation="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=sh.set)
        sh.grid(row=1, column=0, sticky="ew")
    cont.grid_rowconfigure(0, weight=1)
    cont.grid_columnconfigure(0, weight=1)
    tree.tag_configure("alterna", background=COLOR_FILA_ALTERNA)
    return cont, tree


def tag_fila(indice):
    return ("alterna",) if indice % 2 else ()
