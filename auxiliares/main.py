
from ultralytics import YOLO
from moviepy import VideoFileClip
import os
import pandas as pd


modelo = YOLO(r"modelos\best.pt")

print(modelo.names) # Nombres de las clases {0: 'cliente', 1: 'empleado'}

def reduce_fps(input_video_path, output_folder, target_fps):
    """
    Reduce la cantidad de frames por segundo (FPS) de un video y guarda el video modificado.

    Args:
        input_video_path (str): Ruta del video de entrada (.mp4).
        output_folder (str): Carpeta donde se guardará el video modificado.
        target_fps (int): Cantidad deseada de frames por segundo.

    Returns:
        str: Ruta del video modificado.
    """
    try:
        # Cargar el video
        clip = VideoFileClip(input_video_path)

        # Crear la carpeta de salida si no existe
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Generar el nombre del archivo de salida
        output_video_path = os.path.join(
            output_folder, os.path.basename(input_video_path)
        )

        # Guardar el video modificado
        clip.write_videofile(output_video_path, fps=target_fps, codec="libx264")

        print(f"Video guardado en: {output_video_path}")
        return output_video_path

    except Exception as e:
        print(f"Error al procesar el video: {e}")
        return None

# # Ejemplo de uso
input_video = "grabaciones\\recortes\\grabacion_2025-02-20_18-38-15.mp4"  # Ruta del video original
# output_dir = "videos\\OneDrive_1_25-1-2025\\modificado"  # Carpeta para guardar el video modificado
# fps = 1  # Nuevo valor de FPS

# #reduce_fps(input_video, output_dir, fps)
    

# Ejecutar tracking en un video y guardar resultados en una carpeta específica
resultados = modelo.track(input_video, persist=True, save=True, project="grabaciones", name="tracking", stream=True)

# Lista para almacenar los datos
data = []

# Recorrer los resultados obtenidos
for frame_id, resultado in enumerate(resultados):
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
df.to_csv("grabaciones/tracking/results.csv", index=False)

print("✅ CSV guardado en grabaciones/tracking/results.csv")
