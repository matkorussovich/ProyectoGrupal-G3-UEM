import streamlit as st
import cv2
import tempfile
import pandas as pd
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Análisis de Videos - YOLO", layout="wide")

# Título
st.title("Análisis de Videos de Cámaras de Seguridad con YOLO")

# Subida de video
st.sidebar.header("Cargar Video")
video_file = st.sidebar.file_uploader("Sube tu video aquí", type=["mp4", "avi", "mov"])

if video_file:
    # Mostrar video cargado
    st.subheader("Video Cargado")
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    video_path = tfile.name

    st.video(video_path)

    # Procesar video con YOLO (placeholder)
    st.subheader("Análisis de Detección de Objetos")
    st.text("Procesando el video...")
    
    # Simulación de detección (sólo como ejemplo)
    with st.spinner("Corriendo modelo YOLO..."):
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        detected_objects = []  # Lista para almacenar detecciones simuladas

        for i in range(min(frame_count, 50)):  # Procesar hasta 50 frames para la demo
            ret, frame = cap.read()
            if not ret:
                break

            # Simulación de detección de un objeto (ejemplo)
            detected_objects.append({"frame": i, "objeto": "Persona", "confianza": 0.85})

        cap.release()

    st.success("Análisis completo!")

    # Mostrar resultados
    st.subheader("Resultados de las Detecciones")
    df_results = pd.DataFrame(detected_objects)
    st.dataframe(df_results)

    # Mostrar analítica
    st.subheader("Analítica del Video")
    st.bar_chart(df_results["objeto"].value_counts())

else:
    st.info("Por favor, carga un video en el panel lateral para comenzar.")