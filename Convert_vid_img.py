# !pip install opencv-python
# !pip install opencv-contrib-python

import cv2
import os


def convert_video_to_images(input_video, output_folder):
    # Crea carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # abre el archivo de video
    video_capture = cv2.VideoCapture(input_video)
    success, frame = video_capture.read()
    count = 0

    # Lee cada frame y la guarda como una imagen
    while success:
        image_path = os.path.join(output_folder, f"frame_{count:04d}.jpg")  # Ajusta el formato de la imagen
        cv2.imwrite(image_path, frame)  # guarda el frame como una imagen
        success, frame = video_capture.read()  # lee el proximo frame
        count += 1

    
    video_capture.release()

# rutas de entrada y salida
input_video = r'Input_prueba/WIN_20241130_12_10_21_Pro.mp4'
output_folder = r'Prueba'

# llama a la funcion
convert_video_to_images(input_video, output_folder)