"""
Módulo de administración de ítems para la base DECATHLON GENERAL
Permite gestionar, editar y administrar todos los ítems de la base de datos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import json
import os
from typing import Dict, List, Optional

class AdminItems:
    """Clase principal para la administración de ítems"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.df_base = None
        self.current_item_index = 0
        self.total_items = 0
        
        # Campos editables con sus opciones
        self.campos_editables = {
            'NORMA': ['NOM-003', 'NOM-004', 'NOM-004-SE-2021', 'NOM-008', 'NOM-015', 'NOM-020', 'NOM-024', 'NOM-035', 'NOM-050', 'NOM-051', 'NOM-116', 'NOM-141', 'NOM-142', 'NOM-173', 'NOM-185', 'NOM-186', 'NOM-189', 'NOM-192', 'NOM-199', 'NOM-235', 'SIN NORMA'],
            'CODIGO FORMATO': ['NOM003', 'NOM004', 'NOM004TEXX', 'NOM008', 'NOM015', 'NOM020', 'NOM020INS', 'NOM024', 'NOM035', 'NOM050', 'NOM051', 'NOM116', 'NOM141', 'NOM142', 'NOM173', 'NOM185', 'NOM186', 'NOM189', 'NOM192', 'NOM199', 'NOM235'],
            'TIPO DE ETIQUETA': ['A', 'B', 'C', 'D', 'E', 'F'],
            'CLIENTE': ['DECATHLON', 'OTRO', 'SPORTLINE', 'GO SPORT', 'INTERSPORT'],
            'LOGO NOM': ['0', '1', '2'],
            'LISTA': ['PZA', 'KG', 'L', 'M', 'M2', 'M3', 'PAR', 'SET', 'UNIDAD']
        }
        
        # Crear ventana de administración
        self.crear_ventana_admin()
        
        # Intentar cargar archivo automáticamente si está configurado
        self.parent.after(100, self.intentar_carga_automatica)
    
    def intentar_carga_automatica(self):
        """Intenta cargar el archivo base automáticamente"""
        print("Intentando carga automática de la base de Decathlon...")
        
        if self.cargar_archivo_automaticamente():
            messagebox.showinfo("Carga Automática", 
                              f"Se ha cargado automáticamente la base de Decathlon con {self.total_items:,} ítems.\n\n"
                              "Puedes comenzar a administrar los ítems directamente.")
        else:
            print("No se pudo cargar automáticamente. El usuario deberá cargar manualmente.")
            # Cambiar el texto del botón para indicar que se puede cargar
            self.btn_cargar.config(text="Cargar Base de Decathlon")
        
    def crear_ventana_admin(self):
        """Crea la ventana principal de administración"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Administrador de Ítems - BASE DECATHLON GENERAL")
        self.window.geometry("1400x900")
        self.window.configure(bg="#FFFFFF")
        
        # Hacer la ventana modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        """Crea la interfaz de usuario"""
        # Frame principal con scrollbar
        main_canvas = tk.Canvas(self.window, bg="#FFFFFF")
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#FFFFFF")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame principal
        main_frame = tk.Frame(scrollable_frame, bg="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text="Administrador de Ítems - BASE DECATHLON GENERAL",
                              font=("Segoe UI", 18, "bold"), 
                              bg="#FFFFFF", fg="#000000")  # Negro para el texto
        title_label.pack(pady=(0, 20))
        
        # Frame de controles superiores
        controls_frame = tk.Frame(main_frame, bg="#FFFFFF")
        controls_frame.pack(fill="x", pady=(0, 20))
        
        # Botón para cargar archivo
        self.btn_cargar = tk.Button(controls_frame, 
                                   text="Cargar Archivo Base",
                                   command=self.cargar_archivo_base,
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#FFD700", fg="#000000",  # Amarillo dorado y negro
                                   relief="flat", padx=20, pady=10)
        self.btn_cargar.pack(side="left", padx=(0, 20))
        
        # Botón para restaurar vista completa (inicialmente oculto)
        self.btn_restaurar = tk.Button(controls_frame, 
                                     text="Restaurar Vista Completa",
                                     command=self.restaurar_vista_completa,
                                     font=("Segoe UI", 12, "bold"),
                                     bg="#FFD700", fg="#000000",  # Amarillo dorado y negro
                                     relief="flat", padx=20, pady=10)
        self.btn_restaurar.pack(side="left", padx=(0, 20))
        self.btn_restaurar.pack_forget()  # Oculto inicialmente
        
        # Etiqueta de estado
        self.lbl_estado = tk.Label(controls_frame, 
                                  text="Verificando base de Decathlon...",
                                  font=("Segoe UI", 12), 
                                  bg="#FFFFFF", fg="#000000")  # Negro para el texto
        self.lbl_estado.pack(side="left", padx=20)
        
        # Frame de navegación
        nav_frame = tk.Frame(main_frame, bg="#FFFFFF")
        nav_frame.pack(fill="x", pady=(0, 20))
        
        # Controles de navegación
        tk.Label(nav_frame, text="Navegación:", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#000000").pack(side="left")
        
        self.btn_anterior = tk.Button(nav_frame, text="◀ Anterior", command=self.item_anterior,
                                     state="disabled", bg="#FFD700", fg="#000000", relief="flat")
        self.btn_anterior.pack(side="left", padx=10)
        
        self.lbl_navegacion = tk.Label(nav_frame, text="0 / 0", font=("Segoe UI", 12), bg="#FFFFFF", fg="#000000")
        self.lbl_navegacion.pack(side="left", padx=10)
        
        self.btn_siguiente = tk.Button(nav_frame, text="Siguiente ▶", command=self.item_siguiente,
                                      state="disabled", bg="#FFD700", fg="#000000", relief="flat")
        self.btn_siguiente.pack(side="left", padx=10)
        
        # Frame de búsqueda avanzada
        search_frame = tk.Frame(main_frame, bg="#FFFFFF")
        search_frame.pack(fill="x", pady=(0, 20))
        
        # Título de búsqueda
        tk.Label(search_frame, text="Búsqueda Avanzada", font=("Segoe UI", 14, "bold"), 
                bg="#FFFFFF", fg="#000000").pack(anchor="w", pady=(0, 10))
        
        # Primera fila de filtros
        filter_row1 = tk.Frame(search_frame, bg="#FFFFFF")
        filter_row1.pack(fill="x", pady=5)
        
        # Búsqueda por EAN
        tk.Label(filter_row1, text="EAN:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=8).pack(side="left")
        self.entry_ean = tk.Entry(filter_row1, font=("Segoe UI", 10), width=15)
        self.entry_ean.pack(side="left", padx=(5, 15))
        
        # Búsqueda por descripción
        tk.Label(filter_row1, text="Descripción:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=10).pack(side="left")
        self.entry_descripcion = tk.Entry(filter_row1, font=("Segoe UI", 10), width=25)
        self.entry_descripcion.pack(side="left", padx=(5, 15))
        
        # Búsqueda por marca
        tk.Label(filter_row1, text="Marca:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=8).pack(side="left")
        self.entry_marca = tk.Entry(filter_row1, font=("Segoe UI", 10), width=15)
        self.entry_marca.pack(side="left", padx=(5, 15))
        
        # Segunda fila de filtros
        filter_row2 = tk.Frame(search_frame, bg="#FFFFFF")
        filter_row2.pack(fill="x", pady=5)
        
        # Filtro por norma
        tk.Label(filter_row2, text="Norma:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=8).pack(side="left")
        self.combo_norma = ttk.Combobox(filter_row2, values=['Todas'] + self.campos_editables['NORMA'], 
                                       font=("Segoe UI", 10), state="readonly", width=15)
        self.combo_norma.set('Todas')
        self.combo_norma.pack(side="left", padx=(5, 15))
        
        # Filtro por tipo de proceso
        tk.Label(filter_row2, text="Tipo Proceso:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=12).pack(side="left")
        self.combo_tipo_proceso = ttk.Combobox(filter_row2, 
                                              values=['Todos', 'ADHERIBLE', 'COSTURA', 'CUMPLE', 'SIN NORMA'], 
                                              font=("Segoe UI", 10), state="readonly", width=15)
        self.combo_tipo_proceso.set('Todos')
        self.combo_tipo_proceso.pack(side="left", padx=(5, 15))
        
        # Filtro por país
        tk.Label(filter_row2, text="País:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=8).pack(side="left")
        self.entry_pais = tk.Entry(filter_row2, font=("Segoe UI", 10), width=15)
        self.entry_pais.pack(side="left", padx=(5, 15))
        
        # Tercera fila - botones de búsqueda
        filter_row3 = tk.Frame(search_frame, bg="#FFFFFF")
        filter_row3.pack(fill="x", pady=10)
        
        # Botón de búsqueda
        self.btn_buscar_avanzada = tk.Button(filter_row3, text="Buscar Avanzada", 
                                            command=self.busqueda_avanzada,
                                            bg="#FFD700", fg="#000000", relief="flat",
                                            font=("Segoe UI", 11, "bold"), padx=20, pady=5)
        self.btn_buscar_avanzada.pack(side="left", padx=(0, 10))
        
        # Botón de limpiar filtros
        self.btn_limpiar_filtros = tk.Button(filter_row3, text="Limpiar Filtros", 
                                            command=self.limpiar_filtros,
                                            bg="#FFD700", fg="#000000", relief="flat",
                                            font=("Segoe UI", 11, "bold"), padx=20, pady=5)
        self.btn_limpiar_filtros.pack(side="left", padx=(0, 10))
        
        # Botón de búsqueda rápida
        self.btn_busqueda_rapida = tk.Button(filter_row3, text="Búsqueda Rápida", 
                                           command=self.busqueda_rapida,
                                           bg="#FFD700", fg="#000000", relief="flat",
                                           font=("Segoe UI", 11, "bold"), padx=20, pady=5)
        self.btn_busqueda_rapida.pack(side="left", padx=(0, 10))
        
        # Etiqueta de resultados
        self.lbl_resultados = tk.Label(filter_row3, text="", font=("Segoe UI", 10), 
                                     bg="#FFFFFF", fg="#666666")
        self.lbl_resultados.pack(side="right", padx=20)
        
        # Frame principal de contenido
        content_frame = tk.Frame(main_frame, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True)
        
        # Frame izquierdo - Información del ítem
        left_frame = tk.Frame(content_frame, bg="#FFFFFF", width=500)  # Más ancho
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)
        
        # Título del frame izquierdo
        tk.Label(left_frame, text="Información del Ítem", 
                font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=(0, 15))
        
        # Campos de solo lectura
        self.crear_campos_solo_lectura(left_frame)
        
        # Frame derecho - Campos editables
        right_frame = tk.Frame(content_frame, bg="#FFFFFF")
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Título del frame derecho
        tk.Label(right_frame, text="Campos Editables", 
                font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=(0, 15))
        
        # Campos editables
        self.crear_campos_editables(right_frame)
        
        # Frame de botones de acción
        action_frame = tk.Frame(main_frame, bg="#FFFFFF")
        action_frame.pack(fill="x", pady=20)
        
        # Botones de acción
        self.btn_guardar = tk.Button(action_frame, text="Guardar Cambios", 
                                    command=self.guardar_cambios,
                                    state="disabled",
                                    font=("Segoe UI", 12, "bold"),
                                    bg="#FFD700", fg="#000000", relief="flat", padx=20, pady=10)
        self.btn_guardar.pack(side="left", padx=(0, 20))
        
        self.btn_exportar = tk.Button(action_frame, text="Exportar Base", 
                                     command=self.exportar_base,
                                     state="disabled",
                                     font=("Segoe UI", 12, "bold"),
                                     bg="#FFD700", fg="#000000", relief="flat", padx=20, pady=10)
        self.btn_exportar.pack(side="left", padx=(0, 20))
        
        self.btn_cerrar = tk.Button(action_frame, text="Cerrar", 
                                   command=self.window.destroy,
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#FFD700", fg="#000000", relief="flat", padx=20, pady=10)
        self.btn_cerrar.pack(side="right")
        
        # Configurar scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para scroll con mouse
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind("<MouseWheel>", _on_mousewheel)
        
    def crear_campos_solo_lectura(self, parent):
        """Crea los campos de solo lectura"""
        campos_solo_lectura = [
            'EAN', 'DESCRIPTION', 'MODEL CODE', 'MARCA', 'CUIDADO', 
            'CARACTERISTICAS', 'MEDIDAS', 'CONTENIDO', 'MAGNITUD',
            'DENOMINACION', 'LEYENDAS', 'EDAD', 'INSUMOS', 'FORRO',
            'TALLA', 'PAIS ORIGEN', 'IMPORTADOR', 'ITEM ESPAÑOL',
            'TYPE OF GOODS', 'HS CODE'
        ]
        
        self.campos_solo_lectura = {}
        
        for campo in campos_solo_lectura:
            frame = tk.Frame(parent, bg="#FFFFFF")
            frame.pack(fill="x", pady=5)
            
            tk.Label(frame, text=f"{campo}:", 
                    font=("Segoe UI", 10, "bold"), 
                    bg="#FFFFFF", fg="#282828", width=20, anchor="w").pack(side="left")
            
            entry = tk.Entry(frame, font=("Segoe UI", 10), state="readonly", bg="#F5F5F5", fg="#282828")
            entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
            
            self.campos_solo_lectura[campo] = entry
            
    def crear_campos_editables(self, parent):
        """Crea los campos editables con menús desplegables"""
        self.campos_editables_widgets = {}
        
        # Crear campos editables con combobox
        for campo, opciones in self.campos_editables.items():
            frame = tk.Frame(parent, bg="#FFFFFF")
            frame.pack(fill="x", pady=5)
            
            tk.Label(frame, text=f"{campo}:", 
                    font=("Segoe UI", 10, "bold"), 
                    bg="#FFFFFF", fg="#282828", width=20, anchor="w").pack(side="left")
            
            combo = ttk.Combobox(frame, values=opciones, 
                                font=("Segoe UI", 10), state="readonly", width=30)
            combo.pack(side="right", padx=(10, 0))
            
            # Bind para detectar cambios
            combo.bind('<<ComboboxSelected>>', lambda e, c=campo: self.campo_cambiado(c))
            
            self.campos_editables_widgets[campo] = combo
        
        # Campo de país como texto libre
        frame_pais = tk.Frame(parent, bg="#FFFFFF")
        frame_pais.pack(fill="x", pady=5)
        
        tk.Label(frame_pais, text="PAIS DE PROCEDENCIA:", 
                font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#282828", width=20, anchor="w").pack(side="left")
        
        self.entry_pais_editable = tk.Entry(frame_pais, font=("Segoe UI", 10), width=30)
        self.entry_pais_editable.pack(side="right", padx=(10, 0))
        
        # Bind para detectar cambios
        self.entry_pais_editable.bind('<KeyRelease>', lambda e: self.campo_cambiado('PAIS DE PROCEDENCIA'))
        
        self.campos_editables_widgets['PAIS DE PROCEDENCIA'] = self.entry_pais_editable
            
    def cargar_archivo_base(self):
        """Carga el archivo base desde la ruta configurada o solicita nueva ruta"""
        try:
            # Buscar la variable BASE_GENERAL_PATH en diferentes ubicaciones
            ruta_archivo = None
            
            # Opción 1: Buscar en la ventana principal
            if hasattr(self.parent, 'BASE_GENERAL_PATH') and self.parent.BASE_GENERAL_PATH:
                ruta_archivo = self.parent.BASE_GENERAL_PATH
                print(f"Usando archivo ya configurado en ventana principal: {ruta_archivo}")
            
            # Opción 2: Buscar en el módulo principal (Procesos.py)
            elif 'BASE_GENERAL_PATH' in globals():
                ruta_archivo = globals()['BASE_GENERAL_PATH']
                print(f"Usando archivo ya configurado en módulo principal: {ruta_archivo}")
            
            # Opción 3: Buscar en el directorio de recursos
            if not ruta_archivo or not os.path.exists(ruta_archivo):
                recursos_path = os.path.join(os.path.dirname(__file__), "resources", "base_general.json")
                if os.path.exists(recursos_path):
                    ruta_archivo = recursos_path
                    print(f"Usando archivo de recursos: {ruta_archivo}")
            
            # Si no se encontró ninguna ruta, solicitar nueva
            if not ruta_archivo or not os.path.exists(ruta_archivo):
                ruta_archivo = filedialog.askopenfilename(
                    title="Seleccionar archivo BASE DECATHLON GENERAL",
                    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
                )
                if not ruta_archivo:
                    return
                
                # Guardar la ruta en la ventana principal
                if not hasattr(self.parent, 'BASE_GENERAL_PATH'):
                    self.parent.BASE_GENERAL_PATH = ruta_archivo
            
            # Cargar el archivo
            if ruta_archivo.endswith('.json'):
                self.df_base = pd.read_json(ruta_archivo)
            else:
                self.df_base = pd.read_excel(ruta_archivo)
            
            self.total_items = len(self.df_base)
            self.current_item_index = 0
            
            # Actualizar interfaz
            self.actualizar_interfaz()
            self.mostrar_item_actual()
            
            # Actualizar estado
            self.lbl_estado.config(text=f"Archivo cargado: {self.total_items:,} ítems", fg="#28A745")
            self.btn_guardar.config(state="normal")
            self.btn_exportar.config(state="normal")
            
            messagebox.showinfo("Éxito", f"Archivo cargado exitosamente con {self.total_items:,} ítems")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo:\n{e}")
    
    def cargar_archivo_automaticamente(self):
        """Intenta cargar el archivo base automáticamente si está configurado"""
        try:
            # Buscar la variable BASE_GENERAL_PATH en diferentes ubicaciones
            ruta_archivo = None
            
            # Opción 1: Buscar en la ventana principal
            if hasattr(self.parent, 'BASE_GENERAL_PATH') and self.parent.BASE_GENERAL_PATH:
                ruta_archivo = self.parent.BASE_GENERAL_PATH
                print(f"Encontrada ruta en ventana principal: {ruta_archivo}")
            
            # Opción 2: Buscar en el módulo principal (Procesos.py)
            elif 'BASE_GENERAL_PATH' in globals():
                ruta_archivo = globals()['BASE_GENERAL_PATH']
                print(f"Encontrada ruta en módulo principal: {ruta_archivo}")
            
            # Opción 3: Buscar en el directorio de recursos
            if not ruta_archivo or not os.path.exists(ruta_archivo):
                recursos_path = os.path.join(os.path.dirname(__file__), "resources", "base_general.json")
                if os.path.exists(recursos_path):
                    ruta_archivo = recursos_path
                    print(f"Usando archivo de recursos: {ruta_archivo}")
            
            if ruta_archivo and os.path.exists(ruta_archivo):
                # Cargar el archivo
                if ruta_archivo.endswith('.json'):
                    self.df_base = pd.read_json(ruta_archivo)
                else:
                    self.df_base = pd.read_excel(ruta_archivo)
                
                self.total_items = len(self.df_base)
                self.current_item_index = 0
                
                # Actualizar interfaz
                self.actualizar_interfaz()
                self.mostrar_item_actual()
                
                # Habilitar botones de acción
                self.btn_guardar.config(state="normal")
                self.btn_exportar.config(state="normal")
                
                print(f"Base de Decathlon cargada exitosamente con {self.total_items:,} ítems")
                return True
                
        except Exception as e:
            print(f"Error cargando archivo automáticamente: {e}")
        
        return False
            
    def actualizar_interfaz(self):
        """Actualiza la interfaz después de cargar el archivo"""
        # Habilitar navegación
        self.btn_anterior.config(state="normal")
        self.btn_siguiente.config(state="normal")
        
        # Actualizar etiqueta de navegación
        self.lbl_navegacion.config(text=f"{self.current_item_index + 1} / {self.total_items}")
        
        # Actualizar estado de la base
        if self.df_base is not None:
            self.lbl_estado.config(text=f"Base cargada: {self.total_items:,} ítems", fg="#28A745")
            self.btn_cargar.config(text="Recargar Base")
        else:
            self.lbl_estado.config(text="Base no cargada", fg="#FF6B35")
            self.btn_cargar.config(text="Cargar Base de Decathlon")
        
    def buscar_item(self, event=None):
        """Busca un ítem por EAN o descripción"""
        termino = self.entry_ean.get().strip()
        if not termino:
            return
            
        try:
            # Buscar por EAN
            if termino.isdigit():
                mask = self.df_base['EAN'].astype(str) == termino
            else:
                # Buscar por descripción
                mask = self.df_base['DESCRIPTION'].str.contains(termino, case=False, na=False)
            
            if mask.any():
                self.current_item_index = mask.idxmax()
                self.mostrar_item_actual()
                messagebox.showinfo("Búsqueda", f"Ítem encontrado en posición {self.current_item_index + 1}")
            else:
                messagebox.showwarning("Búsqueda", "No se encontró ningún ítem con ese término")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda:\n{e}")
    
    def busqueda_avanzada(self):
        """Realiza una búsqueda avanzada con múltiples criterios"""
        if self.df_base is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar la base de datos")
            return
        
        try:
            # Obtener criterios de búsqueda
            ean = self.entry_ean.get().strip()
            descripcion = self.entry_descripcion.get().strip()
            marca = self.entry_marca.get().strip()
            norma = self.combo_norma.get()
            tipo_proceso = self.combo_tipo_proceso.get()
            pais = self.entry_pais.get().strip() # Obtener texto libre del Entry
            
            # Crear máscara de filtrado
            mask = pd.Series([True] * len(self.df_base), index=self.df_base.index)
            
            # Aplicar filtros
            if ean:
                mask &= self.df_base['EAN'].astype(str).str.contains(ean, case=False, na=False)
            
            if descripcion:
                mask &= self.df_base['DESCRIPTION'].str.contains(descripcion, case=False, na=False)
            
            if marca:
                mask &= self.df_base['MARCA'].str.contains(marca, case=False, na=False)
            
            if norma != 'Todas':
                mask &= self.df_base['NORMA'] == norma
            
            if tipo_proceso != 'Todos':
                # Buscar en el campo TIPO DE PROCESO si existe
                if 'TIPO DE PROCESO' in self.df_base.columns:
                    mask &= self.df_base['TIPO DE PROCESO'] == tipo_proceso
                else:
                    # Si no existe, intentar inferir del código de formato
                    if tipo_proceso == 'ADHERIBLE':
                        mask &= self.df_base['CODIGO FORMATO'].str.contains('TEXX|INS', case=False, na=False)
                    elif tipo_proceso == 'COSTURA':
                        mask &= self.df_base['CODIGO FORMATO'].str.contains('004|020', case=False, na=False)
            
            if pais: # Aplicar filtro de país solo si el usuario ingresó algo
                mask &= self.df_base['PAIS DE PROCEDENCIA'].str.contains(pais, case=False, na=False)
            
            # Aplicar filtros
            resultados = self.df_base[mask]
            
            if len(resultados) > 0:
                # Guardar resultados filtrados
                self.resultados_filtrados = resultados
                self.current_item_index = 0
                self.total_items_filtrados = len(resultados)
                
                # Actualizar interfaz
                self.mostrar_item_actual()
                self.actualizar_interfaz_filtrada()
                
                # Mostrar resultados
                self.lbl_resultados.config(text=f"Encontrados: {len(resultados):,} ítems", fg="#28A745")
                messagebox.showinfo("Búsqueda Avanzada", 
                                  f"Se encontraron {len(resultados):,} ítems que coinciden con los criterios.\n\n"
                                  f"Mostrando resultado 1 de {len(resultados):,}")
            else:
                self.lbl_resultados.config(text="No se encontraron resultados", fg="#FF6B35")
                messagebox.showwarning("Búsqueda Avanzada", 
                                     "No se encontraron ítems que coincidan con los criterios especificados.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda avanzada:\n{e}")
    
    def busqueda_rapida(self):
        """Búsqueda rápida con autocompletado"""
        if self.df_base is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar la base de datos")
            return
        
        # Crear ventana de búsqueda rápida
        self.crear_ventana_busqueda_rapida()
    
    def crear_ventana_busqueda_rapida(self):
        """Crea una ventana de búsqueda rápida con autocompletado"""
        self.ventana_busqueda = tk.Toplevel(self.window)
        self.ventana_busqueda.title("Búsqueda Rápida")
        self.ventana_busqueda.geometry("500x400")
        self.ventana_busqueda.configure(bg="#FFFFFF")
        
        # Hacer la ventana modal
        self.ventana_busqueda.transient(self.window)
        self.ventana_busqueda.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(self.ventana_busqueda, bg="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Búsqueda Rápida con Autocompletado", 
                font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#282828").pack(pady=(0, 20))
        
        # Campo de búsqueda
        tk.Label(main_frame, text="Escribe para buscar:", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#282828").pack(anchor="w")
        
        self.entry_busqueda_rapida = tk.Entry(main_frame, font=("Segoe UI", 14), width=40)
        self.entry_busqueda_rapida.pack(fill="x", pady=(10, 20))
        self.entry_busqueda_rapida.bind('<KeyRelease>', self.autocompletar_busqueda)
        self.entry_busqueda_rapida.focus()
        
        # Lista de sugerencias
        tk.Label(main_frame, text="Sugerencias:", 
                font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#282828").pack(anchor="w")
        
        # Frame para la lista
        list_frame = tk.Frame(main_frame, bg="#FFFFFF")
        list_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox con sugerencias
        self.listbox_sugerencias = tk.Listbox(list_frame, font=("Segoe UI", 11), 
                                            yscrollcommand=scrollbar.set, height=15)
        self.listbox_sugerencias.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox_sugerencias.yview)
        
        # Bind para selección
        self.listbox_sugerencias.bind('<Double-Button-1>', self.seleccionar_sugerencia)
        self.listbox_sugerencias.bind('<Return>', self.seleccionar_sugerencia)
        
        # Botones
        button_frame = tk.Frame(main_frame, bg="#FFFFFF")
        button_frame.pack(fill="x", pady=(20, 0))
        
        tk.Button(button_frame, text="Buscar", command=self.ejecutar_busqueda_rapida,
                 bg="#FFD700", fg="#000000", relief="flat", font=("Segoe UI", 11, "bold"),
                 padx=20, pady=5).pack(side="left", padx=(0, 10))
        
        tk.Button(button_frame, text="Cerrar", command=self.ventana_busqueda.destroy,
                 bg="#FFD700", fg="#000000", relief="flat", font=("Segoe UI", 11, "bold"),
                 padx=20, pady=5).pack(side="right")
    
    def autocompletar_busqueda(self, event=None):
        """Genera sugerencias de autocompletado"""
        termino = self.entry_busqueda_rapida.get().strip().lower()
        
        if len(termino) < 2:
            self.listbox_sugerencias.delete(0, tk.END)
            return
        
        try:
            # Buscar en múltiples campos
            sugerencias = set()
            
            # Buscar en EAN
            mask_ean = self.df_base['EAN'].astype(str).str.contains(termino, case=False, na=False)
            sugerencias.update(self.df_base[mask_ean]['EAN'].astype(str).head(10).tolist())
            
            # Buscar en descripción
            mask_desc = self.df_base['DESCRIPTION'].str.contains(termino, case=False, na=False)
            sugerencias.update(self.df_base[mask_desc]['DESCRIPTION'].head(10).tolist())
            
            # Buscar en marca
            mask_marca = self.df_base['MARCA'].str.contains(termino, case=False, na=False)
            sugerencias.update(self.df_base[mask_marca]['MARCA'].head(10).tolist())
            
            # Limpiar y mostrar sugerencias
            self.listbox_sugerencias.delete(0, tk.END)
            for sugerencia in sorted(list(sugerencias))[:20]:  # Máximo 20 sugerencias
                self.listbox_sugerencias.insert(tk.END, sugerencia)
                
        except Exception as e:
            print(f"Error en autocompletado: {e}")
    
    def seleccionar_sugerencia(self, event=None):
        """Selecciona una sugerencia de la lista"""
        try:
            seleccion = self.listbox_sugerencias.get(self.listbox_sugerencias.curselection())
            self.entry_busqueda_rapida.delete(0, tk.END)
            self.entry_busqueda_rapida.insert(0, seleccion)
        except:
            pass
    
    def ejecutar_busqueda_rapida(self):
        """Ejecuta la búsqueda rápida"""
        termino = self.entry_busqueda_rapida.get().strip()
        if not termino:
            return
        
        try:
            # Buscar en múltiples campos
            mask = (
                self.df_base['EAN'].astype(str).str.contains(termino, case=False, na=False) |
                self.df_base['DESCRIPTION'].str.contains(termino, case=False, na=False) |
                self.df_base['MARCA'].str.contains(termino, case=False, na=False)
            )
            
            resultados = self.df_base[mask]
            
            if len(resultados) > 0:
                # Guardar resultados
                self.resultados_filtrados = resultados
                self.current_item_index = 0
                self.total_items_filtrados = len(resultados)
                
                # Actualizar interfaz
                self.mostrar_item_actual()
                self.actualizar_interfaz_filtrada()
                
                # Cerrar ventana de búsqueda
                self.ventana_busqueda.destroy()
                
                # Mostrar resultados
                self.lbl_resultados.config(text=f"Búsqueda rápida: {len(resultados):,} ítems", fg="#28A745")
                messagebox.showinfo("Búsqueda Rápida", 
                                  f"Se encontraron {len(resultados):,} ítems que coinciden con '{termino}'")
            else:
                messagebox.showwarning("Búsqueda Rápida", 
                                     f"No se encontraron ítems que coincidan con '{termino}'")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda rápida:\n{e}")
    
    def limpiar_filtros(self):
        """Limpia todos los filtros de búsqueda"""
        self.entry_ean.delete(0, tk.END)
        self.entry_descripcion.delete(0, tk.END)
        self.entry_marca.delete(0, tk.END)
        self.combo_norma.set('Todas')
        self.combo_tipo_proceso.set('Todos')
        self.entry_pais.delete(0, tk.END) # Limpiar el Entry de país
        
        # Restaurar vista completa
        if hasattr(self, 'resultados_filtrados'):
            delattr(self, 'resultados_filtrados')
            delattr(self, 'total_items_filtrados')
        
        # Actualizar interfaz
        self.actualizar_interfaz()
        self.lbl_resultados.config(text="", fg="#666666")
        
        messagebox.showinfo("Filtros Limpiados", "Todos los filtros han sido limpiados. Mostrando todos los ítems.")
    
    def restaurar_vista_completa(self):
        """Restaura la vista completa de todos los ítems"""
        try:
            # Restaurar vista completa
            if hasattr(self, 'resultados_filtrados'):
                delattr(self, 'resultados_filtrados')
                delattr(self, 'total_items_filtrados')
            
            # Resetear índice
            self.current_item_index = 0
            
            # Actualizar interfaz
            self.actualizar_interfaz()
            self.mostrar_item_actual()
            
            # Limpiar etiqueta de resultados
            self.lbl_resultados.config(text="", fg="#666666")
            
            # Ocultar botón de restaurar
            self.btn_restaurar.pack_forget()
            
            messagebox.showinfo("Vista Restaurada", "Se ha restaurado la vista completa de todos los ítems.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar vista completa:\n{e}")
    
    def actualizar_interfaz_filtrada(self):
        """Actualiza la interfaz cuando hay resultados filtrados"""
        if hasattr(self, 'resultados_filtrados'):
            # Usar resultados filtrados
            self.btn_anterior.config(state="normal")
            self.btn_siguiente.config(state="normal")
            self.lbl_navegacion.config(text=f"{self.current_item_index + 1} / {self.total_items_filtrados}")
            
            # Cambiar texto del botón y mostrar botón de restaurar
            self.btn_cargar.config(text="Recargar Base")
            self.btn_restaurar.pack()
        else:
            # Vista normal
            self.actualizar_interfaz()
            self.btn_restaurar.pack_forget()
        
    def mostrar_item_actual(self):
        """Muestra el ítem actual en la interfaz"""
        if self.df_base is None:
            return
        
        # Determinar qué DataFrame usar
        if hasattr(self, 'resultados_filtrados'):
            df_actual = self.resultados_filtrados
            total_actual = self.total_items_filtrados
        else:
            df_actual = self.df_base
            total_actual = self.total_items
        
        if self.current_item_index >= total_actual:
            return
            
        item = df_actual.iloc[self.current_item_index]
        
        # Actualizar campos de solo lectura
        for campo, entry in self.campos_solo_lectura.items():
            if campo in item:
                valor = str(item[campo]) if pd.notna(item[campo]) else ""
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, valor)
                entry.config(state="readonly")
            else:
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.config(state="readonly")
        
        # Actualizar campos editables
        for campo, combo in self.campos_editables_widgets.items():
            if campo in item:
                valor = str(item[campo]) if pd.notna(item[campo]) else ""
                if isinstance(combo, ttk.Combobox):
                combo.set(valor)
                elif isinstance(combo, tk.Entry):
                    combo.delete(0, tk.END)
                    combo.insert(0, valor)
            else:
                if isinstance(combo, ttk.Combobox):
                combo.set("")
                elif isinstance(combo, tk.Entry):
                    combo.delete(0, tk.END)
                    combo.insert(0, "")
        
        # Actualizar navegación
        if hasattr(self, 'resultados_filtrados'):
            self.lbl_navegacion.config(text=f"{self.current_item_index + 1} / {self.total_items_filtrados}")
        else:
        self.lbl_navegacion.config(text=f"{self.current_item_index + 1} / {self.total_items}")
        
    def item_anterior(self):
        """Navega al ítem anterior"""
        if self.current_item_index > 0:
            self.current_item_index -= 1
            self.mostrar_item_actual()
            
    def item_siguiente(self):
        """Navega al ítem siguiente"""
        # Determinar el límite máximo
        if hasattr(self, 'resultados_filtrados'):
            limite = self.total_items_filtrados
        else:
            limite = self.total_items
            
        if self.current_item_index < limite - 1:
            self.current_item_index += 1
            self.mostrar_item_actual()
            
    def campo_cambiado(self, campo):
        """Se ejecuta cuando se cambia un campo editable"""
        # Aquí puedes agregar lógica adicional si es necesario
        pass
        
    def guardar_cambios(self):
        """Guarda los cambios realizados en el ítem actual"""
        try:
            if self.df_base is None:
                return
                
            # Obtener valores actuales de los campos editables
            for campo, combo in self.campos_editables_widgets.items():
                if isinstance(combo, ttk.Combobox):
                    nuevo_valor = combo.get()
                elif isinstance(combo, tk.Entry):
                nuevo_valor = combo.get()
                else:
                    nuevo_valor = "" # Para otros tipos de widgets
                    
                if nuevo_valor:
                    self.df_base.at[self.current_item_index, campo] = nuevo_valor
                    
            messagebox.showinfo("Éxito", "Cambios guardados en memoria")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cambios:\n{e}")
            
    def exportar_base(self):
        """Exporta la base de datos modificada"""
        try:
            if self.df_base is None:
                return
                
            # Solicitar ruta de guardado
            ruta_guardado = filedialog.asksaveasfilename(
                title="Guardar Base de Datos Modificada",
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Archivos JSON", "*.json")]
            )
            
            if not ruta_guardado:
                return
                
            # Guardar según la extensión
            if ruta_guardado.endswith('.json'):
                self.df_base.to_json(ruta_guardado, orient="records", indent=2)
            else:
                self.df_base.to_excel(ruta_guardado, index=False)
                
            messagebox.showinfo("Éxito", f"Base de datos exportada a:\n{ruta_guardado}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

def abrir_admin_items(parent_window):
    """Función para abrir la ventana de administración de ítems"""
    AdminItems(parent_window)
