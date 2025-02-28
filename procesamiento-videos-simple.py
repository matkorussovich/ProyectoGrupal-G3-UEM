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
videos_path = r"grabaciones\seleccion-presentacion"

lista_videos = [f for f in os.listdir(videos_path) if f.endswith('.mp4') and 'procesado' not in f]

os.environ['YOLO_VERBOSE'] = 'False'  # Desactivar mensajes de depuración

# Crear la carpeta de salida si no existe
os.makedirs("grabaciones/Salida/csv", exist_ok=True)

# Procesar cada video
for nombre_video in lista_videos:

    print("Iniciando procesamiento de",nombre_video)  

    # Extraer la fecha y hora inicial desde el nombre del archivo
    fecha_hora_inicial_str = nombre_video.split('_')[1] + " " + nombre_video.split('_')[2].replace('.mp4', '')
    fecha_hora_inicial = datetime.strptime(fecha_hora_inicial_str, "%Y-%m-%d %H-%M-%S")

    nombre_csv = nombre_video.replace('.mp4', '')

    resultado = model.track(os.path.join(videos_path, nombre_video), persist=True, save=True, project="grabaciones/Salida", name = nombre_video, stream=True)

    # Lista para almacenar los datos
    data = []

    # Recorrer los resultados obtenidos
    for frame_id, resultado in enumerate(resultado):
        if resultado.boxes is not None:
            boxes = resultado.boxes.xyxy.cpu().numpy()  # Coordenadas (x1, y1, x2, y2)
            confidences = resultado.boxes.conf.cpu().numpy()  # Confianza de la detección
            class_ids = resultado.boxes.cls.cpu().numpy()  # ID de la clase detectada
            track_ids = resultado.boxes.id.cpu().numpy() if resultado.boxes.id is not None else [-1] * len(boxes)

            # Guardar cada detección en la lista
            for i in range(len(boxes)):
                data.append([frame_id, track_ids[i], class_ids[i], confidences[i], *boxes[i]])

    # Crear un DataFrame y guardarlo en un CSV
    df = pd.DataFrame(data, columns=["frame", "track_id", "class_id", "confidence", "x1", "y1", "x2", "y2"])
    df.to_csv(f"grabaciones/Salida/csv/{nombre_csv}.csv", index=False)

    print(f"✅ CSV guardado en grabaciones/Salida/csv/{nombre_csv}.csv")