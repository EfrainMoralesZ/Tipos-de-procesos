"""Reglas de clasificación del TIPO DE PROCESO (ADHERIBLE / COSTURA) y su editor.

Las reglas se guardan en datos/reglas.json; ProcesosV4 las lee cada vez que procesa un reporte,
así que los cambios aplican sin reiniciar ni tocar código.
"""
import copy
import json
import os

import customtkinter as ctk
from tkinter import messagebox

import Estilos as E
import Rutas

ARCHIVO_REGLAS = Rutas.archivo_datos("reglas.json")
RESULTADOS = ("ADHERIBLE", "COSTURA")

# Artículos que con NOM-004 / NOM-020 se etiquetan con adherible en lugar de costura
_PALABRAS_EXCEPCION = [
    'CALCETIN', 'CALCETINES', 'MEDIA', 'MEDIAS', 'SOCKS', 'ROPA INTERIOR',
    'PANTIMEDIAS', 'BANDA PARA LA CABEZA', 'MUÑEQUERAS', 'CALCETAS', 'CALCETÍN',
    'MOCHILAS', 'BOLSAS', 'BOLSA', 'RIÑONERAS', 'BOLSA DE DEPORTE', 'BOLSA RIÑON',
    'SANDALIAS', 'RIENDA DE EQUITACIÓN', 'RIENDA', 'CINTA PARA CABEZA',
    'CINTURÓN CORREDOR CON FRASCO', 'CAMPANAS ABIERTAS EQUITACIÓN',
    'CUERDA DE POLIAMIDA (KIT VIENTOS Y TENSORES)', 'CUERDAS',
]

# Valores que estaban fijos en ProcesosV4.py; se usan para crear reglas.json si no existe o está dañado
REGLAS_POR_DEFECTO = {
    "normas_adherible": [
        'NOM-050-SCFI-2004', 'NOM-121-SCFI-2004', 'NOM-015-SCFI-2007',
        'NOM-024-SCFI-2013', 'NOM-141-SSA1/SCFI-2012', 'NOM004TEXX', 'NOM020INS',
        'NOM-115-STPS-2009', 'NOM-189-SSA1/SCFI-2018',
    ],
    "normas_costura": ['NOM-004-SE-2021', 'NOM-020-SCFI-1997', 'NOM004', 'NOM020'],
    "normas_validas": [
        '003', 'NOM-004-SE-2021', '008', 'NOM-015-SCFI-2007', '020', 'NOM-020-SCFI-1997',
        'NOM-024-SCFI-2013', '035', 'NOM-050-SCFI-2004', '051', '116', 'NOM-141-SSA1/SCFI-2012',
        '142', '173', '185', '186', 'NOM-189-SSA1/SCFI-2018', '192', '199', '235',
        'NOM-115-STPS-2009', 'NOM-121-SCFI-2004',
    ],
    "excepciones": [
        {"nombre": "Excepción NOM-004", "normas": ['NOM-004-SE-2021', 'NOM004'],
         "palabras": list(_PALABRAS_EXCEPCION), "resultado": "ADHERIBLE"},
        {"nombre": "Excepción NOM-020", "normas": ['NOM-020-SCFI-1997', 'NOM020'],
         "palabras": list(_PALABRAS_EXCEPCION), "resultado": "ADHERIBLE"},
    ],
    # NORMA UVA del pedimento (número) -> norma que se escribe en el TIPO DE PROCESO
    "equivalencias_pedimento": [
        {"numero": "4", "norma": "NOM-004-SE-2021"},
        {"numero": "15", "norma": "NOM-015-SCFI-2007"},
        {"numero": "20", "norma": "NOM-020-SCFI-1997"},
        {"numero": "24", "norma": "NOM-024-SCFI-2013"},
        {"numero": "50", "norma": "NOM-050-SCFI-2004"},
        {"numero": "115", "norma": "NOM-115-STPS-2009"},
        {"numero": "121", "norma": "NOM-121-SCFI-2004"},
        {"numero": "141", "norma": "NOM-141-SSA1/SCFI-2012"},
        {"numero": "189", "norma": "NOM-189-SSA1/SCFI-2018"},
    ],
}


#  LECTURA / ESCRITURA
def _normalizar(valores):
    """Mayúsculas, sin espacios sobrantes, sin vacíos ni duplicados (conserva el orden)."""
    vistos = []
    for v in valores or []:
        v = str(v).strip().upper()
        if v and v not in vistos:
            vistos.append(v)
    return vistos


