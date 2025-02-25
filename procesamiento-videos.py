import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import cv2
from ultralytics import YOLO
import os
import csv

# Cargar modelo YOLO11s fine tuneado.
model = YOLO(r'modelos\best.pt', verbose=False)

# Obtener lista de videos MP4 en la carpeta grabaciones
videos_path = r"grabaciones"
lista_videos = [f for f in os.listdir(videos_path) if f.endswith('.mp4') and 'procesado' not in f]

os.environ['YOLO_VERBOSE'] = 'False'  # Desactivar mensajes de depuración

# Crear la carpeta de salida si no existe
os.makedirs("datos-salida", exist_ok=True)

# Definir las coordenadas de la línea del mostrador (inicio y fin)
x1_mostrador, y1_mostrador = 199, 115
x2_mostrador, y2_mostrador = 424, 285

# Función para calcular la distancia entre un punto (px, py) y una línea definida por dos puntos (x1, y1) y (x2, y2)
def distancia_punto_linea(px, py, x1, y1, x2, y2):
    """
    Calcula la distancia entre un punto (px, py) y una línea definida por dos puntos (x1, y1) y (x2, y2).
    
    Parámetros:
    - px, py: Coordenadas del punto.
    - x1, y1, x2, y2: Coordenadas de los puntos que definen la línea.
    
    Retorna:
    - Distancia entre el punto y la línea.
    """
    return abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / np.sqrt((y2 - y1)**2 + (x2 - x1)**2)

# Función para contar los clientes cerca de la línea del mostrador
def contar_clientes_linea(detecciones, x1_mostrador, y1_mostrador, x2_mostrador, y2_mostrador):
    count = 0
    clientes_detectados = []  # Lista para almacenar las coordenadas de los clientes detectados
    for deteccion in detecciones:
        bbox = deteccion.xywh[0]
        x, y = bbox[0].item(), bbox[1].item()  # Centro en formato xywh
        clase = int(deteccion.cls[0].item())

        # Clase 0: Cliente. Clase 1: Empleado
        if clase == 0:
            distancia = distancia_punto_linea(x, y, x1_mostrador, y1_mostrador, x2_mostrador, y2_mostrador)
            if distancia < 30:  # Umbral para considerar que está en la zona del mostrador
                count += 1
            clientes_detectados.append((x, y))  # Guardar la coordenada de los clientes
    return count, clientes_detectados

# Procesar cada video
for nombre_video in lista_videos:
    video = cv2.VideoCapture(os.path.join(videos_path, nombre_video))
    print("Iniciando procesamiento de",nombre_video)  

    # Lista para almacenar los resultados
    resultados = []

    # Lista para almacenar los resultados de detección con clientes totales
    resultados_clientes_totales = []

    # Extraer la fecha y hora inicial desde el nombre del archivo
    fecha_hora_inicial_str = nombre_video.split('_')[1] + " " + nombre_video.split('_')[2].replace('.mp4', '')
    fecha_hora_inicial = datetime.strptime(fecha_hora_inicial_str, "%Y-%m-%d %H-%M-%S")

    # Abrir el archivo CSV en modo de escritura continua
    nombre_csv = nombre_video.replace('.mp4', '')
    with open(f'datos-salida/{nombre_csv}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Escribir la cabecera del CSV
        writer.writerow(['fecha_hora', 'clientes_mostrador', 'clientes_totales', 'x_cliente', 'y_cliente', 'empleados_totales'])

        # Procesar cada fotograma
        while True:
            ret, frame = video.read()
            if not ret:
                break

            # Obtener el número de fotograma y calcular el tiempo en segundos
            frame_number = int(video.get(cv2.CAP_PROP_POS_FRAMES))
            fps = video.get(cv2.CAP_PROP_FPS)
            segundos_transcurridos = frame_number / fps

            # Calcular la nueva fecha y hora
            nueva_fecha_hora = fecha_hora_inicial + timedelta(seconds=segundos_transcurridos)
            fecha_hora_exacta = nueva_fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

            # Realizar la detección de objetos (clientes y empleados)
            resultados_deteccion = model(frame, verbose=False)

            # Extraer las detecciones
            detecciones = resultados_deteccion[0].boxes if resultados_deteccion else []

            # Contar clientes cerca del mostrador y obtener sus coordenadas
            clientes_mostrador, clientes_detectados = contar_clientes_linea(detecciones, x1_mostrador, y1_mostrador, x2_mostrador, y2_mostrador)

            # Contar todos los clientes detectados en el fotograma
            clientes_totales = sum(1 for deteccion in detecciones if int(deteccion.cls[0].item()) == 0)  # Suponiendo que 0 es la clase "cliente"

            # Contar los empleados
            empleados_totales = sum(1 for deteccion in detecciones if int(deteccion.cls[0].item()) == 1)  # Suponiendo que 1 es la clase "empleado"

            # Guardar la información del primer cliente detectado (si hay alguno)
            x_cliente, y_cliente = (None, None) if not clientes_detectados else clientes_detectados[0]

            # Escribir la fila en el CSV
            writer.writerow([fecha_hora_exacta, clientes_mostrador, clientes_totales, x_cliente, y_cliente, empleados_totales])

    # Liberar el video y cerrar ventanas
    video.release()
    cv2.destroyAllWindows()

    # Mostrar mensaje de finalización
    print("Procesamiento de",nombre_video,"finalizado")

    # Renombrar el video para evitar procesarlo nuevamente
    os.rename(os.path.join(videos_path, nombre_video), os.path.join(videos_path, nombre_video.replace('.mp4', '_procesado.mp4')))