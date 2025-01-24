# ProyectoGrupal-G3-UEM


El archivo `requirements.txt` contiene la lista de todas las librerías y sus versiones específicas que necesita el proyecto para funcionar correctamente. Esto asegura que todo el equipo use las mismas dependencias, evitando errores de compatibilidad.

## Instalación de librerías desde `requirements.txt`

Para instalar todas las librerías especificadas en el archivo requirements.txt, sigue estos pasos:

1. **Asegúrate de estar en el entorno virtual**:
    ```bash
    .\venv\Scripts\activate
    ```

2. **Ejecuta el siguiente comando**:
    ```bash
    pip install -r requirements.txt
    ```

Esto instalará automáticamente todas las dependencias necesarias para el proyecto.

## Pasos para actualizar el archivo `requirements.txt`

1. **Asegúrate de estar en el entorno virtual**:
   - En Windows:
     ```bash
     .\venv\Scripts\activate
     ```

2. **Actualiza el archivo `requirements.txt`** con las librerías instaladas en el entorno virtual:
   ```bash
   pip freeze > requirements.txt

Esto sobreescribirá el archivo requirements.txt con la lista actual de dependencias.