def _normalizar_reglas(reglas):
    limpias = {clave: _normalizar(reglas.get(clave, REGLAS_POR_DEFECTO[clave]))
               for clave in ("normas_adherible", "normas_costura", "normas_validas")}
    limpias["excepciones"] = [
        {"nombre": str(exc.get("nombre", "")).strip() or "Sin nombre",
         "normas": _normalizar(exc.get("normas")),
         "palabras": _normalizar(exc.get("palabras")),
         "resultado": exc.get("resultado") if exc.get("resultado") in RESULTADOS else "ADHERIBLE"}
        for exc in reglas.get("excepciones", REGLAS_POR_DEFECTO["excepciones"])
    ]
    equivalencias, numeros = [], set()
    for eq in reglas.get("equivalencias_pedimento", REGLAS_POR_DEFECTO["equivalencias_pedimento"]):
        numero = numero_norma(eq.get("numero"))
        norma = str(eq.get("norma", "")).strip().upper()
        if numero and norma and numero not in numeros:
            numeros.add(numero)
            equivalencias.append({"numero": numero, "norma": norma})
    limpias["equivalencias_pedimento"] = sorted(equivalencias, key=lambda eq: int(eq["numero"]))
    return limpias


def cargar_reglas():
    """Lee reglas.json; si no existe lo crea con los valores por defecto."""
    if not os.path.exists(ARCHIVO_REGLAS) or os.path.getsize(ARCHIVO_REGLAS) == 0:
        guardar_reglas(REGLAS_POR_DEFECTO)
        return _normalizar_reglas(copy.deepcopy(REGLAS_POR_DEFECTO))
    try:
        with open(ARCHIVO_REGLAS, "r", encoding="utf-8") as f:
            return _normalizar_reglas(json.load(f))
    except (json.JSONDecodeError, AttributeError) as e:
        raise ValueError(f"El archivo de reglas está dañado:\n{ARCHIVO_REGLAS}\n\n{e}")


def guardar_reglas(reglas):
    with open(ARCHIVO_REGLAS, "w", encoding="utf-8") as f:
        json.dump(_normalizar_reglas(reglas), f, indent=4, ensure_ascii=False)


#  CLASIFICACIÓN
def clasificar(norma, descripcion, tipo, reglas):
    """Devuelve (tipo_de_proceso, motivo). Orden: excepciones, adheribles, costura, tipo actual."""
    norma = str(norma).upper().strip()
    descripcion = str(descripcion).upper().strip()
    tipo = str(tipo).upper().strip()

    for exc in reglas["excepciones"]:
        if norma in exc["normas"]:
            for palabra in exc["palabras"]:
                if palabra in descripcion:
                    return exc["resultado"], f'{exc["nombre"]}: la descripción contiene "{palabra}"'
    if norma in reglas["normas_adherible"]:
        return "ADHERIBLE", "La norma está en Normas adheribles"
    if norma in reglas["normas_costura"]:
        return "COSTURA", "La norma está en Normas de costura"
    if tipo:
        return tipo, "Ninguna regla aplica; se conserva el CODIGO FORMATO de la base general"
    return "SIN NORMA", "Ninguna regla aplica y no hay CODIGO FORMATO"


def es_norma_valida(norma, reglas):
    return str(norma).upper().strip() in reglas["normas_validas"]


#  PEDIMENTO
def numero_norma(valor):
    """'4', 4.0, '004' -> '4'. Devuelve None si el valor no es un número entero."""
    texto = str(valor).strip()
    try:
        numero = float(texto)
    except ValueError:
        return None
    if numero != numero or numero != int(numero):  # NaN o con decimales
        return None
    return str(int(numero))


def norma_pedimento(valor, reglas):
    """Convierte la NORMA UVA del pedimento a la norma completa.

    Devuelve (norma, conocida): conocida=False si el número no está en las equivalencias
    (entonces se usa el número a 3 dígitos, p. ej. '003'). Devuelve (None, True) si viene vacía."""
    if valor is None or str(valor).strip().upper() in ("", "NAN", "NONE"):
        return None, True
    numero = numero_norma(valor)
    if numero is None:  # ya viene escrita como norma (ej. NOM-004-SE-2021)
        return str(valor).strip().upper(), True
    for eq in reglas["equivalencias_pedimento"]:
        if eq["numero"] == numero:
            return eq["norma"], True
    return numero.zfill(3), False


