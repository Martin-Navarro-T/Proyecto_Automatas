import re
import csv
from datetime import datetime

# Especificar las columnas que se van a leer (omitimos las últimas dos)
columnas = [
    'ID', 'ID_Sesion', 'ID_Conexión_unico', 'Usuario', 'IP_NAS_AP', 'Tipo__conexión',
    'Inicio_de_Conexión_Dia', 'Inicio_de_Conexión_Hora', 'FIN_de_Conexión_Dia', 'FIN_de_Conexión_Hora',
    'Session_Time', 'Input_Octects', 'Output_Octects', 'MAC_AP', 'MAC_Cliente',
    'Razon_de_Terminación_de_Sesión'
]

# Expresiones regulares para cada columna
regex_patterns = {
# Valida un ID que consiste en 6 a 7 dígitos donde el primer dígito no puede ser cero.
    'ID': re.compile(r"^[1-9][0-9]{5,6}$"),

# Valida un ID de sesión que puede contener 8 caracteres alfanuméricos seguidos opcionalmente por un guion medio y otros 8 caracteres alfanuméricos.
    'ID_Sesion': re.compile(r"^[A-Z\d]{8}-?[A-Z\d]{8}$"),
    
# Valida un ID de conexión único que puede ser de 16 caracteres alfanuméricos o dígitos, o solo letras minúsculas, ignorando mayúsculas.
    'ID_Conexión_unico': re.compile(r"^(?:[a-z\d]{16}|\d{16}|[a-z]{16})$"),
    
# Valida un nombre de usuario que puede contener letras, dígitos, guiones bajos, puntos y guiones, con longitud de 1 a 50 caracteres. 
    'Usuario': re.compile(r"^[\w.-][\w.-]{0,49}$"),
    
# Valida una dirección IP en formato IPv4.
    'IP_NAS_AP': re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"),

# Valida el tipo de conexión como "Wireless-802.11".
    'Tipo__conexión': re.compile(r"^Wireless-802.11$"),

# Valida una fecha en formato YYYY-MM-DD.
    'Inicio_de_Conexión_Dia': re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"),
    
# Valida una hora en formato HH:MM:SS.
    'Inicio_de_Conexión_Hora': re.compile(r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"),

# Valida una fecha de finalización de sesión en formato YYYY-MM-DD.
    'FIN_de_Conexión_Dia': re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"),

# Valida una hora de finalización de sesión en formato HH:MM:SS.
    'FIN_de_Conexión_Hora': re.compile(r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"),

# Valida un tiempo de sesión que puede ser cero o un número entero positivo.
    'Session_Time': re.compile(r"^(0|[1-9]\d*)$"),

# Valida un número entero positivo que representa octetos de entrada.
    'Input_Octects': re.compile(r"^\d+$"),

# Valida un número entero positivo que representa octetos de salida.
    'Output_Octects': re.compile(r"^\d+$"),
    
# Valida una dirección MAC en formato punto de acceso.
    'MAC_AP': re.compile(r"^([0-9A-F]{2}-){5}[0-9A-F]{2}:HCDD$"),
    # Explicación: Valida una dirección MAC de punto de acceso en un formato específico.

# Valida una dirección MAC en formato cliente.
    'MAC_Cliente': re.compile(r"^([0-9A-F]{2}-){5}[0-9A-F]{2}$"),

# Valida la razón de terminación de sesión permitiendo solo ciertos valores específicos.
    'Razon_de_Terminación_de_Sesión': re.compile(r"^(User-Request|Stale-Session|Session-Timeout|NAS-Reboot|Admin-Reboot|)$")
}


def comprobar_columnas(columna, row):
    # Itera sobre todas las columnas en la fila, excepto la última
    for i in range(len(row) - 1):
        # Verifica si el valor de la columna actual cumple con la expresión regular correspondiente a 'columna'
        if regex_patterns[columna].match(row[columnas[i]]):
            # Si hay coincidencia, asigna el valor de la columna a 'col_v' (variable global)
            global col_v
            col_v = row[columnas[i]]
            return True  # Retorna True si encuentra una coincidencia válida
    return False  # Retorna False si no encuentra ninguna coincidencia


def verificar_y_ordenar_fila(row, row_num):
    # Revisar cada valor de la fila y corregir si es necesario
    fila_corregida = {}  # Diccionario para almacenar los valores corregidos de la fila
    fila_erronea = False  # Bandera para indicar si la fila contiene errores
    
    for columna in columnas:  # Itera sobre cada columna definida en 'columnas'
        if columna in row and regex_patterns[columna].match(row[columna]):
            # Si la columna está presente en la fila y su valor coincide con la expresión regular correspondiente
            fila_corregida[columna] = row[columna]  # Asigna el valor de la columna corregida
        elif comprobar_columnas(columna, row):
            fila_corregida[columna] = col_v  # Usa el valor global 'col_v' obtenido de 'comprobar_columnas'
        else:
            # Si no se cumple la expresión regular o no se encuentra el valor correcto, maneja el error
            print(f"Error en columna '{columna}': {row.get(columna, '')}, En la linea: {row_num}")
            fila_corregida[columna] = ""  # Asigna una cadena vacía como valor de la columna corregida
            fila_erronea = True  # Marca la fila como errónea si encuentra algún error

    return fila_corregida, fila_erronea  # Retorna el diccionario de la fila corregida y la bandera de fila errónea


def analizar_csv(file_path, fecha_inicio, fecha_fin):
    archivo_temporal = 'temporal.csv' # Nombre del archivo temporal para almacenar datos procesados
    archivo_errores = 'errores.csv' # Nombre del archivo para almacenar filas con errores
    ap_trafico = {} # Diccionario para almacenar el tráfico por punto de acceso (AP)

    # Convertir fechas de inicio y fin de cadena a objetos datetime
    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

    datos_exportar = []  # Lista para almacenar los datos filtrados y corregidos

    # Abrir archivos CSV de entrada, temporal y de errores
    with open(file_path, newline='', encoding='utf-8') as csvfile, \
            open(archivo_temporal, 'w', newline='', encoding='utf-8') as temporalfile, \
            open(archivo_errores, 'a', newline='', encoding='utf-8') as errfile:

        reader = csv.DictReader(csvfile)  # Crear lector de CSV con diccionarios
        writer = csv.DictWriter(temporalfile, fieldnames=columnas + ['', ''])  # Escritor para archivo temporal
        error_writer = csv.DictWriter(errfile, fieldnames=columnas + ['', ''])  # Escritor para archivo de errores

        writer.writeheader()  # Escribir los encabezados en el archivo temporal

        # Iterar sobre cada fila del archivo CSV original
        for row_num, row in enumerate(reader, start=1):
            row, fila_erronea = verificar_y_ordenar_fila(row, row_num)  # Corregir y validar la fila

            # Convertir la fecha de conexión a un objeto datetime
            fecha_conexion_dt = datetime.strptime(row['Inicio_de_Conexión_Dia'], '%Y-%m-%d')

            # Verificar si la fecha de conexión está dentro del rango especificado
            if fecha_inicio_dt <= fecha_conexion_dt <= fecha_fin_dt:
                if not fila_erronea:  # Si la fila no contiene errores
                    ap = row['MAC_AP']  # Obtener la dirección MAC del punto de acceso (AP)
                    trafico = int(row['Input_Octects']) + int(row['Output_Octects'])  # Calcular el tráfico

                    # Actualizar el diccionario 'ap_trafico' con el tráfico acumulado por AP
                    if ap in ap_trafico:
                        ap_trafico[ap] += trafico
                    else:
                        ap_trafico[ap] = trafico

                    # Filtrar y preparar la fila para escribirla en el archivo temporal
                    filtered_row = {k: row[k] for k in columnas if k in row}
                    filtered_row.update({'': '', '': ''})  # Agregar campos adicionales (vacíos en este caso)

                    writer.writerow(filtered_row)  # Escribir la fila en el archivo temporal
                    datos_exportar.append(filtered_row)  # Agregar la fila a la lista de datos exportados
                else:
                    # Si la fila contiene errores, escribirla en el archivo de errores
                    filtered_row = {k: row[k] for k in columnas if k in row}
                    filtered_row.update({'': '', '': ''})  # Agregar campos adicionales (vacíos en este caso)
                    error_writer.writerow(filtered_row)  # Escribir la fila en el archivo de errores

    # Cerrar los archivos temporal y de errores
    temporalfile.close()
    errfile.close()

    # Preparar el resultado final con un mensaje de análisis completado y los AP con más tráfico
    resultado = "Análisis completado.\n\n"
    resultado += "AP con más tráfico en el rango de fechas especificado:\n"
    for ap, trafico in sorted(ap_trafico.items(), key=lambda item: item[1], reverse=True):
        resultado += f"{ap}: {trafico} octetos\n"

    return resultado  # Retornar el resultado final del análisis

if __name__ == "__main__":
    print(analizar_csv('datos.csv', '2022-01-01', '2022-01-31'))
