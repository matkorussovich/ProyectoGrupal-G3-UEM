import streamlit as st

def show_inicio():
    # Título principal
    st.title("Bienvenido a In Sight")
    
    # Descripción de la aplicación
    st.header("In Sight: Análisis de Métricas de Negocio con YOLO")
    
    st.write(
        """
        **In Sight** es una herramienta poderosa diseñada para ayudar a las empresas a analizar y visualizar métricas de negocio en tiempo real utilizando la tecnología de detección de objetos **YOLO** (You Only Look Once). Esta aplicación permite realizar un análisis detallado de datos de cámaras de seguridad y obtener información valiosa sobre el comportamiento de los clientes, empleados y operaciones en general.
        """
    )

    # Agregamos dos columnas para el contenido
    col_1, col_2 = st.columns(2, gap="medium")

    # Columna 1: Beneficios de la aplicación
    with col_1:
        st.subheader("Beneficios de usar In Sight:")
        st.write(
            """
            - **Análisis en tiempo real**: Obtén información actualizada sobre el tráfico de personas, interacciones y eventos importantes.
            - **Monitoreo de cámaras de seguridad**: Visualiza y analiza videos en vivo para detectar patrones y comportamientos.
            - **Métricas de negocio**: Analiza el rendimiento de las operaciones comerciales con datos de video.
            - **Fácil integración con tu infraestructura**: Compatible con cámaras de seguridad existentes y sistemas de gestión de datos.
            - **Interfaz intuitiva**: No necesitas ser un experto en análisis de datos para obtener información valiosa.
            """
        )

    # Columna 2: Cómo funciona
    with col_2:
        st.subheader("¿Cómo funciona In Sight?")
        st.write(
            """
            In Sight utiliza **YOLO** para procesar imágenes y videos en tiempo real, detectando objetos y personas de manera eficiente. La aplicación analiza los datos capturados por las cámaras de seguridad y presenta visualizaciones y métricas útiles para mejorar las decisiones comerciales.

            La interfaz permite al usuario interactuar con los datos, mostrar analíticas de los videos grabados y ver el conteo de personas y empleados en diferentes secciones de la tienda o instalaciones.
            """
        )

    # Llamado a la acción
    st.write("\n")
    st.write("---")
    st.header("¿Estás listo para comenzar?")


    # Footer con créditos
    st.write("---")
    st.markdown(
        """
        <div style="text-align: center; font-size: 15px; color: #888888;">
            <p>Desarrollado por Matko Ivan Russovich, Alvaro Settimo y Antony Paolo Perez Vargas para el Máster en Data Science de la Universidad Europea</p>
        </div>
        """,
        unsafe_allow_html=True
    )
