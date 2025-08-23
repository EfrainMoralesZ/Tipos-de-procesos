"""
Módulo de administración de códigos cumple
Permite gestionar, editar y administrar todos los códigos cumple de la base de datos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import json
import os
from typing import Dict, List, Optional

class AdminCodigosCumple:
    """Clase principal para la administración de códigos cumple"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.df_codigos = None
        self.current_item_index = 0
        self.total_items = 0
        
        # Campos editables con sus opciones
        self.campos_editables = {
            'CRITERIO': ['CUMPLE', 'NO CUMPLE', 'REVISADO', 'PENDIENTE', 'APROBADO', 'RECHAZADO'],
            'ESTADO': ['ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'EN REVISION'],
            'PRIORIDAD': ['ALTA', 'MEDIA', 'BAJA', 'URGENTE'],
            'CATEGORIA': ['TEXTIL', 'CALZADO', 'EQUIPO', 'ACCESORIOS', 'OTROS']
        }
        
        # Crear ventana de administración
        self.crear_ventana_admin()
        
        # Intentar cargar archivo automáticamente si está configurado
        self.parent.after(100, self.intentar_carga_automatica)
    
    def intentar_carga_automatica(self):
        """Intenta cargar el archivo de códigos cumple automáticamente"""
        print("Intentando carga automática de códigos cumple...")
        
        if self.cargar_archivo_automaticamente():
            messagebox.showinfo("Carga Automática", 
                              f"Se ha cargado automáticamente la base de códigos cumple con {self.total_items:,} ítems.\n\n"
                              "Puedes comenzar a administrar los códigos directamente.")
        else:
            print("No se pudo cargar automáticamente. El usuario deberá cargar manualmente.")
            self.btn_cargar.config(text="Cargar Códigos Cumple")
    
    def crear_ventana_admin(self):
        """Crea la ventana principal de administración"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Administrador de Códigos Cumple")
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
                              text="Administrador de Códigos Cumple",
                              font=("Segoe UI", 18, "bold"), 
                              bg="#FFFFFF", fg="#000000")
        title_label.pack(pady=(0, 20))
        
        # Frame de controles superiores
        controls_frame = tk.Frame(main_frame, bg="#FFFFFF")
        controls_frame.pack(fill="x", pady=(0, 20))
        
        # Botón para cargar archivo
        self.btn_cargar = tk.Button(controls_frame, 
                                   text="Cargar Códigos Cumple",
                                   command=self.cargar_archivo_codigos,
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#FFD700", fg="#000000",
                                   relief="flat", padx=20, pady=10)
        self.btn_cargar.pack(side="left", padx=(0, 20))
        
        # Etiqueta de estado
        self.lbl_estado = tk.Label(controls_frame, 
                                  text="Verificando códigos cumple...",
                                  font=("Segoe UI", 12), 
                                  bg="#FFFFFF", fg="#000000")
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
        
        # Frame de búsqueda
        search_frame = tk.Frame(main_frame, bg="#FFFFFF")
        search_frame.pack(fill="x", pady=(0, 20))
        
        # Título de búsqueda
        tk.Label(search_frame, text="Búsqueda de Códigos", font=("Segoe UI", 14, "bold"), 
                bg="#FFFFFF", fg="#000000").pack(anchor="w", pady=(0, 10))
        
        # Fila de filtros
        filter_row = tk.Frame(search_frame, bg="#FFFFFF")
        filter_row.pack(fill="x", pady=5)
        
        # Búsqueda por ITEM
        tk.Label(filter_row, text="ITEM:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=8).pack(side="left")
        self.entry_item = tk.Entry(filter_row, font=("Segoe UI", 10), width=15)
        self.entry_item.pack(side="left", padx=(5, 15))
        
        # Filtro por criterio
        tk.Label(filter_row, text="Criterio:", font=("Segoe UI", 10, "bold"), 
                bg="#FFFFFF", fg="#000000", width=10).pack(side="left")
        self.combo_criterio = ttk.Combobox(filter_row, values=['Todos'] + self.campos_editables['CRITERIO'], 
                                          font=("Segoe UI", 10), state="readonly", width=15)
        self.combo_criterio.set('Todos')
        self.combo_criterio.pack(side="left", padx=(5, 15))
        
        # Botón de búsqueda
        self.btn_buscar = tk.Button(filter_row, text="Buscar", command=self.buscar_codigo,
                                   bg="#FFD700", fg="#000000", relief="flat",
                                   font=("Segoe UI", 11, "bold"), padx=15, pady=5)
        self.btn_buscar.pack(side="left", padx=(0, 10))
        
        # Botón de limpiar
        self.btn_limpiar = tk.Button(filter_row, text="Limpiar", command=self.limpiar_filtros,
                                    bg="#FFD700", fg="#000000", relief="flat",
                                    font=("Segoe UI", 11, "bold"), padx=15, pady=5)
        self.btn_limpiar.pack(side="left", padx=(0, 10))
        
        # Etiqueta de resultados
        self.lbl_resultados = tk.Label(filter_row, text="", font=("Segoe UI", 10), 
                                     bg="#FFFFFF", fg="#666666")
        self.lbl_resultados.pack(side="right", padx=20)
        
        # Frame principal de contenido
        content_frame = tk.Frame(main_frame, bg="#FFFFFF")
        content_frame.pack(fill="both", expand=True)
        
        # Frame izquierdo - Información del código
        left_frame = tk.Frame(content_frame, bg="#FFFFFF", width=500)  # Más ancho
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)
        
        # Título del frame izquierdo
        tk.Label(left_frame, text="Información del Código", 
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
        
        self.btn_exportar = tk.Button(action_frame, text="Exportar Códigos", 
                                     command=self.exportar_codigos,
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
            'ITEM', 'EAN', 'DESCRIPTION', 'MODEL CODE', 'MARCA', 'CUIDADO', 
            'CARACTERISTICAS', 'MEDIDAS', 'CONTENIDO', 'MAGNITUD',
            'DENOMINACION', 'LEYENDAS', 'EDAD', 'INSUMOS'
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
        
        for campo, opciones in self.campos_editables.items():
            frame = tk.Frame(parent, bg="#FFFFFF")
            frame.pack(fill="x", pady=10)
            
            tk.Label(frame, text=f"{campo}:", 
                    font=("Segoe UI", 11, "bold"), 
                    bg="#FFFFFF", fg="#282828", width=25, anchor="w").pack(side="left")
            
            # Crear combobox con opciones
            combo = ttk.Combobox(frame, values=opciones, 
                                font=("Segoe UI", 10), state="readonly", width=30)
            combo.pack(side="right", padx=(10, 0))
            
            # Bind para detectar cambios
            combo.bind('<<ComboboxSelected>>', lambda e, c=campo: self.campo_cambiado(c))
            
            self.campos_editables_widgets[campo] = combo
    
    def cargar_archivo_codigos(self):
        """Carga el archivo de códigos cumple"""
        try:
            # Intentar usar la ruta ya configurada desde el módulo principal
            from Procesos import INSPECCION_PATH
            
            if INSPECCION_PATH and os.path.exists(INSPECCION_PATH):
                ruta_archivo = INSPECCION_PATH
                print(f"Usando archivo ya configurado: {ruta_archivo}")
            else:
                # Solicitar nueva ruta
                ruta_archivo = filedialog.askopenfilename(
                    title="Seleccionar archivo de códigos cumple",
                    filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Archivos JSON", "*.json")]
                )
                if not ruta_archivo:
                    return
                
                # Guardar la ruta en el módulo principal
                import Procesos
                Procesos.INSPECCION_PATH = ruta_archivo
            
            # Cargar el archivo
            if ruta_archivo.endswith('.json'):
                self.df_codigos = pd.read_json(ruta_archivo)
            else:
                self.df_codigos = pd.read_excel(ruta_archivo)
            
            self.total_items = len(self.df_codigos)
            self.current_item_index = 0
            
            # Actualizar interfaz
            self.actualizar_interfaz()
            self.mostrar_item_actual()
            
            # Actualizar estado
            self.lbl_estado.config(text=f"Archivo cargado: {self.total_items:,} códigos", fg="#28A745")
            self.btn_guardar.config(state="normal")
            self.btn_exportar.config(state="normal")
            
            messagebox.showinfo("Éxito", f"Archivo cargado exitosamente con {self.total_items:,} códigos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo:\n{e}")
    
    def cargar_archivo_automaticamente(self):
        """Intenta cargar el archivo de códigos cumple automáticamente"""
        try:
            # Importar la variable desde el módulo principal
            from Procesos import INSPECCION_PATH
            
            if INSPECCION_PATH and os.path.exists(INSPECCION_PATH):
                ruta_archivo = INSPECCION_PATH
                
                # Cargar el archivo
                if ruta_archivo.endswith('.json'):
                    self.df_codigos = pd.read_json(ruta_archivo)
                else:
                    self.df_codigos = pd.read_excel(ruta_archivo)
                
                self.total_items = len(self.df_codigos)
                self.current_item_index = 0
                
                # Actualizar interfaz
                self.actualizar_interfaz()
                self.mostrar_item_actual()
                
                # Actualizar estado
                self.lbl_estado.config(text=f"Archivo cargado automáticamente: {self.total_items:,} códigos", fg="#28A745")
                self.btn_guardar.config(state="normal")
                self.btn_exportar.config(state="normal")
                
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
        if self.df_codigos is not None:
            self.lbl_estado.config(text=f"Base cargada: {self.total_items:,} códigos", fg="#28A745")
            self.btn_cargar.config(text="Recargar Códigos")
        else:
            self.lbl_estado.config(text="Base no cargada", fg="#FF6B35")
            self.btn_cargar.config(text="Cargar Códigos Cumple")
    
    def mostrar_item_actual(self):
        """Muestra el código actual en la interfaz"""
        if self.df_codigos is None or self.current_item_index >= self.total_items:
            return
            
        item = self.df_codigos.iloc[self.current_item_index]
        
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
                combo.set(valor)
            else:
                combo.set("")
        
        # Actualizar navegación
        self.lbl_navegacion.config(text=f"{self.current_item_index + 1} / {self.total_items}")
    
    def item_anterior(self):
        """Navega al código anterior"""
        if self.current_item_index > 0:
            self.current_item_index -= 1
            self.mostrar_item_actual()
            
    def item_siguiente(self):
        """Navega al código siguiente"""
        if self.current_item_index < self.total_items - 1:
            self.current_item_index += 1
            self.mostrar_item_actual()
    
    def buscar_codigo(self):
        """Busca un código por criterios"""
        if self.df_codigos is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar la base de datos")
            return
        
        try:
            # Obtener criterios de búsqueda
            item = self.entry_item.get().strip()
            criterio = self.combo_criterio.get()
            
            # Crear máscara de filtrado
            mask = pd.Series([True] * len(self.df_codigos), index=self.df_codigos.index)
            
            # Aplicar filtros
            if item:
                mask &= self.df_codigos['ITEM'].astype(str).str.contains(item, case=False, na=False)
            
            if criterio != 'Todos':
                mask &= self.df_codigos['CRITERIO'] == criterio
            
            # Aplicar filtros
            resultados = self.df_codigos[mask]
            
            if len(resultados) > 0:
                # Guardar resultados filtrados
                self.resultados_filtrados = resultados
                self.current_item_index = 0
                self.total_items_filtrados = len(resultados)
                
                # Actualizar interfaz
                self.mostrar_item_actual()
                self.actualizar_interfaz_filtrada()
                
                # Mostrar resultados
                self.lbl_resultados.config(text=f"Encontrados: {len(resultados):,} códigos", fg="#28A745")
                messagebox.showinfo("Búsqueda", 
                                  f"Se encontraron {len(resultados):,} códigos que coinciden con los criterios.")
            else:
                self.lbl_resultados.config(text="No se encontraron resultados", fg="#FF6B35")
                messagebox.showwarning("Búsqueda", 
                                     "No se encontraron códigos que coincidan con los criterios especificados.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda:\n{e}")
    
    def limpiar_filtros(self):
        """Limpia todos los filtros de búsqueda"""
        self.entry_item.delete(0, tk.END)
        self.combo_criterio.set('Todos')
        
        # Restaurar vista completa
        if hasattr(self, 'resultados_filtrados'):
            delattr(self, 'resultados_filtrados')
            delattr(self, 'total_items_filtrados')
        
        # Actualizar interfaz
        self.actualizar_interfaz()
        self.lbl_resultados.config(text="", fg="#666666")
        
        messagebox.showinfo("Filtros Limpiados", "Todos los filtros han sido limpiados. Mostrando todos los códigos.")
    
    def actualizar_interfaz_filtrada(self):
        """Actualiza la interfaz cuando hay resultados filtrados"""
        if hasattr(self, 'resultados_filtrados'):
            # Usar resultados filtrados
            self.btn_anterior.config(state="normal")
            self.btn_siguiente.config(state="normal")
            self.lbl_navegacion.config(text=f"{self.current_item_index + 1} / {self.total_items_filtrados}")
            
            # Cambiar texto del botón
            self.btn_cargar.config(text="Restaurar Vista Completa")
        else:
            # Vista normal
            self.actualizar_interfaz()
    
    def campo_cambiado(self, campo):
        """Se ejecuta cuando se cambia un campo editable"""
        pass
        
    def guardar_cambios(self):
        """Guarda los cambios realizados en el código actual"""
        try:
            if self.df_codigos is None:
                return
                
            # Obtener valores actuales de los campos editables
            for campo, combo in self.campos_editables_widgets.items():
                nuevo_valor = combo.get()
                if nuevo_valor:
                    self.df_codigos.at[self.current_item_index, campo] = nuevo_valor
                    
            messagebox.showinfo("Éxito", "Cambios guardados en memoria")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cambios:\n{e}")
            
    def exportar_codigos(self):
        """Exporta la base de códigos cumple modificada"""
        try:
            if self.df_codigos is None:
                return
                
            # Solicitar ruta de guardado
            ruta_guardado = filedialog.asksaveasfilename(
                title="Guardar Códigos Cumple Modificados",
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Archivos JSON", "*.json")]
            )
            
            if not ruta_guardado:
                return
                
            # Guardar según la extensión
            if ruta_guardado.endswith('.json'):
                self.df_codigos.to_json(ruta_guardado, orient="records", indent=2)
            else:
                self.df_codigos.to_excel(ruta_guardado, index=False)
                
            messagebox.showinfo("Éxito", f"Códigos cumple exportados a:\n{ruta_guardado}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

def abrir_admin_codigos_cumple(parent_window):
    """Función para abrir la ventana de administración de códigos cumple"""
    AdminCodigosCumple(parent_window)
