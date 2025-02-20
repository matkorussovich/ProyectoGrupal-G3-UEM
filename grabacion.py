import cv2
import subprocess
import numpy as np
import time
import os
import signal
from datetime import datetime
from camara import CameraManager
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Inicializar la clase CameraManager
camera_manager = CameraManager(
    login_url="https://api-smart.prosegur.cloud/smart-server/ws/access/login",
    play_url=os.getenv("play_url"),
    username=os.getenv("user"),
    password=os.getenv("password"),
)

# Autenticar y obtener link de streaming
camera_manager.authenticate()
video_url = camera_manager.get_streaming_link()

# Crear carpeta de grabaciones si no existe
if not os.path.exists("grabaciones"):
    os.makedirs("grabaciones")

# Variables de control
grabando = True
fps = 10
frame_size = (640, 360)

# Función para iniciar FFmpeg
def start_ffmpeg_process(url):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", url,
        "-vf", "scale=640:360",
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-an",
        "-r", str(fps),
        "-hide_banner",
        "-loglevel", "error",
        "pipe:1"
    ]
    return subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**9)

# Manejo de interrupción (Ctrl + C)
def signal_handler(sig, frame):
    global grabando
    print("\nInterrupción detectada. Finalizando grabación...")
    grabando = False

signal.signal(signal.SIGINT, signal_handler)

# Iniciar grabación
process = start_ffmpeg_process(video_url)
inicio_grabacion = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nombre_archivo = f"grabaciones/grabacion_{inicio_grabacion}.mp4"
video_writer = cv2.VideoWriter(nombre_archivo, cv2.VideoWriter_fourcc(*"mp4v"), fps, frame_size)

print(f"Grabando en: {nombre_archivo}")

tiempo_inicio = time.time()

try:
    while grabando:
        raw_frame = process.stdout.read(640 * 360 * 3)
        if len(raw_frame) != 640 * 360 * 3:
            print("Error al leer el frame, terminando...")
            break

        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((360, 640, 3))
        video_writer.write(frame)

        # Verificar si ya pasó 1 hora (3600 segundos)
        if time.time() - tiempo_inicio >= 3600:
            video_writer.release()
            inicio_grabacion = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_archivo = f"grabaciones/grabacion_{inicio_grabacion}.mp4"
            video_writer = cv2.VideoWriter(nombre_archivo, cv2.VideoWriter_fourcc(*"mp4v"), fps, frame_size)
            print(f"Nuevo archivo iniciado: {nombre_archivo}")
            tiempo_inicio = time.time()

except Exception as e:
    print(f"Error: {e}")

finally:
    print("Finalizando grabación...")
    video_writer.release()
    process.kill()
    print("Grabación terminada.")
