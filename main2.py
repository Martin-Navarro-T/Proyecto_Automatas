import tkinter as tk  
from tkinter import filedialog, messagebox  
from datetime import datetime 
from openpyxl import Workbook  # Para trabajar con archivos Excel
from automatas import analizar_csv  
from PIL import Image, ImageTk  # Para manejar imágenes

# Variable global para almacenar los datos a exportar
datos_exportacion = []

def convertir_fecha(fecha):
    return datetime.strptime(fecha, '%d-%m-%Y').strftime('%Y-%m-%d')

def seleccionar_archivo(entry_file):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry_file.delete(0, tk.END)  # Limpiar el campo de entrada
        entry_file.insert(0, file_path)  # Insertar la ruta del archivo seleccionado

def mostrar_resultados(resultados, text_widget):
    text_widget.config(state=tk.NORMAL)  # Habilitar el widget para permitir cambios
    text_widget.delete("1.0", tk.END)  # Limpiar texto anterior
    text_widget.insert(tk.END, resultados)  # Insertar resultados
    text_widget.config(state=tk.DISABLED)  # Deshabilitar edición

def iniciar_analisis(entry_file, entry_inicio, entry_fin, text_widget):
    global datos_exportacion
    file_path = entry_file.get()  # Obtener la ruta del archivo desde el campo de entrada
    fecha_inicio = entry_inicio.get()  # Obtener la fecha de inicio desde el campo de entrada
    fecha_fin = entry_fin.get()  # Obtener la fecha de fin desde el campo de entrada
    fecha_inicio_dt = convertir_fecha(fecha_inicio)  # Convertir la fecha de inicio al formato YYYY-MM-DD
    fecha_fin_dt = convertir_fecha(fecha_fin)  # Convertir la fecha de fin al formato YYYY-MM-DD
    
    if file_path and fecha_inicio and fecha_fin:  # Verificar que todos los campos estén completos
        try:
            resultados = analizar_csv(file_path, fecha_inicio_dt, fecha_fin_dt)  # Llamar a la función analizar_csv
            datos_exportacion = resultados  # Almacenar los datos para la exportación
            mostrar_resultados(resultados, text_widget)  # Mostrar los resultados en el widget de texto
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al analizar el archivo: {e}")  # Mostrar mensaje de error si ocurre una excepción
    else:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")  # Mostrar mensaje de error si faltan campos

def procesar_datos_exportacion(texto):
    #strip para quitar espacios y split para separar por saltos de linea
    lineas = texto.strip().split('\n')  # Dividir el texto en líneas y eliminar espacios en blanco al inicio y final
    datos = [] 
    
    for linea in lineas[1:]:  # Recorrer cada línea, omitiendo la primera que es el encabezado
        partes = linea.split(': ')
        if len(partes) == 2:
            mac_ap, octetos = partes[0], partes[1].replace(' octetos', '')  # Separar la MAC_AP y los octetos
            datos.append({'MAC_AP': mac_ap, 'Octetos': int(octetos)})  # Agregar los datos a la lista
    
    return datos  # Devolver los datos procesados como una lista de diccionarios

def exportar_a_excel():
    global datos_exportacion
    if datos_exportacion:  # Verificar si hay datos para exportar
        nombre_archivo_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])  # Obtener el nombre del archivo Excel
        if nombre_archivo_excel:
            try:
                datos_procesados = procesar_datos_exportacion(datos_exportacion)  # Procesar los datos de exportación
                libro = Workbook()  # Crear un nuevo libro de trabajo
                hoja = libro.active  # Obtener la hoja activa del libro
                hoja.title = "Datos"  # Asignar un nombre a la hoja
                
                encabezados = ['MAC_AP', 'Octetos']  # Definir los encabezados de las columnas
                hoja.append(encabezados)  # Agregar los encabezados a la primera fila
                
                for fila in datos_procesados:  # Recorrer los datos procesados
                    hoja.append([fila['MAC_AP'], fila['Octetos']])  # Agregar cada fila de datos a la hoja
                
                libro.save(nombre_archivo_excel)  # Guardar el archivo Excel
                messagebox.showinfo("Éxito", f"Datos exportados exitosamente a {nombre_archivo_excel}")  # Mostrar mensaje de éxito
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al exportar los datos: {e}")  # Mostrar mensaje de error si ocurre una excepción
        else:
            messagebox.showinfo("Cancelado", "Exportación cancelada.")  # Mostrar mensaje si se cancela la exportación
    else:
        messagebox.showerror("Error", "No hay datos disponibles para exportar. Realice el análisis primero.")  # Mostrar mensaje si no hay datos para exportar

