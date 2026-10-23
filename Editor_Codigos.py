import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import Estilos as E
import pandas as pd
import json
import os
import numpy as np
import Rutas
import sys

def recurso_path(ruta_relativa):
    """
    Devuelve la ruta correcta del recurso, ya sea en desarrollo o en .exe.
    """
    try:
        # Ruta temporal dentro del ejecutable
        base_path = sys._MEIPASS
    except AttributeError:
        # Ruta normal durante desarrollo
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)


class EditorCodigos:
    def __init__(self, parent, archivo_excel, archivo_json):
        self.parent = parent
        self.ARCHIVO_CODIGOS = archivo_excel
        # Asegurar que siempre se guarde en la ruta que el dashboard lee
        self.ARCHIVO_JSON_DASHBOARD = recurso_path("datos/codigos_cumple.json")
        self.ARCHIVO_JSON = archivo_json  # Puede ser diferente, pero el dashboard siempre leerá de ARCHIVO_JSON_DASHBOARD
        self.df_codigos_cumple = pd.DataFrame()

        self.cargar_datos()
        self.crear_ventana()

    def cargar_datos(self):
        """Carga los datos desde Excel y JSON"""
        try:
            # Cargar Excel
            if os.path.exists(self.ARCHIVO_CODIGOS):
                self.df_codigos_cumple = pd.read_excel(self.ARCHIVO_CODIGOS, engine='openpyxl')
                # Reemplazar NaN por cadenas vacías en CRITERIO cuando OBSERVACIONES es "CUMPLE"
                mask_cumple = self.df_codigos_cumple["OBSERVACIONES"].astype(str).str.upper() == "CUMPLE"
                self.df_codigos_cumple.loc[mask_cumple, "CRITERIO"] = ""
            else:
                self.df_codigos_cumple = pd.DataFrame(columns=["ITEM", "OBSERVACIONES", "CRITERIO"])

            # Cargar JSON (opcional) - pero el dashboard siempre leerá de ARCHIVO_JSON_DASHBOARD
            if os.path.exists(self.ARCHIVO_JSON):
                with open(self.ARCHIVO_JSON, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
                    # sincronizar si quieres
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")

    def crear_ventana(self):
        self.ventana = E.nueva_ventana(self.parent, "Editor de Códigos", 980, 660, modal=False,
                                       redimensionable=True)
        self.ventana.minsize(820, 520)

        contenido = ctk.CTkFrame(self.ventana, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=26, pady=22)

        # Título
        header, self.lbl_conteo = E.encabezado(contenido, "editor", "Editor de Códigos", "")
        header.pack(fill="x", pady=(0, 16))

        # Buscador
        search_frame = E.card(contenido, corner_radius=12)
        search_frame.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(search_frame, text="", image=E.crear_icono("lupa", tam=18, circulo=False,
                     color=E.COLOR_TEXTO_TENUE)).pack(side="left", padx=(14, 6), pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar por item, observación o criterio…",
                                         font=E.fuente(12), height=36, border_width=0,
                                         fg_color=E.COLOR_CARD, text_color=E.COLOR_TEXTO)
        self.search_entry.pack(side="left", fill="x", expand=True, pady=8)

        E.boton(search_frame, "Limpiar", self.limpiar_busqueda, "secundario", width=90,
                height=32).pack(side="right", padx=(6, 10))
        E.boton(search_frame, "Buscar", self.filtrar_tabla, "primario", "lupa", width=100,
                height=32).pack(side="right")

        # Tabla con scrollbars
        table_card = E.card(contenido, corner_radius=12)
        table_card.pack(fill="both", expand=True)
        table_frame, self.tree = E.tabla(table_card, ("ITEM", "OBSERVACIONES", "CRITERIO"))
        table_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.tree.heading("ITEM", text="ITEM")
        self.tree.heading("OBSERVACIONES", text="OBSERVACIONES")
        self.tree.heading("CRITERIO", text="CRITERIO")
        self.tree.column("ITEM", width=150, anchor="center", minwidth=100)
        self.tree.column("OBSERVACIONES", width=450, anchor="w", minwidth=300)
        self.tree.column("CRITERIO", width=150, anchor="w", minwidth=100)
        self.tree.bind("<Double-1>", lambda event: self.abrir_editar_item())

        # Botones en la parte inferior
        button_frame = ctk.CTkFrame(contenido, fg_color="transparent")
        button_frame.pack(fill="x", pady=(16, 0))

        buttons_config = [
            ("Agregar item", self.abrir_agregar_item, "primario", "mas"),
            ("Editar item", self.abrir_editar_item, "primario", "editor"),
            ("Subir Excel", self.importar_excel, "primario", "subir"),
            ("Eliminar item", self.eliminar_item_principal, "peligro", "basura"),  # Rojo para indicar peligro
        ]

        for text, command, variante, icono in buttons_config:
            E.boton(button_frame, text, command, variante, icono).pack(side="left", padx=(0, 8))

        E.boton(button_frame, "Cerrar", self.ventana.destroy, "oscuro", "x", width=110).pack(side="right")

        self.actualizar_tabla()
        self.search_entry.bind("<Return>", lambda event: self.filtrar_tabla())

    def limpiar_busqueda(self):
        self.search_entry.delete(0, "end")
        self.actualizar_tabla()
        self.ventana.focus_set()

    def eliminar_item_principal(self):
        """Elimina el item seleccionado con confirmación"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Eliminar Item", "Seleccione un item de la tabla para eliminar", parent=self.ventana)
            return
        
        # Obtener el valor del ITEM seleccionado
        item_values = self.tree.item(selected[0])["values"]
        if not item_values or item_values[0] in ["No hay datos", "No se encontraron resultados"]:
            return
            
        item_id = item_values[0]
        observaciones = item_values[1]
        
        # Mostrar alerta de confirmación
        confirmacion = messagebox.askyesno(
            "⚠️ CONFIRMAR ELIMINACIÓN",
            f"¿Está seguro que desea eliminar el item?\n\n"
            f"ITEM: {item_id}\n"
            f"OBSERVACIONES: {observaciones}\n\n"
            f"Esta acción no se puede deshacer.",
            icon="warning",
            parent=self.ventana
        )
        
        if not confirmacion:
            return
        
        try:
            # Encontrar y eliminar el item del DataFrame
            mask = self.df_codigos_cumple["ITEM"].astype(str) == str(item_id)
            if mask.any():
                # Eliminar el item
                self.df_codigos_cumple = self.df_codigos_cumple[~mask]
                
                # Guardar los cambios
                self.guardar_datos()
                
                # Actualizar la tabla
                self.actualizar_tabla()
                
                messagebox.showinfo("Eliminar Item", f"Item '{item_id}' eliminado correctamente", parent=self.ventana)
            else:
                messagebox.showerror("Error", "No se pudo encontrar el item seleccionado", parent=self.ventana)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar item: {str(e)}", parent=self.ventana)

    def actualizar_tabla(self):
        """Actualiza la tabla con los datos actuales"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.lbl_conteo.configure(text=f"{len(self.df_codigos_cumple)} registros")

        if len(self.df_codigos_cumple) == 0:
            self.tree.insert("", "end", values=("No hay datos", "", ""))
            return
            
        for i, (_, row) in enumerate(self.df_codigos_cumple.iterrows()):
            # Formatear los valores para mostrar vacío en lugar de nan
            item = row["ITEM"]
            observaciones = row["OBSERVACIONES"]
            criterio = row["CRITERIO"]
            
            # Convertir a cadena y reemplazar 'nan' por vacío
            if pd.isna(criterio) or str(criterio).lower() == 'nan':
                criterio = ""
            
            self.tree.insert("", "end", values=(item, observaciones, criterio), tags=E.tag_fila(i))

    def filtrar_tabla(self):
        """Filtra la tabla por el valor de búsqueda"""
        busqueda = self.search_entry.get().strip().lower()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        if not busqueda:
            self.actualizar_tabla()
            return
            
        # Crear máscara para la búsqueda en todos los campos
        mask = (
            self.df_codigos_cumple["ITEM"].astype(str).str.lower().str.contains(busqueda) |
            self.df_codigos_cumple["OBSERVACIONES"].astype(str).str.lower().str.contains(busqueda) |
            self.df_codigos_cumple["CRITERIO"].astype(str).str.lower().str.contains(busqueda)
        )
        
        resultados = self.df_codigos_cumple[mask]
        
        self.lbl_conteo.configure(text=f"{len(resultados)} de {len(self.df_codigos_cumple)} registros")

        if len(resultados) == 0:
            self.tree.insert("", "end", values=("No se encontraron resultados", "", ""))
            return
            
        for i, (_, row) in enumerate(resultados.iterrows()):
            # Formatear los valores para mostrar vacío en lugar de nan
            item = row["ITEM"]
            observaciones = row["OBSERVACIONES"]
            criterio = row["CRITERIO"]
            
            # Convertir a cadena en lugar de nan
            if pd.isna(criterio) or str(criterio).lower() == 'nan':
                criterio = ""
            
            self.tree.insert("", "end", values=(item, observaciones, criterio), tags=E.tag_fila(i))

    def abrir_agregar_item(self):
        AgregarItem(self)

    def abrir_editar_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Editar Item", "Seleccione un item de la tabla", parent=self.ventana)
            return
        
        # Obtener el valor del ITEM seleccionado
        item_values = self.tree.item(selected[0])["values"]
        if not item_values or item_values[0] in ["No hay datos", "No se encontraron resultados"]:
            return
            
        item_id = item_values[0]
        
        # Encontrar el índice en el DataFrame
        try:
            mask = self.df_codigos_cumple["ITEM"].astype(str) == str(item_id)
            if mask.any():
                index = self.df_codigos_cumple[mask].index[0]
                EditorItem(self, index)
            else:
                messagebox.showerror("Error", "No se pudo encontrar el item seleccionado", parent=self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar item: {str(e)}", parent=self.ventana)

    def guardar_datos(self):
        """Guarda los datos a Excel y JSON (en la ruta que el dashboard lee)"""
        try:
            # Asegurarse de que los valores NaN se guarden como vacíos
            self.df_codigos_cumple["CRITERIO"] = self.df_codigos_cumple["CRITERIO"].replace({np.nan: "", "nan": ""})
            
            # Guardar en Excel (archivo original)
            self.df_codigos_cumple.to_excel(self.ARCHIVO_CODIGOS, index=False)
            
            # Crear el directorio de la ruta del dashboard si no existe
            dashboard_dir = os.path.dirname(self.ARCHIVO_JSON_DASHBOARD)
            if dashboard_dir and not os.path.exists(dashboard_dir):
                os.makedirs(dashboard_dir)

            # Guardar en JSON en la ruta que el dashboard lee (siempre absoluta)
            self.df_codigos_cumple.to_json(self.ARCHIVO_JSON_DASHBOARD, orient="records", force_ascii=False, indent=4)

            # También guardar en el JSON original si es diferente
            if self.ARCHIVO_JSON != self.ARCHIVO_JSON_DASHBOARD:
                json_dir = os.path.dirname(self.ARCHIVO_JSON)
                if json_dir and not os.path.exists(json_dir):
                    os.makedirs(json_dir)
                self.df_codigos_cumple.to_json(self.ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)

            messagebox.showinfo("Guardar", "Datos guardados correctamente. El dashboard se actualizará automáticamente.", parent=self.ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos: {str(e)}", parent=self.ventana)




    def importar_excel(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel para importar",
            filetypes=[("Excel files", "*.xlsx *.xls")],
            parent=self.ventana
        )
        if not file_path:
            return

        try:
            # --- Leer archivo Excel ---
            df_nuevo = pd.read_excel(file_path, engine='openpyxl')

            # Columnas requeridas
            columnas_requeridas = {"ITEM", "CRITERIO"}
            if not columnas_requeridas.issubset(df_nuevo.columns):
                messagebox.showerror("Error", f"El archivo Excel debe contener las columnas: {', '.join(columnas_requeridas)}", parent=self.ventana)
                return

            # Limpiar y convertir ITEM a número
            df_nuevo = df_nuevo.fillna("")
            df_nuevo["ITEM"] = (
                df_nuevo["ITEM"].astype(str)
                .str.extract(r"(\d+)")  # extrae solo números
                .astype(float)
                .astype("Int64")
            )

            # Guardar el CRITERIO original para mostrar en la columna "Obs. Nueva"
            df_nuevo["CRITERIO_ORIGINAL"] = df_nuevo["CRITERIO"].astype(str).str.strip()

            if "TIPO DE PROCESO" in df_nuevo.columns:
                # Archivo tipo reporte "TIPO DE PROCESO": la columna TIPO DE PROCESO indica
                # si el item cumple; CRITERIO trae la observación cuando no cumple.
                tipo_proceso = df_nuevo["TIPO DE PROCESO"].astype(str).str.strip().str.upper()
                es_cumple = tipo_proceso == "CUMPLE"

                df_nuevo["OBS_NEW"] = df_nuevo["CRITERIO_ORIGINAL"]
                df_nuevo.loc[es_cumple, "OBS_NEW"] = "CUMPLE"

                df_nuevo["CRIT_NEW"] = df_nuevo["OBS_NEW"].str.upper().apply(lambda x: "" if x == "CUMPLE" else "REVISADO")
                df_nuevo.loc[df_nuevo["OBS_NEW"].str.strip() == "", "CRIT_NEW"] = ""

                df_nuevo = df_nuevo[["ITEM", "OBS_NEW", "CRIT_NEW"]].copy()

                # 🔹 Filtrar filas que no traen ni observación ni estado de cumplimiento
                df_nuevo = df_nuevo[df_nuevo["OBS_NEW"].str.strip() != ""]
            else:
                # Asignar CRITERIO automáticamente para la lógica interna
                df_nuevo["CRITERIO"] = df_nuevo["CRITERIO_ORIGINAL"].str.upper()
                df_nuevo["CRITERIO"] = df_nuevo["CRITERIO"].apply(lambda x: "" if x == "CUMPLE" else "REVISADO")

                df_nuevo = df_nuevo[["ITEM", "CRITERIO_ORIGINAL", "CRITERIO"]].copy()

                # Crear columnas de salida para el treeview
                df_nuevo["OBS_NEW"] = df_nuevo["CRITERIO_ORIGINAL"]  # Obs. Nueva = el valor original del archivo
                df_nuevo["CRIT_NEW"] = df_nuevo["CRITERIO"]           # Crit. Nueva = lógica interna (REVISADO o vacío)

                # 🔹 Filtrar filas que tienen Obs. Nueva vacía
                df_nuevo = df_nuevo[df_nuevo["OBS_NEW"].str.strip() != ""]

                # 🔹 Eliminar filas donde OBS_NEW contenga "REVISADO" (de la columna CRITERIO original del archivo)
                df_nuevo = df_nuevo[~df_nuevo["OBS_NEW"].str.upper().str.contains("REVISADO", na=False)]


            # Si no hay datos existentes, importar todo
            if self.df_codigos_cumple is None or self.df_codigos_cumple.empty:
                self.df_codigos_cumple = df_nuevo.copy()
                self.actualizar_tabla()
                self.guardar_datos()
                messagebox.showinfo("Importar Excel", "Todos los datos han sido importados correctamente.", parent=self.ventana)
                return

            # Preparar datos existentes
            dict_existente = self.df_codigos_cumple.set_index("ITEM").to_dict("index")

            # Detectar cambios y nuevos items
            cambios = []
            nuevos_items = []
            actualizaciones = 0

            for _, row in df_nuevo.iterrows():
                item = row["ITEM"]
                obs_nuevo = row["OBS_NEW"]     # valor original del archivo
                crit_nuevo = row["CRIT_NEW"]   # REVISADO o vacío según la lógica

                if item in dict_existente:
                    obs_actual = dict_existente[item].get("OBSERVACIONES", "")
                    crit_actual = dict_existente[item].get("CRITERIO", "")

                    # Verificar si hay algún cambio en OBSERVACIONES o CRITERIO
                    if obs_actual != obs_nuevo or crit_actual != crit_nuevo:
                        cambios.append({
                            "item": item,
                            "obs_actual": obs_actual,
                            "crit_actual": crit_actual,
                            "obs_nuevo": obs_nuevo,
                            "crit_nuevo": crit_nuevo,
                            "tipo": "actualización"
                        })
                        actualizaciones += 1

                else:
                    cambios.append({
                        "item": item,
                        "obs_actual": "",
                        "crit_actual": "",
                        "obs_nuevo": obs_nuevo,
                        "crit_nuevo": crit_nuevo,
                        "tipo": "nuevo"
                    })
                    nuevos_items.append(item)


            # Crear ventana de revisión más compacta
            win = E.nueva_ventana(self.ventana, "Revisión de cambios - Importar Excel", 1200, 600,
                                  redimensionable=True)
            win.minsize(900, 450)

            # Frame principal
            main_frame = ctk.CTkFrame(win, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=24, pady=20)

            # Título y estadísticas
            title_frame, _ = E.encabezado(main_frame, "subir", "Revisión de cambios",
                                          "Doble clic en una celda para editarla antes de aplicar")
            title_frame.pack(fill="x", pady=(0, 12))

            stats_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            stats_frame.pack(fill="x", pady=(0, 12))

            for texto, color, fondo in ((f"Nuevos items: {len(nuevos_items)}", E.COLOR_VERDE, E.COLOR_VERDE_FONDO),
                                        (f"Actualizaciones: {actualizaciones}", E.COLOR_AZUL, E.COLOR_AZUL_FONDO)):
                ctk.CTkLabel(stats_frame, text=texto, font=E.fuente(12, "bold"), text_color=color,
                             fg_color=fondo, corner_radius=8, height=30).pack(side="left", padx=(0, 8), ipadx=10)

            # Frame para la tabla con scrollbars
            table_card = E.card(main_frame, corner_radius=12)
            table_card.pack(fill="both", expand=True)

            # Crear treeview con nombres de columnas más cortos
            cols = ("ITEM", "TIPO", "OBS_ACT", "CRIT_ACT", "OBS_NEW", "CRIT_NEW", "ACTUALIZAR")
            col_names = {
                "ITEM": "Item",
                "TIPO": "Tipo",
                "OBS_ACT": "Obs. Actual",
                "CRIT_ACT": "Crit. Actual", 
                "OBS_NEW": "Obs. Nueva",
                "CRIT_NEW": "Crit. Nueva",
                "ACTUALIZAR": "Actualizar"
            }
            
            # Definir tree como variable local dentro de esta función
            table_frame, tree = E.tabla(table_card, cols, height=12, selectmode="extended")
            table_frame.pack(fill="both", expand=True, padx=2, pady=2)
            tree.tag_configure("nuevo", background=E.COLOR_VERDE_FONDO)
            
            # Configurar columnas con autoajuste y nombres cortos
            column_configs = {
                "ITEM": {"width": 80, "minwidth": 60, "stretch": False},
                "TIPO": {"width": 90, "minwidth": 70, "stretch": False},
                "OBS_ACT": {"width": 180, "minwidth": 120, "stretch": True},
                "CRIT_ACT": {"width": 180, "minwidth": 120, "stretch": True},
                "OBS_NEW": {"width": 180, "minwidth": 120, "stretch": True},
                "CRIT_NEW": {"width": 180, "minwidth": 120, "stretch": True},
                "ACTUALIZAR": {"width": 100, "minwidth": 80, "stretch": False}
            }
            
            for col in cols:
                tree.heading(col, text=col_names[col])
                config = column_configs[col]
                tree.column(col, width=config["width"], minwidth=config["minwidth"], stretch=config["stretch"])
            
            # Insertar datos en el treeview
            for cambio in cambios:
                tipo_texto = "NUEVO" if cambio["tipo"] == "nuevo" else "ACTUAL"
                
                item_id = tree.insert("", "end", values=(
                    cambio["item"],
                    tipo_texto,
                    cambio["obs_actual"],
                    cambio["crit_actual"],
                    cambio["obs_nuevo"],
                    cambio["crit_nuevo"],
                    "Sí"  # Por defecto seleccionado
                ))

                # Aplicar color según el tipo
                if cambio["tipo"] == "nuevo":
                    tree.item(item_id, tags=("nuevo",))

            # Autoajustar columnas al contenido después de insertar datos
            def autoajustar_columnas():
                for col in cols:
                    # Obtener el ancho máximo del contenido
                    max_width = 0
                    for item in tree.get_children():
                        cell_value = tree.set(item, col)
                        width = len(str(cell_value)) * 7 + 15  # Aproximación basada en longitud
                        if width > max_width:
                            max_width = width
                    
                    # Limitar el ancho máximo para no hacer columnas demasiado grandes
                    max_width = min(max_width, 300)
                    
                    # Ajustar la columna
                    tree.column(col, width=max_width)
            
            # Llamar después de un breve retraso para que se renderice el contenido
            win.after(100, autoajustar_columnas)
            
            # Función para editar celdas
            def editar_celda(event):
                region = tree.identify("region", event.x, event.y)
                if region == "cell":
                    item = tree.identify_row(event.y)
                    column = tree.identify_column(event.x)
                    col_index = int(column.replace("#", "")) - 1
                    col_name = cols[col_index]
                    
                    # No permitir editar columnas de solo lectura
                    if col_name in ["TIPO"]:
                        return
                    
                    # Obtener coordenadas y valor actual
                    x, y, width, height = tree.bbox(item, column)
                    current_value = tree.set(item, col_name)
                    
                    # Crear widget de edición
                    if col_name == "ACTUALIZAR":
                        # Combobox para Sí/No
                        edit_widget = ttk.Combobox(tree, values=["Sí", "No"], state="readonly")
                        edit_widget.set(current_value)
                    else:
                        # Entry para texto normal
                        edit_widget = ttk.Entry(tree)
                        edit_widget.insert(0, current_value)
                    
                    edit_widget.place(x=x, y=y, width=width, height=height)
                    edit_widget.focus()
                    edit_widget.select_range(0, tk.END)
                    
                    def guardar_edicion(event=None):
                        nuevo_valor = edit_widget.get()
                        tree.set(item, col_name, nuevo_valor)
                        edit_widget.destroy()
                    
                    def cancelar_edicion(event=None):
                        edit_widget.destroy()
                    
                    edit_widget.bind("<Return>", guardar_edicion)
                    edit_widget.bind("<Escape>", cancelar_edicion)
                    edit_widget.bind("<FocusOut>", guardar_edicion)
            
            tree.bind("<Double-1>", editar_celda)
            
            # Función para alternar selección
            def toggle_selection(select_all):
                for item in tree.get_children():
                    new_val = "Sí" if select_all else "No"
                    tree.set(item, "ACTUALIZAR", new_val)
            
            # Frame de botones de selección
            selection_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            selection_frame.pack(fill="x", pady=(14, 0))

            E.boton(selection_frame, "Seleccionar todos", lambda: toggle_selection(True),
                    "secundario", "check").pack(side="left", padx=(0, 8))
            E.boton(selection_frame, "Deseleccionar todos", lambda: toggle_selection(False),
                    "secundario", "x").pack(side="left")
            
            # Función para aplicar cambios
            def aplicar_cambios():
                # Contadores para estadísticas
                aplicados_nuevos = 0
                aplicados_actualizaciones = 0
                
                # Aplicar cambios seleccionados
                for item_id in tree.get_children():
                    vals = tree.item(item_id)["values"]
                    seleccionado = vals[6]  # Columna ACTUALIZAR
                    
                    if seleccionado == "Sí":
                        item = vals[0]
                        obs_nuevo = vals[4]
                        crit_nuevo = vals[5]
                        tipo = "nuevo" if vals[1] == "NUEVO" else "actualización"
                        
                        # Actualizar el diccionario existente
                        dict_existente[item] = {"OBSERVACIONES": obs_nuevo, "CRITERIO": crit_nuevo}
                        
                        # Contar según el tipo
                        if tipo == "nuevo":
                            aplicados_nuevos += 1
                        else:
                            aplicados_actualizaciones += 1
                
                # Convertir de vuelta a DataFrame
                self.df_codigos_cumple = pd.DataFrame.from_dict(dict_existente, orient="index").reset_index()
                self.df_codigos_cumple = self.df_codigos_cumple.rename(columns={"index": "ITEM"})
                
                # Guardar los cambios (esto guardará en la ruta del dashboard)
                self.guardar_datos()
                
                # Actualizar la tabla principal
                self.actualizar_tabla()
                
                # Mostrar resumen
                resumen = f"Cambios aplicados y guardados exitosamente:\n\n• Nuevos items: {aplicados_nuevos}\n• Actualizaciones: {aplicados_actualizaciones}"
                messagebox.showinfo("Importar Excel", resumen, parent=self.ventana)

                win.destroy()

            # Botones de acción (misma fila que los de selección, a la derecha)
            E.boton(selection_frame, "Cancelar", win.destroy, "oscuro", "x",
                    width=110).pack(side="right")
            E.boton(selection_frame, "Aplicar cambios", aplicar_cambios, "primario",
                    "check").pack(side="right", padx=(0, 8))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar el Excel: {str(e)}", parent=self.ventana)




def formulario_item(ventana, titulo, subtitulo, icono, campos, comando_guardar):
    """Arma el diálogo de item: encabezado, campos (etiqueta, atributo, valor) y botones.

    Devuelve un dict {atributo: CTkEntry}.
    """
    main_frame = ctk.CTkFrame(ventana, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=26, pady=22)

    header, _ = E.encabezado(main_frame, icono, titulo, subtitulo, tam_icono=44)
    header.pack(fill="x", pady=(0, 16))

    form = E.card(main_frame, corner_radius=12)
    form.pack(fill="x")

    entradas = {}
    for label_text, attr_name, valor in campos:
        ctk.CTkLabel(form, text=label_text, font=E.fuente(12, "bold"), text_color=E.COLOR_TEXTO,
                     anchor="w").pack(fill="x", padx=18, pady=(14, 4))
        entry = ctk.CTkEntry(form, font=E.fuente(12), height=36, corner_radius=8,
                             border_color=E.COLOR_BORDE, fg_color=E.COLOR_SUPERFICIE,
                             text_color=E.COLOR_TEXTO)
        if valor:
            entry.insert(0, str(valor))
        entry.pack(fill="x", padx=18)
        entradas[attr_name] = entry
    entry.pack_configure(pady=(0, 18))  # margen inferior de la card

    btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(16, 0))
    E.boton(btn_frame, "Cancelar", ventana.destroy, "secundario", "x", width=120).pack(side="right")
    E.boton(btn_frame, "Guardar", comando_guardar, "primario", "guardar", width=120).pack(side="right", padx=(0, 8))

    primera = next(iter(entradas.values()))
    ventana.after(200, primera.focus_set)
    ventana.bind("<Return>", lambda event: comando_guardar())
    ventana.bind("<Escape>", lambda event: ventana.destroy())
    return entradas


class AgregarItem:
    def __init__(self, editor: EditorCodigos):
        self.editor = editor
        self.ventana = E.nueva_ventana(editor.ventana, "Agregar Nuevo Item", 500, 440)

        # Campos de entrada
        campos = [
            ("ITEM", "item_entry", ""),
            ("OBSERVACIONES", "obs_entry", ""),
            ("CRITERIO", "crit_entry", "")
        ]
        entradas = formulario_item(self.ventana, "Agregar nuevo item",
                                   "Registra un código con su observación y criterio",
                                   "mas", campos, self.agregar_item)
        for attr_name, entry in entradas.items():
            setattr(self, attr_name, entry)

        # 🔹 Vinculamos el evento para desactivar criterio si es "CUMPLE"
        self.obs_entry.bind("<KeyRelease>", self.verificar_observacion)

    def verificar_observacion(self, event=None):
        """Desactiva la entrada de criterio si la observación es 'CUMPLE'"""
        if self.obs_entry.get().strip().upper() == "CUMPLE":
            self.crit_entry.delete(0, tk.END)
            self.crit_entry.configure(state="disabled", fg_color=E.COLOR_GRIS)
        else:
            self.crit_entry.configure(state="normal", fg_color=E.COLOR_SUPERFICIE)

    def agregar_item(self):
        item = self.item_entry.get().strip()
        observaciones = self.obs_entry.get().strip()
        
        # Si la entrada está deshabilitada, criterio queda vacío
        if self.crit_entry.cget("state") == "disabled":
            criterio = ""
        else:
            criterio = self.crit_entry.get().strip()
        
        if not item:
            messagebox.showwarning("Advertencia", "El campo ITEM no puede estar vacío", parent=self.ventana)
            return
            
        # Verificar si el ITEM ya existe
        if item in self.editor.df_codigos_cumple["ITEM"].astype(str).values:
            messagebox.showwarning("Advertencia", f"El ITEM {item} ya existe", parent=self.ventana)
            return
            
        # Seguridad extra: si la observación es "CUMPLE", limpiar criterio
        if observaciones.upper() == "CUMPLE":
            criterio = ""
            
        nuevo = {"ITEM": item, "OBSERVACIONES": observaciones, "CRITERIO": criterio}
        self.editor.df_codigos_cumple = pd.concat(
            [self.editor.df_codigos_cumple, pd.DataFrame([nuevo])],
            ignore_index=True
        )

        # 🔹 Guardar de inmediato en Excel y JSON (incluyendo la ruta del dashboard)
        self.editor.guardar_datos()

        # Refrescar tabla y cerrar
        self.editor.actualizar_tabla()
        self.ventana.destroy()
        messagebox.showinfo("Éxito", "Item agregado y guardado correctamente", parent=self.editor.ventana)

class EditorItem:
    def __init__(self, editor: EditorCodigos, index):
        self.editor = editor
        self.index = index
        self.ventana = E.nueva_ventana(editor.ventana, "Editar Item", 500, 380)

        row = editor.df_codigos_cumple.loc[index]

        # Campos de entrada
        campos = [
            ("OBSERVACIONES", "obs_entry", self.format_value(row["OBSERVACIONES"])),
            ("CRITERIO", "crit_entry", self.format_value(row["CRITERIO"]))
        ]
        entradas = formulario_item(self.ventana, f"Editar item {row['ITEM']}",
                                   "Modifica la observación y el criterio del código",
                                   "editor", campos, self.guardar_cambios)
        for attr_name, entry in entradas.items():
            setattr(self, attr_name, entry)

    def format_value(self, value):
        """Formatea el valor para mostrar vacío en lugar de nan"""
        if pd.isna(value) or str(value).lower() == 'nan':
            return ""
        return value


    def guardar_cambios(self):
        observaciones = self.obs_entry.get().strip()
        criterio = self.crit_entry.get().strip()
        
        # Si la observación es "CUMPLE", asegurar que el criterio esté vacío
        if observaciones.upper() == "CUMPLE":
            criterio = ""
        
        self.editor.df_codigos_cumple.at[self.index, "OBSERVACIONES"] = observaciones
        self.editor.df_codigos_cumple.at[self.index, "CRITERIO"] = criterio
        
        # Guardar cambios (esto guardará en la ruta del dashboard)
        self.editor.guardar_datos()
        
        self.ventana.destroy()
        messagebox.showinfo("Éxito", "Cambios guardados correctamente", parent=self.editor.ventana)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.withdraw()
    archivo_excel = recurso_path("datos/codigos_cumple.xlsx")
    archivo_json = recurso_path("datos/codigos_cumple.json")
  # Ahora ambos apuntan al mismo archivo
    app = EditorCodigos(root, archivo_excel, archivo_json)
    app.ventana.bind("<Destroy>", lambda e: root.destroy() if e.widget is app.ventana else None)
    root.mainloop()