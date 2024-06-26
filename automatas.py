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
    'ID': re.compile(r"^[1-9][0-9]{5,6}$"),
    'ID_Sesion': re.compile(r"^[A-Z\d]{8}-?[A-Z\d]{8}$"),
    'ID_Conexión_unico': re.compile(r"^(?:[a-z\d]{16}|\d{16}|[a-z]{16})$"),
    'Usuario': re.compile(r"^[\w.-][\w.-]{0,49}$"),
    'IP_NAS_AP': re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"),
    'Tipo__conexión': re.compile(r"^Wireless-802.11$"),
    'Inicio_de_Conexión_Dia': re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"),
    'Inicio_de_Conexión_Hora': re.compile(r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"),
    'FIN_de_Conexión_Dia': re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"),
    'FIN_de_Conexión_Hora': re.compile(r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"),
    'Session_Time': re.compile(r"^(0|[1-9]\d*)$"),
    'Input_Octects': re.compile(r"^\d+$"),
    'Output_Octects': re.compile(r"^\d+$"),
    'MAC_AP': re.compile(r"^([0-9A-F]{2}-){5}[0-9A-F]{2}:HCDD$"),
    'MAC_Cliente': re.compile(r"^([0-9A-F]{2}-){5}[0-9A-F]{2}$"),
    'Razon_de_Terminación_de_Sesión': re.compile(r"^(User-Request|Stale-Session|Session-Timeout|NAS-Reboot|Admin-Reboot|)$")
}

def comprobar_columnas(columna, row):
    for i in range(len(row) - 1):
        if regex_patterns[columna].match(row[columnas[i]]):
            global col_v
            col_v = row[columnas[i]]
            return True
    return False

def verificar_y_ordenar_fila(row, row_num):
    # Revisar cada valor de la fila y corregir si es necesario
    fila_corregida = {}
    fila_erronea = False
    for columna in columnas:
        if columna in row and regex_patterns[columna].match(row[columna]):
            fila_corregida[columna] = row[columna]
        elif comprobar_columnas(columna, row):
            fila_corregida[columna] = col_v
        else:
            print(f"Error en columna '{columna}': {row.get(columna, '')}, En la linea: {row_num}")
            fila_corregida[columna] = ""
            fila_erronea = True

    return fila_corregida, fila_erronea

def analizar_csv(file_path, fecha_inicio, fecha_fin):
    archivo_temporal = 'temporal.csv'
    archivo_errores = 'errores.csv'
    ap_trafico = {}

    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

    datos_exportar = []

    with open(file_path, newline='', encoding='utf-8') as csvfile, \
            open(archivo_temporal, 'w', newline='', encoding='utf-8') as temporalfile, \
            open(archivo_errores, 'a', newline='', encoding='utf-8') as errfile:  # Abrir en modo 'a' para añadir

        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(temporalfile, fieldnames=columnas + ['', ''])
        error_writer = csv.DictWriter(errfile, fieldnames=columnas + ['', ''])

        writer.writeheader()  # Escribir los encabezados en el archivo temporal
        # No escribimos los encabezados en errores.csv porque ya están escritos

        for row_num, row in enumerate(reader, start=1):
            row, fila_erronea = verificar_y_ordenar_fila(row, row_num)

            # Filtrar por fecha de conexión
            fecha_conexion_dt = datetime.strptime(row['Inicio_de_Conexión_Dia'], '%Y-%m-%d')
            if fecha_inicio_dt <= fecha_conexion_dt <= fecha_fin_dt:
                if not fila_erronea:
                    ap = row['MAC_AP']
                    trafico = int(row['Input_Octects']) + int(row['Output_Octects'])
                    if ap in ap_trafico:
                        ap_trafico[ap] += trafico
                    else:
                        ap_trafico[ap] = trafico

                    # Crear fila con campos vacíos al final
                    filtered_row = {k: row[k] for k in columnas if k in row}
                    filtered_row.update({'': '', '': ''})

                    # Escribir la fila en el archivo temporal
                    writer.writerow(filtered_row)
                    datos_exportar.append(filtered_row)
                else:
                    # Escribir la fila errónea en el archivo de errores
                    filtered_row = {k: row[k] for k in columnas if k in row}
                    filtered_row.update({'': '', '': ''})
                    error_writer.writerow(filtered_row)

    # No reemplazar el archivo original con el archivo temporal, solo cerrar los archivos
    temporalfile.close()
    errfile.close()

    # Preparar el resultado a retornar
    resultado = "Análisis completado.\n\n"
    resultado += "AP con más tráfico en el rango de fechas especificado:\n"
    for ap, trafico in sorted(ap_trafico.items(), key=lambda item: item[1], reverse=True):
        resultado += f"{ap}: {trafico} octetos\n"
    return resultado

if __name__ == "__main__":
    print(analizar_csv('datos.csv', '2022-01-01', '2022-01-31'))