#  INTERFAZ
class ListaEditable(ctk.CTkFrame):
    """Card con una lista de textos: agregar (Enter), editar (doble clic) y eliminar (Supr).
    Modifica en sitio la lista que recibe, así el diccionario de reglas queda actualizado."""

    def __init__(self, parent, ventana, titulo, descripcion, columna, al_cambiar):
        super().__init__(parent, fg_color=E.COLOR_CARD, corner_radius=14,
                         border_width=1, border_color=E.COLOR_BORDE)
        self.ventana = ventana
        self.al_cambiar = al_cambiar
        self.valores = []
        self.editando = None  # índice del valor que se está editando

        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(cabecera, text=titulo, font=E.fuente(14, "bold"),
                     text_color=E.COLOR_TEXTO, anchor="w").pack(side="left")
        self.lbl_conteo = ctk.CTkLabel(cabecera, text="0", font=E.fuente(11, "bold"), width=34, height=22,
                                       corner_radius=11, fg_color=E.COLOR_ICONO_FONDO, text_color=E.COLOR_TEXTO)
        self.lbl_conteo.pack(side="right")
        ctk.CTkLabel(self, text=descripcion, font=E.fuente(11), text_color=E.COLOR_TEXTO_SEC,
                     anchor="w", justify="left", wraplength=250).pack(fill="x", padx=16, pady=(2, 10))

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=16)
        self.entry = ctk.CTkEntry(fila, height=34, corner_radius=8, border_color=E.COLOR_BORDE_FUERTE,
                                  fg_color=E.COLOR_CARD, text_color=E.COLOR_TEXTO, font=E.fuente(12),
                                  placeholder_text="Escribe y presiona Enter")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.btn = E.boton(fila, "Agregar", self._confirmar, "primario", icono="mas", width=96, height=34)
        self.btn.pack(side="left")

        cont, self.tree = E.tabla(self, (columna,), horizontal=False, selectmode="extended")
        self.tree.heading(columna, text=columna, anchor="w")
        self.tree.column(columna, anchor="w", stretch=True, width=200)
        # El pie se empaca antes que la tabla para que no desaparezca si la ventana es baja
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=16, pady=(0, 14))
        cont.pack(fill="both", expand=True, padx=16, pady=10)
        ctk.CTkLabel(pie, text="Doble clic para editar", font=E.fuente(11),
                     text_color=E.COLOR_TEXTO_TENUE).pack(side="left")
        E.boton(pie, "Eliminar", self._eliminar, "peligro", icono="basura",
                width=96, height=30).pack(side="right")

        self.entry.bind("<Return>", self._confirmar)
        self.entry.bind("<Escape>", lambda e: self._cancelar_edicion())
        self.tree.bind("<Double-1>", self._editar)
        self.tree.bind("<Delete>", lambda e: self._eliminar())

    def set_lista(self, lista):
        self.valores = lista
        self._cancelar_edicion()
        self._refrescar()

    def _refrescar(self, seleccionar=None):
        self.tree.delete(*self.tree.get_children())
        for i, v in enumerate(self.valores):
            self.tree.insert("", "end", iid=str(i), values=(v,), tags=E.tag_fila(i))
        if seleccionar is not None:
            self.tree.selection_set(str(seleccionar))
            self.tree.see(str(seleccionar))
        self.lbl_conteo.configure(text=str(len(self.valores)))

    def _confirmar(self, _e=None):
        valor = self.entry.get().strip().upper()
        if not valor:
            return
        otros = [v for i, v in enumerate(self.valores) if i != self.editando]
        if valor in otros:
            messagebox.showinfo("Valor repetido", f'"{valor}" ya está en la lista.', parent=self.ventana)
            return
        if self.editando is None:
            self.valores.append(valor)
            indice = len(self.valores) - 1
        else:
            indice = self.editando
            self.valores[indice] = valor
        self._cancelar_edicion()
        self._refrescar(indice)
        self.al_cambiar()

    def _editar(self, _e=None):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        self.editando = int(seleccion[0])
        self.entry.delete(0, "end")
        self.entry.insert(0, self.valores[self.editando])
        self.entry.focus_set()
        self.btn.configure(text="Guardar")
        E.estilo_boton(self.btn, "oscuro", icono="check")

    def _cancelar_edicion(self):
        if self.editando is not None:
            self.entry.delete(0, "end")
        self.editando = None
        self.btn.configure(text="Agregar")
        E.estilo_boton(self.btn, "primario", icono="mas")

    def _eliminar(self):
        indices = sorted((int(i) for i in self.tree.selection()), reverse=True)
        if not indices:
            messagebox.showinfo("Eliminar", "Selecciona uno o más valores de la lista.", parent=self.ventana)
            return
        for i in indices:
            del self.valores[i]
        self._cancelar_edicion()
        self._refrescar()
        self.al_cambiar()


