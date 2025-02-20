
from ultralytics import YOLO

modelo = YOLO("yolo11s.pt")


from moviepy import VideoFileClip
import os

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

# Ejemplo de uso
input_video = "videos\\OneDrive_1_25-1-2025\\Clientes6.mp4"  # Ruta del video original
output_dir = "videos\\OneDrive_1_25-1-2025\\modificado"  # Carpeta para guardar el video modificado
fps = 1  # Nuevo valor de FPS

#reduce_fps(input_video, output_dir, fps)
    
   

#resultado = modelo.track(source="videos\\OneDrive_1_25-1-2025\\modificado\\Clientes6.mp4", show=True, save=True)
resultado = modelo.track(source=0, show=True, save=False)