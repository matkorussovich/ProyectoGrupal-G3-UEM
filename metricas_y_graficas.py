import pandas as pd
import matplotlib.pyplot as plt
import re
import os

def procesar_csv(nombre_csv):
    # Extraer la fecha y hora del nombre del archivo
    match = re.search(r'grabacion_(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})', nombre_csv)
    if not match:
        print("Error: Nombre de archivo no coincide con el formato esperado.")
        return
    fecha, hora_ini, min_ini, seg_ini = match.groups()
    hora_ini, min_ini, seg_ini = map(int, [hora_ini, min_ini, seg_ini])
    
    # Cargar datos
    df = pd.read_csv(nombre_csv)
    df.columns = ["frame", "track_id", "class_id", "confidence", "x1", "y1", "x2", "y2"]
    
    # FPS del video
    fps = 10
    
    # Cantidad total de clientes
    clientes_totales = df[df["class_id"] == 0]["track_id"].nunique()
    
    # Confianza media total y por clase
    confianza_media_total = df["confidence"].mean()
    confianza_media_por_clase = df.groupby("class_id")["confidence"].mean()
    
    # Calcular tiempo de permanencia
    tiempos_permanencia = (df.groupby("track_id")["frame"].max() - df.groupby("track_id")["frame"].min()) / fps
    tiempo_medio = tiempos_permanencia.mean()
    tiempo_maximo = tiempos_permanencia.max()
    tiempo_minimo = tiempos_permanencia.min()
    
    # Agregar la columna de timestamp relativo
    df["segundo"] = df["frame"] / fps
    df["hora"] = (hora_ini * 3600 + min_ini * 60 + seg_ini + df["segundo"]) // 3600
    clientes_por_hora = df[df["class_id"] == 0].groupby("hora")["track_id"].nunique()
    
    # Calcular tiempo total de ausencia de empleados
    total_frames = df["frame"].max()
    frames_con_empleados = df[df["class_id"] == 1]["frame"].nunique()
    frames_sin_empleados = total_frames - frames_con_empleados
    tiempo_ausente = frames_sin_empleados / fps
    
    # Graficar cantidad de clientes por hora
    plt.figure(figsize=(8, 5))
    clientes_por_hora.plot(kind='bar', color='b', alpha=0.7)
    plt.xlabel("Hora")
    plt.ylabel("Cantidad de Clientes")
    plt.title(f"Clientes por hora - {fecha}")
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
    
    # Histograma de tiempos de permanencia
    plt.figure(figsize=(8, 5))
    plt.hist(tiempos_permanencia, bins=10, color='g', alpha=0.7, edgecolor='black')
    plt.xlabel("Tiempo de Permanencia (s)")
    plt.ylabel("Cantidad de Clientes")
    plt.title("Distribución de Tiempos de Permanencia")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
    
    # Mostrar métricas calculadas
    print(f"Cantidad total de clientes detectados: {clientes_totales}")
    print(f"Confianza media total: {confianza_media_total:.2f}")
    print(f"Confianza media por clase:\n{confianza_media_por_clase}")
    print(f"Tiempo medio de permanencia: {tiempo_medio:.2f} s")
    print(f"Tiempo máximo de permanencia: {tiempo_maximo:.2f} s")
    print(f"Tiempo mínimo de permanencia: {tiempo_minimo:.2f} s")
    print(f"Tiempo total de ausencia de empleados: {tiempo_ausente:.2f} s")
    
# Ejecutar análisis sobre un archivo CSV de ejemplo
nombre_csv = "grabacion_2025-02-24_21-11-19.csv"
procesar_csv(nombre_csv)


