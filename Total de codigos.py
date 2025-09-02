# canvas_width = 300
        #canvas_height = 200
        #canvas = tk.Canvas(frame_graph, width=canvas_width, height=canvas_height, bg="#FFFFFF", highlightthickness=0)
        #canvas.pack() #

        # Dibujar gráfica de barras
        def dibujar_grafica():
            canvas.delete("all")
            
            # Datos para la gráfica
            datos = [
                ("Códigos", stats['total_codigos']),
                ("Catálogo", stats['total_items']),
                ("Historial", stats['total_procesos']),
                ("Archivos", stats_archivos['total_archivos']),
                ("Cumplen", stats['codigos_cumplen']) # NUEVO: Añadir códigos que cumplen
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
        
        # ... (resto de la función mostrar_estadisticas) ...

#dibujar_grafica()
#        
#        # Botones en la parte inferior
#        frame_botones = tk.Frame(ventana, bg="#FFFFFF")
#        frame_botones.pack(pady=20)