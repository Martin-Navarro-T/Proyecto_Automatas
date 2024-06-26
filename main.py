import re
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from openpyxl import Workbook
from automatas import analizar_csv
from PIL import Image, ImageTk  # Necesario para manejar el logo de Excel

# Variable global para almacenar los datos a exportar
datos_exportacion = []

# Función para convertir fechas de DD-MM-YYYY a YYYY-MM-DD
def convertir_fecha(fecha):
    return datetime.strptime(fecha, '%d-%m-%Y').strftime('%Y-%m-%d')

def seleccionar_archivo(entry_file):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def mostrar_resultados(resultados, text_widget):
    text_widget.config(state=tk.NORMAL)  # Habilitar para permitir cambios
    text_widget.delete("1.0", tk.END)  # Limpiar texto anterior
    text_widget.insert(tk.END, resultados)  # Insertar resultados
    text_widget.config(state=tk.DISABLED)  # Deshabilitar edición

def iniciar_analisis(entry_file, entry_inicio, entry_fin, text_widget):
    global datos_exportacion
    file_path = entry_file.get()
    fecha_inicio = entry_inicio.get()
    fecha_fin = entry_fin.get()
    fecha_inicio_dt = convertir_fecha(fecha_inicio)
    fecha_fin_dt = convertir_fecha(fecha_fin)
    
    if file_path and fecha_inicio and fecha_fin:
        try:
            resultados = analizar_csv(file_path, fecha_inicio_dt, fecha_fin_dt)
            datos_exportacion = resultados  # Almacenar los datos para la exportación
            mostrar_resultados(resultados, text_widget)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al analizar el archivo: {e}")
    else:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")

def procesar_datos_exportacion(texto):
    lineas = texto.strip().split('\n')
    datos = []
    
    for linea in lineas[1:]:  # Omitir la primera línea que es el encabezado
        partes = linea.split(': ')
        if len(partes) == 2:
            mac_ap, octetos = partes[0], partes[1].replace(' octetos', '')
            datos.append({'MAC_AP': mac_ap, 'Octetos': int(octetos)})
    
    return datos

def exportar_a_excel():
    global datos_exportacion
    if datos_exportacion:
        nombre_archivo_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if nombre_archivo_excel:
            try:
                # Procesar los datos de exportación
                datos_procesados = procesar_datos_exportacion(datos_exportacion)
                
                # Crear un libro de trabajo y una hoja
                libro = Workbook()
                hoja = libro.active
                hoja.title = "Datos"
                
                # Agregar los encabezados
                encabezados = ['MAC_AP', 'Octetos']
                hoja.append(encabezados)

                # Agregar las filas de datos
                for fila in datos_procesados:
                    hoja.append([fila['MAC_AP'], fila['Octetos']])

                # Guardar el archivo Excel
                libro.save(nombre_archivo_excel)
                messagebox.showinfo("Éxito", f"Datos exportados exitosamente a {nombre_archivo_excel}")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al exportar los datos: {e}")
        else:
            messagebox.showinfo("Cancelado", "Exportación cancelada.")
    else:
        messagebox.showerror("Error", "No hay datos disponibles para exportar. Realice el análisis primero.")

def main():
    root = tk.Tk()
    root.title("Analizador de Tráfico de AP")
    root.configure(bg="black")

    # Cargar el logo de Excel
    img = Image.open("excel_logo.png")
    img = img.resize((40, 40), Image.LANCZOS)
    excel_logo = ImageTk.PhotoImage(img)

    # Estilos
    entry_style = {"bg": "black", "fg": "white", "insertbackground": "white", "highlightbackground": "green", "highlightcolor": "green", "font": ("Helvetica", 10, "bold")}
    label_style = {"bg": "black", "fg": "white", "font": ("Helvetica", 10, "bold")}
    button_style = {"bg": "green", "fg": "white", "highlightbackground": "green", "highlightcolor": "green", "font": ("Helvetica", 10, "bold"), "bd": 0}

    def round_button(button):
        button.config(borderwidth=0, relief="solid")
        button.bind("<Enter>", lambda e: button.config(relief="flat"))
        button.bind("<Leave>", lambda e: button.config(relief="solid"))
        button.config(highlightthickness=0, relief="flat", overrelief="flat")

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

    # Agregar logo de Excel encima del botón de exportar
    btn_exportar_logo = tk.Label(root, image=excel_logo, bg="black")
    btn_exportar_logo.image = excel_logo  # Necesario para mantener la referencia
    btn_exportar_logo.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    btn_exportar = tk.Button(root, text="Exportar a Excel", command=lambda: exportar_a_excel(), **button_style)
    round_button(btn_exportar)
    btn_exportar.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
