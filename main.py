from ultralytics import YOLO

modelo = YOLO("yolo11n-pose.pt")

resultado = modelo.track(source="video.mp4", show=True, save=True)