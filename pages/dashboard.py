import os
import re
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# Ruta de la carpeta donde están las grabaciones
CARPETA_GRABACIONES = r"grabaciones\Salida"
CARPETA_CSV = r"grabaciones\Salida\csv"
# CARPETA_CSV = r"datos-salida"

# Función para obtener las fechas y horas disponibles a partir de los nombres de los archivos
def obtener_fechas_horas():

    archivos = os.listdir(CARPETA_GRABACIONES)
    fechas_horas_dict = {}

    # Expresión regular para extraer fecha y hora completa (con minutos y segundos)
    patron = r"grabacion_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})\.mp4"

    for archivo in archivos:
        match = re.search(patron, archivo)
        if match:
            fecha = match.group(1)  # Fecha en formato YYYY-MM-DD
            hora_completa = match.group(2)  # Hora completa en formato HH-MM-SS

            # Convertir la fecha a formato DD/MM/YYYY
            fecha_formateada = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
            
            # Usar la hora completa (hora, minutos y segundos) tal cual del nombre del archivo
            hora_redondeada = hora_completa.replace('-', ':')  # Convertimos la hora a HH:MM:SS

            # Agregar al diccionario
            if fecha_formateada not in fechas_horas_dict:
                fechas_horas_dict[fecha_formateada] = []
            fechas_horas_dict[fecha_formateada].append(hora_redondeada)

    # Ordenar las horas en cada fecha
    for fecha in fechas_horas_dict:
        fechas_horas_dict[fecha].sort(reverse=True)

    # Ordenar las fechas
    fechas_disponibles = sorted(fechas_horas_dict.keys(), reverse=True)

    return fechas_disponibles, fechas_horas_dict

# Obtener las fechas y horas disponibles
fechas_disponibles, fechas_horas_dict = obtener_fechas_horas()

def show_dashboard():
    
    # col_t1, col_t2 = st.columns([1, 5])
    
    # with col_t1:
    #     st.image("imagenes/logo-negro.png", width=200)
    
    # with col_t2:
    #     st.write(
    #         """
    #         ## Empanadas Tita de Buenos Aires 🥟
    #         """
    #     )
      
    #col1, col2, col3 = st.columns((2, 3.5, 2), gap='medium')
    col1, col2 = st.columns(2)

    with col1:
        # st.image("imagenes/logo-negro.png", width=120)
        st.write(
            """
            ## Empanadas Tita de Buenos Aires 🥟

            Análisis de grabaciones de la cámara de seguridad de la tienda.
            """
        )

        col_f, col_h = st.columns(2)

        with col_f:

            # Selección de fecha
            seleccion_fecha = st.selectbox("Selecciona la fecha:", fechas_disponibles)

        with col_h:

            # Selección de hora basada en la fecha elegida
            if seleccion_fecha:
                horas_disponibles = fechas_horas_dict.get(seleccion_fecha, [])
            else:
                horas_disponibles = []

            seleccion_hora = st.selectbox("Selecciona la hora:", horas_disponibles if horas_disponibles else ["No hay horas disponibles"])

        # Video
    
        if seleccion_fecha and seleccion_hora and seleccion_hora != "No hay horas disponibles":
            # Convertir la fecha seleccionada a formato 'YYYY-MM-DD'
            fecha_formato_archivo = datetime.strptime(seleccion_fecha, "%d/%m/%Y").strftime("%Y-%m-%d")

            # Buscar la hora completa (con minutos y segundos) en el nombre del archivo
            hora_completa = seleccion_hora.replace(":", "-")  # Convertir la hora a formato HH-MM-SS

            # Ahora construimos el nombre del archivo original
            nombre_video = f"grabacion_{fecha_formato_archivo}_{hora_completa}.mp4/grabacion_{fecha_formato_archivo}_{hora_completa}.mp4"

            # Nombre del archivo CSV
            csv = f"grabacion_{fecha_formato_archivo}_{hora_completa}.csv"
            
            ruta_csv = os.path.join(CARPETA_CSV, csv)
            
            print("ruta csv:",ruta_csv)

            # Cargo el csv 
            df = pd.read_csv(ruta_csv)

            # Eliminar las columnas x_cliente e y_cliente
            df = df.drop(columns=['x_cliente', 'y_cliente'])

            # Convertir la columna 'fecha_hora' a tipo datetime
            df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])

            # Obtener el primer registro (más antiguo)
            primer_registro = df['fecha_hora'].min()

            # Calcular la diferencia en minutos con respecto al primer registro
            df['minuto_video'] = (df['fecha_hora'] - primer_registro).dt.total_seconds() // 60

            # Agrupar por minuto
            df['minuto'] = df['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M')  # agrupar por minuto
            df_minute = df.groupby('minuto').agg({
                'clientes_mostrador': lambda x: x.mode()[0] if not x.mode().empty else np.nan,
                'clientes_totales': lambda x: x.mode()[0] if not x.mode().empty else np.nan,
                'empleados_totales': lambda x: x.mode()[0] if not x.mode().empty else np.nan,
                'minuto_video': 'first'  # Mantener el primer valor del minuto_video en cada grupo
            }).reset_index()

            # Convertir 'minuto' de vuelta a datetime
            df_minute['fecha_hora'] = pd.to_datetime(df_minute['minuto'])

            # Crear una columna combinada de la fecha y hora con el minuto del video
            df_minute['hora_minuto_combinado'] = df_minute['fecha_hora'].dt.strftime('%H:%M') + ' - Min: ' + df_minute['minuto_video'].astype(str)

            print("ruta video:",os.path.join(CARPETA_GRABACIONES, nombre_video))

            # Verificar si el archivo existe antes de intentar mostrarlo
            ruta_video = os.path.join(CARPETA_GRABACIONES, nombre_video)
            if os.path.exists(ruta_video):
                st.video(ruta_video, format="video/mp4", start_time=0, subtitles=None, end_time=None, loop=False, autoplay=False, muted=True)
            else:
                st.warning(f"No se encontró la grabación: {nombre_video}")

            # ================================
            # Visualización de métricas
            # ================================
            total_clientes_mostrador = df_minute['clientes_mostrador'].sum()
            # promedio_clientes_mostrador = df['clientes_mostrador'].mean()
            st.metric(label="Cantidad aprox de clientes en mostrador", value=total_clientes_mostrador)
            # st.metric(label="Promedio de clientes cerca del mostrador por frame:** {promedio_clientes_mostrador:.2f}")

            total_clientes_totales = df_minute['clientes_totales'].sum()
            st.metric(label="Cantidad Aproximada de Clientes", value=total_clientes_totales)

        else:
            st.warning("Selecciona una fecha y hora para ver la grabación.")

    with col2:
        
        st.subheader("  ")
        st.subheader("  ")

        # Gráfico para clientes mostrador
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_minute['hora_minuto_combinado'], y=df_minute['clientes_mostrador'], mode='lines', name='Clientes Mostrador', line=dict(color='royalblue')))
        fig1.update_layout(title='Clientes Mostrador por Minuto', xaxis_title='Fecha y Hora', yaxis_title='Clientes Mostrador')
        st.plotly_chart(fig1)

        # Gráfico para clientes totales
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_minute['hora_minuto_combinado'], y=df_minute['clientes_totales'], mode='lines', name='Clientes Totales', line=dict(color='forestgreen')))
        fig2.update_layout(title='Clientes Totales por Minuto', xaxis_title='Fecha y Hora', yaxis_title='Clientes Totales')
        st.plotly_chart(fig2)