import os
import streamlit as st
from streamlit_navigation_bar import st_navbar
import pages as pg
import os
import altair as alt

st.set_page_config(page_title="in-sight", page_icon="👁️", initial_sidebar_state="collapsed", layout="wide")
alt.theme.enable("dark")

pages = ["Video en Vivo", "Análisis", "GitHub"]
parent_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(parent_dir, "imagenes/logo.svg")
urls = {"GitHub": "https://github.com/matkorussovich/ProyectoGrupal-G3-UEM"}

styles = {
    "nav": {
        "background-color": "black",
        "justify-content": "left",
    },
    "img": {
        "width": "120px",
        "height": "60px",
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px",
        "font-size": "14px",
        "font-family": "Arial",
    },
    "active": {
        "background-color": "white",  # Solo fondo blanco
        "font-weight": "normal",
        "padding": "14px",
    }
}

options = {
    "show_menu": True,
    "show_sidebar": False,
}


st.markdown(
    """
    <style>
    /* Color del texto principal */
    .navbar-span .navbar-text {
        color: white !important;
    }
    
    /* Color del texto activo */
    .navbar-span.active .navbar-text {
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

page = st_navbar(
    pages,
    logo_path=logo_path,
    urls=urls,
    styles=styles,
    options=options,
)


functions = {
    "Inicio": pg.show_inicio,
    "Video en Vivo": pg.show_vivo,
    "Análisis": pg.show_dashboard
}
go_to = functions.get(page, functions["Inicio"])

if go_to:
    go_to()