class TablaEquivalencias(ctk.CTkFrame):
    """Card con las equivalencias número de pedimento -> norma. Modifica en sitio la lista recibida."""

    def __init__(self, parent, ventana, al_cambiar):
        super().__init__(parent, fg_color=E.COLOR_CARD, corner_radius=14,
                         border_width=1, border_color=E.COLOR_BORDE)
        self.ventana = ventana
        self.al_cambiar = al_cambiar
        self.valores = []
        self.editando = None

        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(cabecera, text="Equivalencias de NORMA UVA", font=E.fuente(14, "bold"),
                     text_color=E.COLOR_TEXTO, anchor="w").pack(side="left")
        self.lbl_conteo = ctk.CTkLabel(cabecera, text="0", font=E.fuente(11, "bold"), width=34, height=22,
                                       corner_radius=11, fg_color=E.COLOR_ICONO_FONDO, text_color=E.COLOR_TEXTO)
        self.lbl_conteo.pack(side="right")
        ctk.CTkLabel(self, text="El pedimento trae la norma como número (4, 15, 20…). Al generar el tipo de "
                                "proceso se escribe la norma completa de esta tabla. Si un número no está aquí, "
                                "se usa a 3 dígitos (ej. 3 → 003) y se avisa al terminar.",
                     font=E.fuente(11), text_color=E.COLOR_TEXTO_SEC, anchor="w", justify="left",
                     wraplength=900).pack(fill="x", padx=16, pady=(2, 10))

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", padx=16)
        estilo_entry = dict(height=34, corner_radius=8, border_color=E.COLOR_BORDE_FUERTE,
                            fg_color=E.COLOR_CARD, text_color=E.COLOR_TEXTO, font=E.fuente(12))
        self.entry_num = ctk.CTkEntry(fila, width=110, placeholder_text="Número", **estilo_entry)
        self.entry_num.pack(side="left", padx=(0, 8))
        self.entry_norma = ctk.CTkEntry(fila, placeholder_text="Norma, ej. NOM-004-SE-2021", **estilo_entry)
        self.entry_norma.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.btn = E.boton(fila, "Agregar", self._confirmar, "primario", icono="mas", width=110, height=34)
        self.btn.pack(side="left")

        cont, self.tree = E.tabla(self, ("NUMERO", "NORMA"), horizontal=False, selectmode="extended")
        self.tree.heading("NUMERO", text="NORMA UVA (PEDIMENTO)", anchor="w")
        self.tree.heading("NORMA", text="NORMA EN EL TIPO DE PROCESO", anchor="w")
        self.tree.column("NUMERO", width=200, anchor="w", stretch=False)
        self.tree.column("NORMA", width=300, anchor="w")
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=16, pady=(0, 14))
        cont.pack(fill="both", expand=True, padx=16, pady=10)
        ctk.CTkLabel(pie, text="Doble clic para editar", font=E.fuente(11),
                     text_color=E.COLOR_TEXTO_TENUE).pack(side="left")
        E.boton(pie, "Eliminar", self._eliminar, "peligro", icono="basura",
                width=96, height=30).pack(side="right")

        for entry in (self.entry_num, self.entry_norma):
            entry.bind("<Return>", self._confirmar)
            entry.bind("<Escape>", lambda e: self._cancelar_edicion())
        self.tree.bind("<Double-1>", self._editar)
        self.tree.bind("<Delete>", lambda e: self._eliminar())

    def set_lista(self, lista):
        self.valores = lista
        self._cancelar_edicion()
        self._refrescar()

    def _refrescar(self, seleccionar=None):
        self.valores.sort(key=lambda eq: int(eq["numero"]))
        self.tree.delete(*self.tree.get_children())
        for i, eq in enumerate(self.valores):
            self.tree.insert("", "end", iid=str(i), values=(eq["numero"], eq["norma"]), tags=E.tag_fila(i))
        if seleccionar is not None:
            i = next((i for i, eq in enumerate(self.valores) if eq["numero"] == seleccionar), None)
            if i is not None:
                self.tree.selection_set(str(i))
                self.tree.see(str(i))
        self.lbl_conteo.configure(text=str(len(self.valores)))

    def _confirmar(self, _e=None):
        numero = numero_norma(self.entry_num.get())
        norma = self.entry_norma.get().strip().upper()
        if numero is None:
            messagebox.showinfo("Número inválido", "Escribe el número de la norma tal como viene en el "
                                                    "pedimento (ej. 4, 15, 20).", parent=self.ventana)
            return
        if not norma:
            messagebox.showinfo("Falta la norma", "Escribe la norma completa (ej. NOM-004-SE-2021).",
                                parent=self.ventana)
            return
        repetido = [eq for i, eq in enumerate(self.valores) if i != self.editando and eq["numero"] == numero]
        if repetido:
            messagebox.showinfo("Número repetido", f'El {numero} ya equivale a {repetido[0]["norma"]}.',
                                parent=self.ventana)
            return
        if self.editando is None:
            self.valores.append({"numero": numero, "norma": norma})
        else:
            self.valores[self.editando] = {"numero": numero, "norma": norma}
        self._cancelar_edicion()
        self._refrescar(numero)
        self.al_cambiar()

    def _editar(self, _e=None):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        self._cancelar_edicion()
        self.editando = int(seleccion[0])
        eq = self.valores[self.editando]
        self.entry_num.insert(0, eq["numero"])
        self.entry_norma.insert(0, eq["norma"])
        self.entry_norma.focus_set()
        self.btn.configure(text="Guardar")
        E.estilo_boton(self.btn, "oscuro", icono="check")

    def _cancelar_edicion(self):
        if self.editando is not None:
            self.entry_num.delete(0, "end")
            self.entry_norma.delete(0, "end")
        self.editando = None
        self.btn.configure(text="Agregar")
        E.estilo_boton(self.btn, "primario", icono="mas")

    def _eliminar(self):
        indices = sorted((int(i) for i in self.tree.selection()), reverse=True)
        if not indices:
            messagebox.showinfo("Eliminar", "Selecciona una o más equivalencias.", parent=self.ventana)
            return
        for i in indices:
            del self.valores[i]
        self._cancelar_edicion()
        self._refrescar()
        self.al_cambiar()


