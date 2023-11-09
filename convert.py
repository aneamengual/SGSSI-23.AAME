import hashlib
import time
import re
import os
import numpy as np

###############
#### LAB 4 ####
###############

def calcular_sha256(file_path):
    sha256 = hashlib.sha256()

    # Abre el archivo en modo binario para lectura
    with open(file_path, 'rb') as file:
        #Lee el archivo en bloques de 4K para la eficiencia
        for block in iter(lambda: file.read(4096), b""):
            #Actualiza el objeto hash con el bloque actual
            sha256.update(block)

    #Devuelve el resumen SHA-256 en formato hexadecimal
    return sha256.hexdigest()

def agregar_sha256_al_archivo(archivo_entrada, archivo_salida):
    #Lee los contenidos del archivo de entrada
    with open(archivo_entrada, 'r') as input_file:
        contenido_original = input_file.read()

    #Calcula el resumen SHA-256 del archivo de entrada
    resumen_sha256 = calcular_sha256(archivo_entrada)

    #Crea los contenidos para el archivo de salida
    contenido_salida = f"{contenido_original}{resumen_sha256}"

    #Escribe los contenidos en el archivo de salida
    with open(archivo_salida, 'w') as output_file:
       output_file.write(contenido_salida)

def verificar_resumen_en_archivo(archivo_original, archivo_comprobacion):
    # Lee los contenidos del archivo original
    with open(archivo_original, 'r') as original_file:
        contenido_original = original_file.read()

    # Calcula el resumen SHA-256 del archivo original
    resumen_sha256 = calcular_sha256(archivo_original)


    # Lee los contenidos del archivo de comprobación
    with open(archivo_comprobacion, 'r') as comprobacion_file:
        contenido_comprobacion = comprobacion_file.read()

    # Verifica si los contenidos coinciden
    return contenido_comprobacion.startswith(contenido_original) and contenido_comprobacion.strip().endswith(f"hex:{resumen_sha256}")

def calcular_hash_por_min(file):
    start_time = time.time()
    calcular_sha256(file)
    end_time = time.time()
    tiempo_promedio_por_ejecucion = (end_time - start_time)
    ejecuciones_por_minuto = 60 / tiempo_promedio_por_ejecucion if tiempo_promedio_por_ejecucion != 0 else 0

    print(f"Tiempo promedio por ejecución: {tiempo_promedio_por_ejecucion:.6f} segundos")
    print(f"Número aproximado de ejecuciones por minuto: {ejecuciones_por_minuto:.2f}")

#print(calcular_sha256("SGSSI-23.CB.01.txt"))
#calcular_hash_por_min("SGSSI-23.CB.01.txt")

###############
#### LAB 5 ####
###############

def calc_sha256(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode())
    return sha256.hexdigest()

def encontrar_proof(contenido_original):
    proof = 0
    while True:
        # Genera la secuencia de 8 caracteres en hexadecimal
        secuencia_hex = format(proof, '08x')

        # Concatena la secuencia de proof al contenido original
        contenido_con_proof = f"{contenido_original}{secuencia_hex}\t9f\t100"

        # Calcula el resumen SHA-256
        resumen_sha256 = calc_sha256(contenido_con_proof)
        
        # Verifica si el resumen comienza con "0"
        if resumen_sha256.startswith("0"):
            print(resumen_sha256)
            return contenido_con_proof

        # Incrementa la proof para la siguiente iteración
        proof += 1

'''
def proof_mas_larga_un_min(contenido_original, archivo_salida, tiempo_maximo=240):
    inicio_tiempo = time.time()
    proof = 0
    mejor_hash = ""
    mejor_longitud = 0
    mejor_contenido = None

    while time.time() - inicio_tiempo < tiempo_maximo:
        secuencia_hex = format(proof, '08x')
        with open(archivo_salida, 'w') as output_file:
            output_file.write(f"{contenido_original}\n{secuencia_hex}\t02a\t100")
        #contenido_con_proof = f"{contenido_original}\n{secuencia_hex}\t9f\t100"
        resumen_sha256 = calcular_sha256(archivo_salida)

        # Encuentra la longitud de la secuencia de 0s al principio del resumen
        longitud_ceros = len(resumen_sha256) - len(resumen_sha256.lstrip('0'))

        if longitud_ceros > mejor_longitud:
            mejor_longitud = longitud_ceros
            mejor_hash = resumen_sha256
            mejor_contenido = f"{contenido_original}\n{secuencia_hex}\t02a\t100"

        proof += 1

    return mejor_contenido
'''
def proof_mas_larga_un_min(contenido_original, archivo_salida, tiempo_maximo=240):
    inicio_tiempo = time.time()
    proof = 0
    mejor_hash = ""
    mejor_longitud = 0
    mejor_contenido = None

    with open(archivo_salida, 'w') as output_file:
        while time.time() - inicio_tiempo < tiempo_maximo:
            secuencia_hex = format(proof, '08x')
            output_file.seek(0)
            output_file.write(f"{contenido_original}\n{secuencia_hex}\t02a\t100")
            output_file.truncate()
            
            resumen_sha256 = calcular_sha256(archivo_salida)

            longitud_ceros = len(resumen_sha256) - len(resumen_sha256.lstrip('0'))

            if longitud_ceros > mejor_longitud:
                mejor_longitud = longitud_ceros
                mejor_hash = resumen_sha256
                mejor_contenido = f"{contenido_original}\n{secuencia_hex}\t02a\t100"

            proof += 1
        output_file.seek(0)
        output_file.write(mejor_contenido)
        output_file.truncate()

    return mejor_hash

