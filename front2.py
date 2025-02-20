import cv2
import subprocess
import numpy as np
import time
import streamlit as st
from ultralytics import YOLO
from camara import CameraManager
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv()

# Inicializar la clase CameraManager
camera_manager = CameraManager(
    login_url = "https://api-smart.prosegur.cloud/smart-server/ws/access/login",
    play_url = os.getenv("play_url"),
    username = os.getenv("user"),
    password = os.getenv("password"),
)

# Autenticar el acceso a la página de Movistar Prosegur
camera_manager.authenticate()

# Obtener el link de streaming de la camara
link = camera_manager.get_streaming_link()

# Configuración de Streamlit
st.title("Proyecto Grupal - Universidad Europea")
st.write("Selecciona la cámara que deseas ver:")

# URLs de las cámaras
camera_urls = {
    "Canal": link,
    "Menendez Pelayo": "https://ca147.cameramanager.com/stream/hls/getPlaylist?access_token=d4c55ed6-4a82-48aa-9aaa-88d7aa8405c1:10008&camera_id=3049621"
    }

# Widget para seleccionar la cámara
selected_camera = st.selectbox("Elige una cámara:", list(camera_urls.keys()))

# Obtener la URL de la cámara seleccionada
video_url = camera_urls[selected_camera]

# Espacio reservado para el video
video_placeholder = st.empty()

# Botón para activar/desactivar YOLO
if "yolo_active" not in st.session_state:
    st.session_state.yolo_active = False  # Estado inicial: YOLO desactivado

if st.button("Activar/Desactivar YOLO"):
    st.session_state.yolo_active = not st.session_state.yolo_active  # Alternar estado

st.write(f"YOLO está {'activado' if st.session_state.yolo_active else 'desactivado'}.")

# Cargar el modelo YOLO
modelo = YOLO("modelos/fine-tune-ultimo.pt")  # Asegúrate de tener el archivo "yolo11s.pt" en el directorio correcto

# Función para iniciar el proceso de FFmpeg
def start_ffmpeg_process(url):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", url,
        "-vf", "scale=640:360",  # Reducir la resolución
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-an",  # No necesitamos audio
        "-r", "10",  # Limitar la velocidad de lectura a 10 FPS
        "-hide_banner",
        "-loglevel", "error",
        "pipe:1"
    ]
    return subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**9)

# Iniciar el proceso de FFmpeg
process = start_ffmpeg_process(video_url)

try:
    # Bucle para leer y mostrar los frames
    while True:
        raw_frame = process.stdout.read(640 * 360 * 3)  # Leer un frame
        if len(raw_frame) != 640 * 360 * 3:
            st.warning("No se pudo leer el frame completo. Saliendo...")
            break

        # Convertir el frame a una imagen OpenCV
        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((360, 640, 3))

        # Procesar el frame con YOLO si está activado
        if st.session_state.yolo_active:
            resultados = modelo.track(frame, persist=True)  # Usar persist=True para seguimiento entre frames
            frame_procesado = resultados[0].plot()  # Obtener el frame con las detecciones dibujadas
        else:
            frame_procesado = frame  # Mostrar el frame sin procesar

        # Convertir el frame de BGR a RGB (Streamlit usa RGB)
        frame_rgb = cv2.cvtColor(frame_procesado, cv2.COLOR_BGR2RGB)

        # Mostrar el frame en Streamlit
        video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        # Controlar la velocidad de actualización
        time.sleep(1 / 10)  # 10 FPS

except Exception as e:
    st.error(f"Ocurrió un error: {e}")

finally:
    # Asegurarse de matar el proceso y liberar recursos
    if process.poll() is None:
        process.kill()