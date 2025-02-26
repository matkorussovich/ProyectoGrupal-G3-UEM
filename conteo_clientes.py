import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import cv2
from ultralytics import YOLO
import os
import csv
from deep_sort_realtime.deepsort_tracker import DeepSort

# Configuracion de DeepSort
CONFIDENCE_THRESHOLD = 0.6
MAX_AGE = 150  # Número de frames para mantener un track sin actualizaciones


# Cargar modelo YOLO11s fine tuneado y DeepSort.
model = YOLO(r'modelos\best.pt', verbose=False)
tracker = DeepSort(max_age=MAX_AGE, max_cosine_distance=0.3, max_iou_distance=0.6, n_init=5)

# Obtener lista de videos MP4 en la carpeta grabaciones
VIDEOS_PATH = r"grabaciones"
lista_videos = [f for f in os.listdir(VIDEOS_PATH) if f.endswith('.mp4') and 'procesado' not in f]

os.environ['YOLO_VERBOSE'] = 'False'  # Desactivar mensajes de depuración

# Crear la carpeta de salida si no existe
CSV_PATH = 'datos-salida/conteo_clientes_hora.csv'
os.makedirs("datos-salida", exist_ok=True)

# Procesar cada video
for nombre_video in lista_videos:
    cap = cv2.VideoCapture(os.path.join(VIDEOS_PATH, nombre_video))
    print("Iniciando procesamiento de", nombre_video)
    
    # Extraer la fecha y hora inicial desde el nombre del archivo
    fecha_hora_inicial_str = nombre_video.split('_')[1] + " " + nombre_video.split('_')[2].replace('.mp4', '')
    fecha_hora_inicial = datetime.strptime(fecha_hora_inicial_str, "%Y-%m-%d %H-%M-%S")
    
    unique_ids_per_hour = {}
    frame_count = 0
    FRAMES_PER_SECOND = int(cap.get(cv2.CAP_PROP_FPS))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        current_time = frame_count / FRAMES_PER_SECOND
      
        # Detección con YOLO
        yolo_results = model(frame)
        boxes = yolo_results[0].boxes
        
        # Extraer datos
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        cls = boxes.cls.cpu().numpy()
        detections = np.column_stack((xyxy, conf, cls))
        
        # Filtrar clientes (clase 0)
        customer_mask = detections[:, 5] == 0
        customer_detections = detections[customer_mask]
        
        # Preparar detecciones para DeepSORT
        converted_detections = []
        for det in customer_detections:
            x1, y1, x2, y2, conf, cls = det[:6]
            if conf >= CONFIDENCE_THRESHOLD:
                w = x2 - x1
                h = y2 - y1
                converted_detections.append(([x1, y1, w, h], conf, cls))
        
        # Actualizar tracker
        tracks = tracker.update_tracks(converted_detections, frame=frame)
        
        current_ids = set()
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            current_ids.add(track_id)
            
            # Extraer fecha y hora del nombre del video
            video_name = os.path.basename(nombre_video)
            try:
                date_str = video_name.split('_')[1] + '_' + video_name.split('_')[2].replace('.mp4', '')
                video_datetime = datetime.strptime(date_str, '%Y-%m-%d_%H-%M-%S')
            except Exception as e:
                print(f"Error al parsear fecha del video: {e}")
                video_datetime = datetime.now()  # Fallback en caso de error
            
            # Calcular el tiempo real sumando el tiempo del video
            real_time = video_datetime + timedelta(seconds=current_time)
            hour_key = real_time.strftime('%Y-%m-%d_%H:00:00')

            # Inicializar si no existe la hora
            if hour_key not in unique_ids_per_hour:
                unique_ids_per_hour[hour_key] = set()

            # Agregar ID único a la hora
            unique_ids_per_hour[hour_key].add(track_id)

    cap.release()
    
    # Procesar los conteos por hora
    results = []
    for hour_key, ids_set in unique_ids_per_hour.items():
        hour_dt = datetime.strptime(hour_key, '%Y-%m-%d_%H:%M:%S')
        results.append({
            'fecha': hour_dt.strftime('%Y-%m-%d'),
            'hora': hour_dt.strftime('%H:00'),
            'dia_semana': hour_dt.strftime('%A'),
            'clientes_unicos': len(ids_set)
        })

   
    # Crear DataFrame
    df = pd.DataFrame(results, columns=['fecha', 'hora', 'dia_semana', 'clientes_unicos'])

    # Guardar en CSV
    df.to_csv(CSV_PATH, index=False, mode='a', header=not os.path.exists(CSV_PATH))

    # Renombrar el video procesado
    os.rename(os.path.join(VIDEOS_PATH, nombre_video), os.path.join(VIDEOS_PATH, nombre_video.replace('.mp4', '_procesado.mp4')))
    print("Procesamiento de", nombre_video, "finalizado")


  