# Función principal para configurar y ejecutar la interfaz gráfica
def main():
    root = tk.Tk()  # Crear la ventana principal de la aplicación
    root.title("Analizador de Tráfico de AP")  # Establecer el título de la ventana
    root.configure(bg="black")  # Configurar el fondo de la ventana

    # Cargar el logo de Excel
    img = Image.open("excel_logo.png")  # Abrir la imagen del logo de Excel
    img = img.resize((40, 40), Image.LANCZOS)  # Redimensionar la imagen
    excel_logo = ImageTk.PhotoImage(img)  # Crear un objeto ImageTk con la imagen redimensionada

    # Estilos para los elementos de la GUI
    entry_style = {"bg": "black", "fg": "white", "insertbackground": "white", "highlightbackground": "green", "highlightcolor": "green", "font": ("Helvetica", 10, "bold")}
    label_style = {"bg": "black", "fg": "white", "font": ("Helvetica", 10, "bold")}
    button_style = {"bg": "green", "fg": "white", "highlightbackground": "green", "highlightcolor": "green", "font": ("Helvetica", 10, "bold"), "bd": 0}

    # Función para configurar el estilo de los botones redondeados
    def round_button(button):
        button.config(borderwidth=0, relief="solid")
        button.bind("<Enter>", lambda e: button.config(relief="flat"))
        button.bind("<Leave>", lambda e: button.config(relief="solid"))
        button.config(highlightthickness=0, relief="flat", overrelief="flat")

    # Elementos de la interfaz gráfica
    tk.Label(root, text="Archivo CSV:", **label_style).grid(row=0, column=0, padx=10, pady=5)
    entry_file = tk.Entry(root, width=50, **entry_style)
    entry_file.grid(row=0, column=1, padx=10, pady=5)
    btn_file = tk.Button(root, text="Seleccionar Archivo", command=lambda: seleccionar_archivo(entry_file), **button_style)
    round_button(btn_file)
    btn_file.grid(row=0, column=2, padx=10, pady=5)

    tk.Label(root, text="Fecha de Inicio (DD-MM-YYYY):", **label_style).grid(row=1, column=0, padx=10, pady=5)
    entry_inicio = tk.Entry(root, width=20, **entry_style)
    entry_inicio.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Fecha de Fin (DD-MM-YYYY):", **label_style).grid(row=2, column=0, padx=10, pady=5)
    entry_fin = tk.Entry(root, width=20, **entry_style)
    entry_fin.grid(row=2, column=1, padx=10, pady=5)

    text_resultados = tk.Text(root, wrap=tk.WORD, width=80, height=20, **entry_style)
    text_resultados.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
    text_resultados.config(state=tk.DISABLED)  # Hacer que el widget de texto sea solo de lectura

    btn_analizar = tk.Button(root, text="Iniciar Análisis", command=lambda: iniciar_analisis(entry_file, entry_inicio, entry_fin, text_resultados), **button_style)
    round_button(btn_analizar)
    btn_analizar.grid(row=3, column=0, columnspan=3, padx=10, pady=20)

    # Agregar el logo de Excel encima del botón de exportar
    btn_exportar_logo = tk.Label(root, image=excel_logo, bg="black")
    btn_exportar_logo.image = excel_logo  # Necesario para mantener la referencia
    btn_exportar_logo.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    btn_exportar = tk.Button(root, text="Exportar a Excel", command=lambda: exportar_a_excel(), **button_style)
    round_button(btn_exportar)
    btn_exportar.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    root.mainloop()  # Ejecutar el bucle principal de la aplicación

if __name__ == "__main__":
    main()  
