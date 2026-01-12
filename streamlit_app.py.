import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Memoria de la app para las dos páginas
if 'paso' not in st.session_state:
    st.session_state.paso = 1

st.title("🎨 Generador de Flyers - Prefectura")

# --- PASO 1: ENTRADA DE DATOS ---
if st.session_state.paso == 1:
    st.header("1. Datos del Evento")
    st.session_state.lugar = st.text_input("Lugar:", "Cuenca, Azuay")
    st.session_state.fecha = st.text_input("Fecha y Hora:", "12 de Enero, 10:00 AM")
    st.session_state.foto = st.file_uploader("Sube la foto de fondo", type=["jpg", "png", "jpeg"])

    if st.button("Siguiente: Diseñar Flyer ➡️"):
        if st.session_state.foto:
            st.session_state.paso = 2
            st.rerun()
        else:
            st.error("Por favor, sube una foto primero.")

# --- PASO 2: DISEÑO Y DESCARGA ---
elif st.session_state.paso == 2:
    st.header("2. Personaliza y Descarga")
    
    color_caja = st.sidebar.color_picker("Color de la caja", "#006847")
    
    # Procesar imagen
    img = Image.open(st.session_state.foto).convert("RGBA")
    draw = ImageDraw.Draw(img)
    ancho, alto = img.size
    
    # Dibujar cuadro de datos
    rgb = tuple(int(color_caja.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    draw.rectangle([ancho*0.05, alto*0.7, ancho*0.95, alto*0.9], fill=rgb + (200,))
    
    st.image(img, use_container_width=True)
    
    if st.button("⬅️ Cambiar Datos"):
        st.session_state.paso = 1
        st.rerun()

    # Preparar descarga
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG")
    st.download_button("📥 Descargar Flyer Final", data=buf.getvalue(), file_name="flyer_azuay.jpg")
