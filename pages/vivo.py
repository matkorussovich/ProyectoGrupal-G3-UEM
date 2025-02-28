import streamlit as st
import cv2
import subprocess
import numpy as np
import time
import streamlit as st
from ultralytics import YOLO
from dotenv import load_dotenv
import os
from camara import CameraManager
from collections import deque
import time
import pandas as pd

def show_vivo():

    st.write(
        """
        ## Empanadas Tita de Buenos Aires 🥟

        Video en vivo de la tienda de la Calle de Bravo Murillo, 43, Madrid, España.
        """
    )

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

    # Defino las columnas
    col1, col2 = st.columns(2)

    with col1:

           # Estado inicial de YOLO en session_state
        if "yolo_active" not in st.session_state:
            st.session_state.yolo_active = False  

        on = st.toggle("Activar procesamiento con modelo Yolo", value=st.session_state.yolo_active, key="yolo_toggle")
        
        # Espacio reservado para el video
        video_placeholder = st.empty()
    
    with col2:
        
        titulo = st.empty() # Espacio para el título

        # Crear 4 columnas para distribuir métricas horizontalmente
        met1, met2, met3, met4 = st.columns(4)
        with met1:
            metric_clientes = st.empty()
        with met2:
            metric_empleados = st.empty()
        with met3:
            metric_personas = st.empty()
        with met4:
            metric_latencia = st.empty()

            # Segunda fila: Confianza promedio de clientes y empleados
        conf1, conf2 = st.columns(2)

        with conf1:
            metric_conf_clientes = st.empty()
        with conf2:
            metric_conf_empleados = st.empty()

        titulo_grafico = st.empty() # Espacio para el título
        
        # Espacio para el gráfico de "pulsaciones"
        chart_placeholder = st.empty()

    history = deque(maxlen=30) # Últimos 30 valores para simular un pulso

    

    # Cargar el modelo YOLO
    modelo = YOLO("modelos/best.pt")  # Asegúrate de tener el archivo "yolo11s.pt" en el directorio correcto

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
    process = start_ffmpeg_process(link)

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
            if on:
                titulo.markdown("### Métricas en tiempo real")
                titulo_grafico.markdown("#### 📊 Cantidad de Clientes en Vivo")
                resultados = modelo.track(frame, persist=True)  # Usar persist=True para seguimiento entre frames
                frame_procesado = resultados[0].plot()  # Obtener el frame con las detecciones dibujadas

                # Extraer detecciones
                boxes = resultados[0].boxes
                clases = boxes.cls.cpu().numpy() if boxes is not None else []
                confianzas = boxes.conf.cpu().numpy() if boxes is not None else []

                num_clientes = sum(1 for box in resultados[0].boxes.cls if box == 0)
                num_empleados = sum(1 for box in resultados[0].boxes.cls if box == 1)
                latencia_total = sum(resultados[0].speed.values())
                num_detecciones = len(resultados[0].boxes)  # Contar objetos detectados
                # Confianza promedio
                clientes = confianzas[clases == 0] if 0 in clases else []
                empleados = confianzas[clases == 1] if 1 in clases else []
                conf_prom_clientes = np.mean(clientes) if len(clientes) > 0 else 0
                conf_prom_empleados = np.mean(empleados) if len(empleados) > 0 else 0

                # Agregar datos al historial para simular el pulso
                total_detectado = num_clientes + num_empleados
                history.append(num_clientes)

                # Crear un DataFrame para actualizar la gráfica
                df = pd.DataFrame({"Detecciones": list(history)})

                # Actualizar gráfico de línea
                chart_placeholder.line_chart(df, use_container_width=True, height=150)

                # Muestro las métricas
                metric_personas.metric(label="Personas detectadas", value=num_detecciones)
                metric_clientes.metric(label="Clientes detectados", value=num_clientes)
                metric_empleados.metric(label="Empleados detectados", value=num_empleados)  
                metric_latencia.metric(label="Latencia (ms)", value=f"{latencia_total:.1f}")  
                metric_conf_clientes.metric(label="Confianza Promedio Clientes", value=f"{conf_prom_clientes:.1f}")
                metric_conf_empleados.metric(label="Confianza Promedio Empleados", value=f"{conf_prom_empleados:.1f}")
            else:
                frame_procesado = frame  # Mostrar el frame sin procesar
                num_clientes, num_empleados, latencia_total = 0, 0, 0


            # Convertir el frame de BGR a RGB (Streamlit usa RGB)
            frame_rgb = cv2.cvtColor(frame_procesado, cv2.COLOR_BGR2RGB)
           
            # Mostrar el frame en Streamlit
            video_placeholder.image(frame_rgb, channels="RGB", width=640)

            # Controlar la velocidad de actualización
            time.sleep(1 / 10)  # 10 FPS

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

    finally:
        # Asegurarse de matar el proceso y liberar recursos
        if process.poll() is None:
            process.kill()