import cv2
import subprocess
import numpy as np
import time
import json

video_url = "https://ca144.cameramanager.com/stream/hls/getPlaylist?access_token=6ece58ff-db6a-4b5a-9457-a7daf1b6244e:10008&camera_id=3035839"

# Obtener la información del stream usando FFmpeg
ffprobe_cmd = [
    "ffprobe",
    "-v", "error",
    "-show_entries", "stream=width,height",
    "-of", "json",
    video_url
]

# Ejecutar ffprobe para obtener la resolución
result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stream_info = json.loads(result.stdout)

# Extraer la resolución
video_width = int(stream_info['streams'][0]['width'])
video_height = int(stream_info['streams'][0]['height'])

print(f"Resolución detectada: {video_width}x{video_height}")

# Comando para invocar ffmpeg y obtener los frames de video en bruto
ffmpeg_cmd = [
    "ffmpeg",
    "-i", video_url,
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-an",
    "-hide_banner",
    "-fflags", "nobuffer",  # Desactivar el buffering
    "-flags", "low_delay",  # Reducir la latencia
    "-r", "10",  # Limitar la velocidad de lectura a 10 FPS
    "-loglevel", "error",
    "pipe:1"
]

try:
    # Iniciar el proceso de ffmpeg
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**9)

    # Variables para calcular los FPS
    frame_count = 0
    start_time = time.time()

    # Ventana para mostrar el video
    while True:
        raw_frame = process.stdout.read(video_width * video_height * 3)
        if len(raw_frame) != video_width * video_height * 3:
            print("No se pudo leer el frame completo. Saliendo...")
            break

        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((video_height, video_width, 3))

        frame_count += 1
        elapsed_time = time.time() - start_time

        if elapsed_time > 1:
            fps = frame_count / elapsed_time
            print(f"FPS procesados: {fps:.2f}")
            frame_count = 0
            start_time = time.time()

        cv2.imshow("Video en Vivo con FFmpeg", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except Exception as e:
    print(f"Ocurrió un error: {e}")

finally:
    if process.poll() is None:
        process.kill()
    cv2.destroyAllWindows()