def _estilo_segmentado():
    return dict(fg_color=E.COLOR_GRIS, selected_color=E.COLOR_AMARILLO,
                selected_hover_color=E.COLOR_AMARILLO_HOVER, unselected_color=E.COLOR_GRIS,
                unselected_hover_color=E.COLOR_GRIS_HOVER, text_color=E.COLOR_TEXTO,
                font=E.fuente(12, "bold"))


class EditorReglas:
    def __init__(self, parent=None):
        self.parent = parent
        try:
            self.reglas = cargar_reglas()
        except ValueError as e:
            if not messagebox.askyesno("Reglas dañadas", f"{e}\n\n¿Restaurar los valores de fábrica?"):
                return
            self.reglas = _normalizar_reglas(copy.deepcopy(REGLAS_POR_DEFECTO))
        self.modificado = False
        self.exc_actual = None
        self._cargando = False
        self.crear_ventana()

    #  VENTANA
    def crear_ventana(self):
        # Altura ajustada a la pantalla (descontando la barra de tareas) según el escalado de Windows
        try:
            escala = ctk.ScalingTracker.get_window_scaling(self.parent) if self.parent else 1
        except Exception:
            escala = 1
        alto = int(min(700, self.parent.winfo_screenheight() / escala - 90)) if self.parent else 700
        self.ventana = v = E.nueva_ventana(self.parent, "Reglas de clasificación", 1060, alto,
                                           modal=True, redimensionable=True)
        v.minsize(940, min(560, alto))
        v.protocol("WM_DELETE_WINDOW", self.cerrar)

        cab, _ = E.encabezado(v, "reglas", "Reglas de clasificación",
                              "Define qué normas son adheribles o de costura y qué artículos se exceptúan. "
                              "Los cambios aplican desde el siguiente reporte.")
        cab.pack(fill="x", padx=24, pady=(20, 6))

        pie = ctk.CTkFrame(v, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=24, pady=(6, 18))
        self.lbl_estado = ctk.CTkLabel(pie, text="", font=E.fuente(12, "bold"), text_color=E.COLOR_TEXTO_SEC)
        self.lbl_estado.pack(side="left", padx=(4, 14))
        E.boton(pie, "Guardar cambios", self.guardar, "primario", icono="guardar", width=160).pack(side="right")
        E.boton(pie, "Cerrar", self.cerrar, "secundario", width=100).pack(side="right", padx=(0, 10))

        tabs = ctk.CTkTabview(v, fg_color=E.COLOR_FONDO, corner_radius=0, anchor="nw",
                              segmented_button_fg_color=E.COLOR_GRIS,
                              segmented_button_selected_color=E.COLOR_AMARILLO,
                              segmented_button_selected_hover_color=E.COLOR_AMARILLO_HOVER,
                              segmented_button_unselected_color=E.COLOR_GRIS,
                              segmented_button_unselected_hover_color=E.COLOR_GRIS_HOVER,
                              text_color=E.COLOR_TEXTO)
        tabs._segmented_button.configure(font=E.fuente(12, "bold"), height=32)
        tabs.pack(fill="both", expand=True, padx=18)
        self._tab_normas(tabs.add("  Normas por tipo  "))
        self._tab_excepciones(tabs.add("  Excepciones por descripción  "))
        self.tabla_equivalencias = TablaEquivalencias(tabs.add("  Pedimento  "), self.ventana, self.marcar_cambio)
        self.tabla_equivalencias.pack(fill="both", expand=True, padx=6, pady=(4, 0))
        self._tab_probar(tabs.add("  Probar  "))

        self.cargar_en_pantalla()

    def _tab_normas(self, tab):
        for col in range(3):
            tab.grid_columnconfigure(col, weight=1, uniform="normas")
        tab.grid_rowconfigure(0, weight=1)
        textos = [
            ("normas_adherible", "Normas adheribles", "Se etiquetan con ADHERIBLE.", "NORMA"),
            ("normas_costura", "Normas de costura", "Se etiquetan con COSTURA, salvo que aplique una excepción.", "NORMA"),
            ("normas_validas", "Normas válidas", "Cualquier norma fuera de esta lista queda como SIN NORMA.", "NORMA"),
        ]
        self.listas_normas = {}
        for col, (clave, titulo, desc, columna) in enumerate(textos):
            lista = ListaEditable(tab, self.ventana, titulo, desc, columna, self.marcar_cambio)
            lista.grid(row=0, column=col, sticky="nsew", padx=6, pady=(4, 0))
            self.listas_normas[clave] = lista

    def _tab_excepciones(self, tab):
        tab.grid_columnconfigure(0, weight=0, minsize=290)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Lista de excepciones
        izq = E.card(tab, width=290)
        izq.grid(row=0, column=0, sticky="nsew", padx=(6, 6), pady=(4, 0))
        ctk.CTkLabel(izq, text="Excepciones", font=E.fuente(14, "bold"), text_color=E.COLOR_TEXTO,
                     anchor="w").pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(izq, text="Si la norma coincide y la descripción contiene una de las palabras, "
                               "se usa el resultado de la excepción.",
                     font=E.fuente(11), text_color=E.COLOR_TEXTO_SEC, anchor="w", justify="left",
                     wraplength=235).pack(fill="x", padx=16, pady=(2, 10))
        cont, self.tree_exc = E.tabla(izq, ("NOMBRE", "RESULTADO"), horizontal=False, selectmode="browse")
        self.tree_exc.heading("NOMBRE", text="NOMBRE", anchor="w")
        self.tree_exc.heading("RESULTADO", text="RESULTADO", anchor="w")
        self.tree_exc.column("NOMBRE", width=130, anchor="w")
        self.tree_exc.column("RESULTADO", width=105, anchor="w", stretch=False)
        self.tree_exc.bind("<<TreeviewSelect>>", self._seleccionar_excepcion)
        botones = ctk.CTkFrame(izq, fg_color="transparent")
        botones.pack(side="bottom", fill="x", padx=16, pady=(10, 14))
        cont.pack(fill="both", expand=True, padx=16)
        E.boton(botones, "Nueva", self.nueva_excepcion, "primario", icono="mas",
                height=32).pack(side="left", fill="x", expand=True, padx=(0, 4))
        E.boton(botones, "Eliminar", self.eliminar_excepcion, "peligro", icono="basura",
                height=32).pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Detalle de la excepción seleccionada
        self.der = der = ctk.CTkFrame(tab, fg_color="transparent")
        der.grid(row=0, column=1, sticky="nsew", pady=(4, 0))
        self.lbl_sin_exc = ctk.CTkLabel(tab, text="No hay excepciones. Agrega una con “Nueva”.",
                                        font=E.fuente(13), text_color=E.COLOR_TEXTO_TENUE)

        datos = E.card(der)
        datos.pack(fill="x", padx=6)
        datos.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(datos, text="Nombre", font=E.fuente(12, "bold"), text_color=E.COLOR_TEXTO,
                     anchor="w").grid(row=0, column=0, sticky="w", padx=16, pady=(12, 2))
        ctk.CTkLabel(datos, text="Resultado cuando aplica", font=E.fuente(12, "bold"), text_color=E.COLOR_TEXTO,
                     anchor="w").grid(row=0, column=1, sticky="w", padx=16, pady=(12, 2))
        self.var_nombre = ctk.StringVar()
        ctk.CTkEntry(datos, textvariable=self.var_nombre, height=34, corner_radius=8,
                     border_color=E.COLOR_BORDE_FUERTE, fg_color=E.COLOR_CARD, text_color=E.COLOR_TEXTO,
                     font=E.fuente(12)).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))
        self.var_nombre.trace_add("write", self._cambio_nombre)
        self.seg_resultado = ctk.CTkSegmentedButton(datos, values=list(RESULTADOS), height=34,
                                                    command=self._cambio_resultado, **_estilo_segmentado())
        self.seg_resultado.grid(row=1, column=1, sticky="w", padx=16, pady=(0, 14))

        listas = ctk.CTkFrame(der, fg_color="transparent")
        listas.pack(fill="both", expand=True, pady=(10, 0))
        listas.grid_columnconfigure((0, 1), weight=1, uniform="exc")
        listas.grid_rowconfigure(0, weight=1)
        self.lista_exc_normas = ListaEditable(listas, self.ventana, "Normas a las que aplica",
                                              "La excepción solo se revisa para estas normas.", "NORMA",
                                              self.marcar_cambio)
        self.lista_exc_normas.grid(row=0, column=0, sticky="nsew", padx=6)
        self.lista_exc_palabras = ListaEditable(listas, self.ventana, "Palabras en la descripción",
                                                "Basta con que la descripción contenga una (ej. CALCETA, MOCHILA).",
                                                "PALABRA", self.marcar_cambio)
        self.lista_exc_palabras.grid(row=0, column=1, sticky="nsew", padx=6)

    def _tab_probar(self, tab):
        c = E.card(tab)
        c.pack(fill="x", padx=6, pady=(4, 0))
        c.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(c, text="Prueba cómo se clasificaría un artículo con las reglas actuales (aunque no estén guardadas).",
                     font=E.fuente(12), text_color=E.COLOR_TEXTO_SEC, anchor="w"
                     ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(14, 10))

        self.prueba = {}
        campos = [("norma", "Norma", "NOM-004-SE-2021"), ("descripcion", "Descripción", "CALCETAS DEPORTIVAS"),
                  ("tipo", "CODIGO FORMATO (opcional)", "")]
        for col, (clave, etiqueta, placeholder) in enumerate(campos):
            ctk.CTkLabel(c, text=etiqueta, font=E.fuente(12, "bold"), text_color=E.COLOR_TEXTO,
                         anchor="w").grid(row=1, column=col, sticky="w", padx=16)
            entry = ctk.CTkEntry(c, height=34, corner_radius=8, border_color=E.COLOR_BORDE_FUERTE,
                                 fg_color=E.COLOR_CARD, text_color=E.COLOR_TEXTO, font=E.fuente(12),
                                 placeholder_text=placeholder)
            entry.grid(row=2, column=col, sticky="ew", padx=16, pady=(2, 0))
            entry.bind("<Return>", lambda e: self.probar())
            self.prueba[clave] = entry
        E.boton(c, "Probar", self.probar, "oscuro", icono="lupa", width=120
                ).grid(row=3, column=0, sticky="w", padx=16, pady=14)

        res = E.card(tab)
        res.pack(fill="x", padx=6, pady=(12, 0))
        ctk.CTkLabel(res, text="Resultado", font=E.fuente(12, "bold"), text_color=E.COLOR_TEXTO_SEC,
                     anchor="w").pack(fill="x", padx=16, pady=(14, 0))
        self.lbl_prueba = ctk.CTkLabel(res, text="—", font=E.fuente(24, "bold"), text_color=E.COLOR_TEXTO, anchor="w")
        self.lbl_prueba.pack(fill="x", padx=16)
        self.lbl_motivo = ctk.CTkLabel(res, text="Escribe una norma y una descripción.", font=E.fuente(12),
                                       text_color=E.COLOR_TEXTO_SEC, anchor="w", justify="left", wraplength=900)
        self.lbl_motivo.pack(fill="x", padx=16, pady=(0, 14))
        ctk.CTkLabel(tab, text="Nota: si el artículo está como CUMPLE en los códigos de cumplimiento, "
                               "en el reporte final se muestra CUMPLE.",
                     font=E.fuente(11), text_color=E.COLOR_TEXTO_TENUE, anchor="w").pack(fill="x", padx=10, pady=8)

    #  CARGA Y ESTADO
    def cargar_en_pantalla(self, seleccionar=0):
        for clave, lista in self.listas_normas.items():
            lista.set_lista(self.reglas[clave])
        self.tabla_equivalencias.set_lista(self.reglas["equivalencias_pedimento"])
        self._refrescar_excepciones(seleccionar)

    def _refrescar_excepciones(self, seleccionar=None):
        self.tree_exc.delete(*self.tree_exc.get_children())
        for i, exc in enumerate(self.reglas["excepciones"]):
            self.tree_exc.insert("", "end", iid=str(i), values=(exc["nombre"], exc["resultado"]),
                                 tags=E.tag_fila(i))
        if self.reglas["excepciones"]:
            self.lbl_sin_exc.grid_forget()
            self.der.grid()
            i = min(seleccionar or 0, len(self.reglas["excepciones"]) - 1)
            self.tree_exc.selection_set(str(i))
            self.tree_exc.see(str(i))
            self._mostrar_excepcion(i)
        else:
            self.exc_actual = None
            self.der.grid_remove()
            self.lbl_sin_exc.grid(row=0, column=1)

    def _seleccionar_excepcion(self, _e=None):
        seleccion = self.tree_exc.selection()
        if seleccion:
            self._mostrar_excepcion(int(seleccion[0]))

    def _mostrar_excepcion(self, indice):
        if self.exc_actual == indice:
            return
        self.exc_actual = indice
        exc = self.reglas["excepciones"][indice]
        self._cargando = True
        self.var_nombre.set(exc["nombre"])
        self._cargando = False
        self.seg_resultado.set(exc["resultado"])
        self.lista_exc_normas.set_lista(exc["normas"])
        self.lista_exc_palabras.set_lista(exc["palabras"])

    def _actualizar_fila_excepcion(self):
        exc = self.reglas["excepciones"][self.exc_actual]
        self.tree_exc.item(str(self.exc_actual), values=(exc["nombre"], exc["resultado"]))

    def _cambio_nombre(self, *_):
        if self._cargando or self.exc_actual is None:
            return
        self.reglas["excepciones"][self.exc_actual]["nombre"] = self.var_nombre.get()
        self._actualizar_fila_excepcion()
        self.marcar_cambio()

    def _cambio_resultado(self, valor):
        if self.exc_actual is None:
            return
        self.reglas["excepciones"][self.exc_actual]["resultado"] = valor
        self._actualizar_fila_excepcion()
        self.marcar_cambio()

    def marcar_cambio(self):
        self.modificado = True
        self.lbl_estado.configure(text="● Cambios sin guardar", text_color=E.COLOR_AMARILLO_HOVER)

    #  ACCIONES
    def nueva_excepcion(self):
        n = len(self.reglas["excepciones"]) + 1
        self.reglas["excepciones"].append({"nombre": f"Nueva excepción {n}", "normas": [],
                                           "palabras": [], "resultado": "ADHERIBLE"})
        self.exc_actual = None
        self._refrescar_excepciones(len(self.reglas["excepciones"]) - 1)
        self.marcar_cambio()

    def eliminar_excepcion(self):
        if self.exc_actual is None:
            return
        nombre = self.reglas["excepciones"][self.exc_actual]["nombre"]
        if not messagebox.askyesno("Eliminar excepción", f'¿Eliminar "{nombre}"?', parent=self.ventana):
            return
        indice = self.exc_actual
        del self.reglas["excepciones"][indice]
        self.exc_actual = None
        self._refrescar_excepciones(max(indice - 1, 0))
        self.marcar_cambio()

    def probar(self):
        norma = self.prueba["norma"].get()
        if not norma.strip():
            self.lbl_prueba.configure(text="—", text_color=E.COLOR_TEXTO)
            self.lbl_motivo.configure(text="Escribe la norma a probar.")
            return
        resultado, motivo = clasificar(norma, self.prueba["descripcion"].get(), self.prueba["tipo"].get(), self.reglas)
        if not es_norma_valida(norma, self.reglas):
            motivo = f"La norma no está en Normas válidas (sin esa revisión sería {resultado}: {motivo})"
            resultado = "SIN NORMA"
        color = {"ADHERIBLE": E.COLOR_AZUL, "COSTURA": E.COLOR_VERDE}.get(resultado, E.COLOR_TEXTO_TENUE)
        self.lbl_prueba.configure(text=resultado, text_color=color)
        self.lbl_motivo.configure(text=motivo)

    def guardar(self):
        for exc in self.reglas["excepciones"]:
            if not exc["nombre"].strip():
                messagebox.showwarning("Falta nombre", "Todas las excepciones necesitan nombre.", parent=self.ventana)
                return
        avisos = []
        ambas = sorted(set(self.reglas["normas_adherible"]) & set(self.reglas["normas_costura"]))
        if ambas:
            avisos.append("Estas normas están en adheribles y en costura (gana ADHERIBLE):\n  " + ", ".join(ambas))
        incompletas = [e["nombre"] for e in self.reglas["excepciones"] if not e["normas"] or not e["palabras"]]
        if incompletas:
            avisos.append("Estas excepciones no tienen normas o palabras y no harán nada:\n  " + ", ".join(incompletas))
        no_validas = [f'{eq["numero"]} → {eq["norma"]}' for eq in self.reglas["equivalencias_pedimento"]
                      if not es_norma_valida(eq["norma"], self.reglas)]
        if no_validas:
            avisos.append("Estas equivalencias apuntan a normas que no están en Normas válidas "
                          "(quedarán como SIN NORMA):\n  " + ", ".join(no_validas))
        if avisos and not messagebox.askyesno("Revisar", "\n\n".join(avisos) + "\n\n¿Guardar de todos modos?",
                                              parent=self.ventana):
            return
        try:
            guardar_reglas(self.reglas)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las reglas:\n{e}", parent=self.ventana)
            return
        self.modificado = False
        self.lbl_estado.configure(text="✓ Guardado", text_color=E.COLOR_VERDE)

    def cerrar(self):
        if self.modificado and not messagebox.askyesno("Cambios sin guardar",
                                                       "Hay cambios sin guardar. ¿Cerrar de todos modos?",
                                                       parent=self.ventana):
            return
        self.ventana.destroy()


def abrir_editor_reglas(parent=None):
    return EditorReglas(parent)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    raiz = ctk.CTk()
    raiz.withdraw()
    editor = EditorReglas(raiz)
    if hasattr(editor, "ventana"):
        editor.ventana.bind("<Destroy>", lambda e: raiz.quit() if e.widget is editor.ventana else None)
        raiz.mainloop()