def minar(archivo_entrada, archivo_salida):
    # Lee los contenidos del archivo de entrada
    with open(archivo_entrada, 'r') as input_file:
        contenido_original = input_file.read()

    # Encuentra una secuencia de proof
    proof_mas_larga_un_min(contenido_original, archivo_salida)


def comprobar_condiciones(archivo1, archivo2, ceros):   
    with open(archivo1, 'r') as a1, open(archivo2, 'r') as a2:
        contenido1 = a1.read()
        contenido2 = a2.read()
    ult_fila = contenido2[-15:].split("\t")

    if contenido2.startswith(contenido1):
        lineas_contenido1 = contenido1.count('\n')  # Cuenta las líneas en contenido1
        lineas_contenido2 = contenido2.count('\n')  # Cuenta las líneas en contenido2

        # Verifica que contenido2 tiene una fila más que contenido1
        if (lineas_contenido2 == lineas_contenido1 + 1 and len(ult_fila) == 3 and re.match(r'^[0-9a-f]{8}$', ult_fila[0]) and 
            re.match(r'^[0-9a-f]{2}$', ult_fila[1]) and ult_fila[2].isdigit()):
            hash_arch2 = calc_sha256(contenido2)
            if hash_arch2.startswith("0" * ceros):
                cond = True
            else:
                cond = False
        else:
            cond = False
    else:
        cond = False

    return cond




###############
#### LAB 6 ####
###############
def archivos_queCumplen_y_masCeros(archivo_entrada, directorio):   
    archivos_cumplen = []
    max_ceros = -1
    archivo_max_ceros = None

    for root, _, files in os.walk(directorio):
        for archivo in files:
            ruta_archivo = os.path.join(root, archivo)

            resumen_sha256 = calcular_sha256(ruta_archivo)
            ceros = len(resumen_sha256) - len(resumen_sha256.lstrip('0'))
            if comprobar_condiciones(archivo_entrada, ruta_archivo, ceros):
                archivos_cumplen.append(ruta_archivo)
                print(ruta_archivo)

                if ceros > max_ceros:
                    max_ceros = ceros
                    archivo_max_ceros = ruta_archivo

    return archivos_cumplen, archivo_max_ceros

def archivos_queCumplen_sorteo(archivo_entrada, directorio):    
    archivos_cumplen = []
    archivos_ceros = []
    max_ceros = -1
    archivo_elegido = None

    for root, _, files in os.walk(directorio):
        for archivo in files:
            ruta_archivo = os.path.join(root, archivo)
            resumen_sha256 = calcular_sha256(ruta_archivo)
            ceros = len(resumen_sha256) - len(resumen_sha256.lstrip('0'))
            if comprobar_condiciones(archivo_entrada, ruta_archivo, ceros):
                archivos_cumplen.append(ruta_archivo)
                archivos_ceros.append(ceros)

    probabilidades = np.array(archivos_ceros) / sum(archivos_ceros)
    archivo_elegido= np.random.choice(archivos_cumplen, p=probabilidades)

    return archivo_elegido
                          

archivo_entrada = 'SGSSI-23.CB.06.txt'
archivo_salida = 'SGSSI-23.CB.06.02a.txt'
directorio_archivos = 'SGSSI-23.S.7.2.CB.04.Candidatos.Laboratorio'


#cumplen, ganador = archivos_queCumplen_y_masCeros(archivo_entrada, directorio_archivos)
#print("Archivo escogido: " + ganador)
#print(cumplen)

#agregar_sha256_al_archivo("SGSSI-23.CB.03.txt", "comp_agregarsha.txt")
hash = minar(archivo_entrada, archivo_salida)
print(hash)
#print(calc_sha256(archivo_salida))
#print(comprobar_condiciones(archivo_entrada, archivo_salida, 7))
print("\nEl hash del archivo SGSSI-23.CB.06.02a.txt es: " + calcular_sha256(archivo_salida))


