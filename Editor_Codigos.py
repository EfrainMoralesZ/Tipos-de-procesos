import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import json
import os
import numpy as np

class EditorCodigos:
    def __init__(self, parent, archivo_excel, archivo_json):
        self.parent = parent
        self.ARCHIVO_CODIGOS = archivo_excel
        self.ARCHIVO_JSON = archivo_json
        self.df_codigos_cumple = pd.DataFrame()

        self.cargar_datos()
        self.crear_ventana()

    def cargar_datos(self):
        """Carga los datos desde Excel y JSON"""
        try:
            # Cargar Excel
            if os.path.exists(self.ARCHIVO_CODIGOS):
                self.df_codigos_cumple = pd.read_excel(self.ARCHIVO_CODIGOS)
                # Reemplazar NaN por cadenas vacías en CRITERIO cuando OBSERVACIONES es "CUMPLE"
                mask_cumple = self.df_codigos_cumple["OBSERVACIONES"].astype(str).str.upper() == "CUMPLE"
                self.df_codigos_cumple.loc[mask_cumple, "CRITERIO"] = ""
            else:
                self.df_codigos_cumple = pd.DataFrame(columns=["ITEM", "OBSERVACIONES", "CRITERIO"])

            # Cargar JSON (opcional)
            if os.path.exists(self.ARCHIVO_JSON):
                with open(self.ARCHIVO_JSON, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
                    # sincronizar si quieres
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")

    def crear_ventana(self):
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("📋 Editor de Códigos")
        
        # TAMAÑO ESPECÍFICO DE LA VENTANA - 1200x600 píxeles
        ancho_ventana = 900
        alto_ventana = 600
        self.ventana.geometry(f"{ancho_ventana}x{alto_ventana}")
        
        # Hacer que la ventana no sea redimensionable
        self.ventana.resizable(False, False)
        
        self.ventana.configure(bg="#FFFFFF")
        
        # Centrar ventana
        self.centrar_ventana(ancho_ventana, alto_ventana)

        # Título con nuevo estilo
        title_frame = tk.Frame(self.ventana, bg="#FFFFFF", pady=15)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="EDITOR DE CÓDIGOS", font=("Segoe UI", 20, "bold"),
                 bg="#FFFFFF", fg="#282828").pack()

        # Buscador con mejor diseño
        search_frame = tk.Frame(self.ventana, bg="#FFFFFF", pady=15)
        search_frame.pack(fill="x", padx=20)
        
        search_inner_frame = tk.Frame(search_frame, bg="#F5F5F5", relief="solid", bd=1)
        search_inner_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(search_inner_frame, text="🔍 Buscar:", bg="#F5F5F5", fg="#282828",
                 font=("INTER", 11)).pack(side="left", padx=10)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_inner_frame, textvariable=self.search_var,
                                     font=("INTER", 11), bg="#FFFFFF", fg="#282828",
                                     relief="flat", width=50)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botones de búsqueda con nuevo color
        btn_search = tk.Button(search_inner_frame, text="Buscar", bg="#ECD925", fg="#282828",
                  font=("INTER", 9, "bold"), command=self.filtrar_tabla, relief="flat", padx=15)
        btn_search.pack(side="left", padx=5)
        
        btn_clear = tk.Button(search_inner_frame, text="Limpiar", bg="#E0E0E0", fg="#282828",
                  font=("INTER", 9), command=self.actualizar_tabla, relief="flat", padx=15)
        btn_clear.pack(side="left", padx=5)

        # Frame para tabla con scrollbars
        table_frame = tk.Frame(self.ventana, bg="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")

        # Tabla con mejor estilo
        style = ttk.Style()
        style.configure("Treeview", 
                        font=("Segoe UI", 10),
                        rowheight=25,
                        background="#FFFFFF",
                        fieldbackground="#FFFFFF",
                        foreground="#282828")
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 11, "bold"),
                        background="#ECD925",
                        foreground="#282828",
                        relief="flat")
        
        self.tree = ttk.Treeview(table_frame, columns=("ITEM", "OBSERVACIONES", "CRITERIO"), 
                                show="headings", yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        
        # Configurar columnas con anchos específicos para el nuevo tamaño
        self.tree.heading("ITEM", text="ITEM")
        self.tree.heading("OBSERVACIONES", text="OBSERVACIONES")
        self.tree.heading("CRITERIO", text="CRITERIO")
        
        # Ajustar anchos de columnas para el nuevo tamaño de ventana
        self.tree.column("ITEM", width=150, anchor="center", minwidth=100)
        self.tree.column("OBSERVACIONES", width=450, anchor="w", minwidth=300)
        self.tree.column("CRITERIO", width=150, anchor="w", minwidth=100)
        
        self.tree.pack(fill="both", expand=True)
        
        # Configurar scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)

        # Botones con nuevo color #ECD925
        button_frame = tk.Frame(self.ventana, bg="#FFFFFF", pady=15)
        button_frame.pack(fill="x", padx=20)
        
        # Botones principales
        buttons_config = [
            ("➕ Agregar Item", self.abrir_agregar_item),
            ("✏️ Editar Item", self.abrir_editar_item),
            ("📤 Subir Excel", self.importar_excel),
            # ("💾 Guardar", self.guardar_datos),
            # ("🔄 Actualizar", self.actualizar_tabla), -- 
            ("❌ Cerrar", self.ventana.destroy)
        ]
        
        for text, command in buttons_config:
            if text == "❌ Cerrar":
                btn = tk.Button(button_frame, text=text, bg="#282828", fg="#FFFFFF",
                          font=("INTER", 10, "bold"), command=command, relief="flat", padx=15, pady=8)
            else:
                btn = tk.Button(button_frame, text=text, bg="#ECD925", fg="#282828",
                          font=("INTER", 10, "bold"), command=command, relief="flat", padx=15, pady=8)
            btn.pack(side="left", padx=5)

        self.actualizar_tabla()
        
        # Bind para buscar con Enter
        self.search_entry.bind("<Return>", lambda event: self.filtrar_tabla())

    def centrar_ventana(self, ancho, alto):
        """Centra la ventana en la pantalla con el tamaño específico"""
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    def actualizar_tabla(self):
        """Actualiza la tabla con los datos actuales"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        if len(self.df_codigos_cumple) == 0:
            self.tree.insert("", "end", values=("No hay datos", "", ""))
            return
            
        for _, row in self.df_codigos_cumple.iterrows():
            # Formatear los valores para mostrar vacío en lugar de nan
            item = row["ITEM"]
            observaciones = row["OBSERVACIONES"]
            criterio = row["CRITERIO"]
            
            # Convertir a cadena y reemplazar 'nan' por vacío
            if pd.isna(criterio) or str(criterio).lower() == 'nan':
                criterio = ""
            
            self.tree.insert("", "end", values=(item, observaciones, criterio))

    def filtrar_tabla(self):
        """Filtra la tabla por el valor de búsqueda"""
        busqueda = self.search_var.get().lower()
        
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
        
        if len(resultados) == 0:
            self.tree.insert("", "end", values=("No se encontraron resultados", "", ""))
            return
            
        for _, row in resultados.iterrows():
            # Formatear los valores para mostrar vacío en lugar de nan
            item = row["ITEM"]
            observaciones = row["OBSERVACIONES"]
            criterio = row["CRITERIO"]
            
            # Convertir a cadena y reemplazar 'nan' por vacío
            if pd.isna(criterio) or str(criterio).lower() == 'nan':
                criterio = ""
            
            self.tree.insert("", "end", values=(item, observaciones, criterio))

    def abrir_agregar_item(self):
        AgregarItem(self)

    def abrir_editar_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Editar Item", "Seleccione un item de la tabla")
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
                messagebox.showerror("Error", "No se pudo encontrar el item seleccionado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar item: {str(e)}")

    def guardar_datos(self):
        """Guarda los datos a Excel y JSON"""
        try:
            # Asegurarse de que los valores NaN se guarden como vacíos
            self.df_codigos_cumple["CRITERIO"] = self.df_codigos_cumple["CRITERIO"].replace({np.nan: "", "nan": ""})
            
            self.df_codigos_cumple.to_excel(self.ARCHIVO_CODIGOS, index=False)
            self.df_codigos_cumple.to_json(self.ARCHIVO_JSON, orient="records", force_ascii=False, indent=4)
            messagebox.showinfo("Guardar", "Datos guardados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos: {str(e)}")

    def importar_excel(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        try:
            df_nuevo = pd.read_excel(file_path)

            columnas_requeridas = {"ITEM", "OBSERVACIONES", "CRITERIO"}
            if not columnas_requeridas.issubset(df_nuevo.columns):
                messagebox.showerror("Error", f"El archivo Excel debe contener las columnas: {columnas_requeridas}")
                return

            df_nuevo = df_nuevo.fillna("")
            mask_cumple = df_nuevo["OBSERVACIONES"].astype(str).str.upper() == "CUMPLE"
            df_nuevo.loc[mask_cumple, "CRITERIO"] = ""

            if self.df_codigos_cumple is None or self.df_codigos_cumple.empty:
                self.df_codigos_cumple = df_nuevo.copy()
                self.actualizar_tabla()
                return

            dict_existente = self.df_codigos_cumple.set_index("ITEM").to_dict("index")

            # --- Detectar cambios ---
            cambios = []
            for _, row in df_nuevo.iterrows():
                item = row["ITEM"]
                obs_nuevo = str(row["OBSERVACIONES"]).strip()
                crit_nuevo = str(row["CRITERIO"]).strip()

                if item in dict_existente:
                    obs_actual = dict_existente[item].get("OBSERVACIONES", "")
                    crit_actual = dict_existente[item].get("CRITERIO", "")
                    if obs_actual != obs_nuevo or crit_actual != crit_nuevo:
                        cambios.append((item, obs_actual, crit_actual, obs_nuevo, crit_nuevo))
                else:
                    cambios.append((item, "", "", obs_nuevo, crit_nuevo))

            if not cambios:
                messagebox.showinfo("Importar Excel", "No se encontraron cambios para actualizar.")
                return

            # --- Mostrar ventana de revisión ---
            win = tk.Toplevel(self.parent if hasattr(self, "parent") else None)
            win.title("Revisión de cambios")
            win.geometry("1200x600")

            cols = ("ITEM", "OBS_ACTUAL", "CRIT_ACTUAL", "OBS_NUEVO", "CRIT_NUEVO", "ACTUALIZAR")
            tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=150)

            # Insertar cambios
            for item, obs_a, crit_a, obs_n, crit_n in cambios:
                tree.insert("", "end", values=(item, obs_a, crit_a, obs_n, crit_n, "Sí"))

            tree.pack(fill="both", expand=True)

            # --- Función para editar celdas ---
            def editar_celda(event):
                seleccion = tree.selection()
                if not seleccion:
                    return
                item_id = seleccion[0]
                col = tree.identify_column(event.x)  # columna clicada
                col_num = int(col.replace("#", "")) - 1  # índice de columna

                # No permitir editar columnas "OBS_ACTUAL" ni "CRIT_ACTUAL"
                if col_num in [1, 2]:
                    return

                x, y, w, h = tree.bbox(item_id, col)
                valor_actual = tree.set(item_id, column=cols[col_num])

                entry = tk.Entry(tree)
                entry.place(x=x, y=y, width=w, height=h)
                entry.insert(0, valor_actual)
                entry.focus()

                def guardar_edicion(event):
                    nuevo_valor = entry.get()
                    tree.set(item_id, column=cols[col_num], value=nuevo_valor)
                    entry.destroy()

                entry.bind("<Return>", guardar_edicion)
                entry.bind("<FocusOut>", lambda e: entry.destroy())

            tree.bind("<Double-1>", editar_celda)

            # --- Aplicar cambios seleccionados ---
            def aplicar_cambios():
                seleccionados = tree.get_children()
                for sel in seleccionados:
                    vals = tree.item(sel)["values"]
                    item, obs_a, crit_a, obs_n, crit_n, act = vals
                    if act == "Sí":
                        dict_existente[item] = {"OBSERVACIONES": obs_n, "CRITERIO": crit_n}

                self.df_codigos_cumple = pd.DataFrame.from_dict(dict_existente, orient="index").reset_index()
                self.df_codigos_cumple = self.df_codigos_cumple.rename(columns={"index": "ITEM"})
                self.actualizar_tabla()
                win.destroy()
                messagebox.showinfo("Importar Excel", "Los cambios seleccionados fueron aplicados.")

            btn_aplicar = tk.Button(win, text="Aplicar cambios", command=aplicar_cambios,
                                    bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
            btn_aplicar.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar el Excel: {str(e)}")
class AgregarItem:
    def __init__(self, editor: EditorCodigos):
        self.editor = editor
        self.ventana = tk.Toplevel(editor.ventana)
        self.ventana.title("Agregar Nuevo Item")
        
        # TAMAÑO ESPECÍFICO PARA VENTANA DE AGREGAR
        self.ventana.geometry("500x400")
        self.ventana.resizable(False, False)
        
        self.ventana.configure(bg="#FFFFFF")
        
        # Centrar ventana
        self.ventana.transient(editor.ventana)
        self.ventana.grab_set()
        
        self.centrar_ventana()

        # Frame principal
        main_frame = tk.Frame(self.ventana, bg="#FFFFFF", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="AGREGAR NUEVO ITEM", font=("Segoe UI", 14, "bold"),
                 bg="#FFFFFF", fg="#282828").pack(pady=10)

        # Campos de entrada
        campos = [
            ("ITEM:", "item_entry"),
            ("OBSERVACIONES:", "obs_entry"),
            ("CRITERIO:", "crit_entry")
        ]
        
        for label_text, attr_name in campos:
            frame = tk.Frame(main_frame, bg="#FFFFFF")
            frame.pack(fill="x", pady=8)
            
            tk.Label(frame, text=label_text, bg="#FFFFFF", fg="#282828",
                     font=("Segoe UI", 10)).pack(anchor="w")
            
            entry = tk.Entry(frame, font=("Segoe UI", 10), bg="#FFFFFF", 
                            fg="#282828", relief="solid", bd=1)
            entry.pack(fill="x", pady=5)
            
            setattr(self, attr_name, entry)

        # Botón guardar
        btn_frame = tk.Frame(main_frame, bg="#FFFFFF")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar", bg="#ECD925", fg="#282828",
                  font=("Segoe UI", 10, "bold"), command=self.agregar_item,
                  relief="flat", padx=20, pady=8).pack(side="left", padx=10)
                  
        tk.Button(btn_frame, text="❌ Cancelar", bg="#E0E0E0", fg="#282828",
                  font=("Segoe UI", 10), command=self.ventana.destroy,
                  relief="flat", padx=20, pady=8).pack(side="left", padx=10)

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f'+{x}+{y}')

    def agregar_item(self):
        item = self.item_entry.get().strip()
        observaciones = self.obs_entry.get().strip()
        criterio = self.crit_entry.get().strip()
        
        if not item:
            messagebox.showwarning("Advertencia", "El campo ITEM no puede estar vacío")
            return
            
        # Verificar si el ITEM ya existe
        if item in self.editor.df_codigos_cumple["ITEM"].astype(str).values:
            messagebox.showwarning("Advertencia", f"El ITEM {item} ya existe")
            return
            
        # Si la observación es "CUMPLE", asegurar que el criterio esté vacío
        if observaciones.upper() == "CUMPLE":
            criterio = ""
            
        nuevo = {"ITEM": item, "OBSERVACIONES": observaciones, "CRITERIO": criterio}
        self.editor.df_codigos_cumple = pd.concat([self.editor.df_codigos_cumple, pd.DataFrame([nuevo])],
                                                  ignore_index=True)
        self.editor.actualizar_tabla()
        self.ventana.destroy()
        messagebox.showinfo("Éxito", "Item agregado correctamente")
class EditorItem:
    def __init__(self, editor: EditorCodigos, index):
        self.editor = editor
        self.index = index
        self.ventana = tk.Toplevel(editor.ventana)
        self.ventana.title(f"Editar Item")
        
        # TAMAÑO ESPECÍFICO PARA VENTANA DE EDITAR
        self.ventana.geometry("500x400")
        self.ventana.resizable(False, False)
        
        self.ventana.configure(bg="#FFFFFF")
        
        # Centrar ventana
        self.ventana.transient(editor.ventana)
        self.ventana.grab_set()
        
        self.centrar_ventana()

        row = editor.df_codigos_cumple.iloc[index]

        # Frame principal
        main_frame = tk.Frame(self.ventana, bg="#FFFFFF", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text=f"EDITAR ITEM: {row['ITEM']}", font=("Segoe UI", 14, "bold"),
                 bg="#FFFFFF", fg="#282828").pack(pady=10)

        # Campos de entrada
        campos = [
            ("OBSERVACIONES:", "obs_entry", row["OBSERVACIONES"]),
            ("CRITERIO:", "crit_entry", self.format_value(row["CRITERIO"]))
        ]
        
        for label_text, attr_name, value in campos:
            frame = tk.Frame(main_frame, bg="#FFFFFF")
            frame.pack(fill="x", pady=8)
            
            tk.Label(frame, text=label_text, bg="#FFFFFF", fg="#282828",
                     font=("Segoe UI", 10)).pack(anchor="w")
            
            entry = tk.Entry(frame, font=("Segoe UI", 10), bg="#FFFFFF", 
                            fg="#282828", relief="solid", bd=1)
            entry.insert(0, value)
            entry.pack(fill="x", pady=5)
            
            setattr(self, attr_name, entry)

        # Botones
        btn_frame = tk.Frame(main_frame, bg="#FFFFFF")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar", bg="#ECD925", fg="#282828",
                  font=("Segoe UI", 10, "bold"), command=self.guardar_cambios,
                  relief="flat", padx=20, pady=8).pack(side="left", padx=10)
                  
        tk.Button(btn_frame, text="❌ Cancelar", bg="#E0E0E0", fg="#282828",
                  font=("Segoe UI", 10), command=self.ventana.destroy,
                  relief="flat", padx=20, pady=8).pack(side="left", padx=10)

    def format_value(self, value):
        """Formatea el valor para mostrar vacío en lugar de nan"""
        if pd.isna(value) or str(value).lower() == 'nan':
            return ""
        return value

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f'+{x}+{y}')

    def guardar_cambios(self):
        observaciones = self.obs_entry.get().strip()
        criterio = self.crit_entry.get().strip()
        
        # Si la observación es "CUMPLE", asegurar que el criterio esté vacío
        if observaciones.upper() == "CUMPLE":
            criterio = ""
        
        self.editor.df_codigos_cumple.at[self.index, "OBSERVACIONES"] = observaciones
        self.editor.df_codigos_cumple.at[self.index, "CRITERIO"] = criterio
        
        self.editor.actualizar_tabla()
        self.ventana.destroy()
        messagebox.showinfo("Éxito", "Cambios guardados correctamente")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    archivo_excel = "codigos_cumple.xlsx"
    archivo_json = "resources/codigos_cumple.json"
    app = EditorCodigos(root, archivo_excel, archivo_json)
    root.mainloop()