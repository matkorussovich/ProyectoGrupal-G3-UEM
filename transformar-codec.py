import subprocess
import os

def convertir_videos_en_carpeta(carpeta_entrada, carpeta_salida):
    # Verifica si la carpeta de salida existe, si no, la crea
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    
    # Recorre todos los archivos en la carpeta de entrada
    for archivo in os.listdir(carpeta_entrada):
        ruta_archivo = os.path.join(carpeta_entrada, archivo)
        
        # Verifica si el archivo es un video (puedes ajustar la extensión si es necesario)
        if archivo.endswith(".mp4"):
            # Ruta del archivo convertido en la carpeta de salida
            nombre_salida = os.path.splitext(archivo)[0] + "_h264.mp4"
            ruta_salida = os.path.join(carpeta_salida, nombre_salida)
            
            # Comando FFmpeg para convertir el video a H.264
            comando = [
                "ffmpeg", "-i", ruta_archivo,  # archivo de entrada
                "-vcodec", "libx264",  # códec H.264
                "-acodec", "aac",  # códec de audio compatible
                "-strict", "experimental",  # opción para usar el códec AAC
                ruta_salida  # archivo de salida
            ]
            
            # Ejecutar el comando para convertir el video
            subprocess.run(comando, check=True)
            print(f"Video convertido: {archivo} -> {nombre_salida}")
        else:
            print(f"El archivo {archivo} no es un video MP4, se omite.")

# Ejemplo de uso
carpeta_entrada = "grabaciones/Salida"  # Ruta de la carpeta con los videos originales
carpeta_salida = "grabaciones/Salida_convertidos"  # Ruta de la carpeta donde se guardarán los videos convertidos

convertir_videos_en_carpeta(carpeta_entrada, carpeta_salida)
