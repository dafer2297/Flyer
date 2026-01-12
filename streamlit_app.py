import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración inicial
st.set_page_config(page_title="Flyers Prefectura", layout="centered")

# Gestión de memoria para navegar entre pasos
if 'paso' not in st.session_state:
    st.session_state.paso = 1

st.title("🎨 Generador de Flyers Oficiales")

# ==========================================
# PASO 1: INGRESO DE DATOS
# ==========================================
if st.session_state.paso == 1:
    st.header("1. Datos del Evento")
    
    st.info("📝 Llena la información que aparecerá en el flyer.")
    
    # Campos de texto
    st.session_state.descripcion = st.text_area("Descripción del Evento:", "Disfruta de la gran feria agroecológica...")
    st.session_state.lugar = st.text_input("Lugar:", "Parque Calderón, Cuenca")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.fecha = st.text_input("Fecha:", "12 Feb")
    with col2:
        st.session_state.hora = st.text_input("Hora:", "10:00 AM")
        
    st.session_state.foto = st.file_uploader("Sube la FOTO de fondo:", type=["jpg", "png", "jpeg"])

    # Botón para continuar
    if st.button("Siguiente: Diseñar Flyer ➡️", type="primary"):
        if st.session_state.foto:
            st.session_state.paso = 2
            st.rerun()
        else:
            st.error("⚠️ Por favor sube una imagen de fondo para continuar.")

# ==========================================
# PASO 2: DISEÑO Y VISUALIZACIÓN
# ==========================================
elif st.session_state.paso == 2:
    st.header("2. Personalización")
    
    # Barra lateral para colores
    st.sidebar.header("🎨 Colores")
    color_caja_fondo = st.sidebar.color_picker("Fondo de Datos (Abajo)", "#006847") # Verde Prefectura
    color_cajas_fecha = st.sidebar.color_picker("Cajas de Fecha/Hora", "#ffffff")
    color_texto_fecha = st.sidebar.color_picker("Texto Fecha/Hora", "#000000")
    
    # --- PROCESAMIENTO DE IMAGEN ---
    # 1. Cargar imagen base
    img = Image.open(st.session_state.foto).convert("RGBA")
    ancho, alto = img.size
    capa = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(capa)
    
    # Intentar cargar fuente grande (si subiste fuente.ttf)
    try:
        font_titulo = ImageFont.truetype("fuente.ttf", int(alto * 0.05)) # 5% del alto de la foto
        font_texto = ImageFont.truetype("fuente.ttf", int(alto * 0.03))
        font_peque = ImageFont.truetype("fuente.ttf", int(alto * 0.025))
    except:
        # Si no hay fuente, usa la por defecto (es pequeña, mejor subir .ttf)
        font_titulo = ImageFont.load_default()
        font_texto = ImageFont.load_default()
        font_peque = ImageFont.load_default()

    # 2. LOGOS (Parte Superior)
    try:
        # Logo Prefectura (Izquierda)
        logo_pref = Image.open("logo_prefectura.png").convert("RGBA")
        ratio_pref = logo_pref.width / logo_pref.height
        nuevo_alto_logo = int(alto * 0.12) # 12% del alto de la foto
        logo_pref = logo_pref.resize((int(nuevo_alto_logo * ratio_pref), nuevo_alto_logo))
        img.paste(logo_pref, (int(ancho*0.05), int(alto*0.03)), logo_pref)

        # Logo Visit Azuay (Derecha)
        logo_visit = Image.open("logo_visit.png").convert("RGBA")
        ratio_visit = logo_visit.width / logo_visit.height
        logo_visit = logo_visit.resize((int(nuevo_alto_logo * ratio_visit), nuevo_alto_logo))
        img.paste(logo_visit, (int(ancho*0.95 - logo_visit.width), int(alto*0.03)), logo_visit)
    except:
        st.warning("⚠️ Sube los logos 'logo_prefectura.png' y 'logo_visit.png' a GitHub para verlos aquí.")

    # 3. TEXTO "INVITA" (Obligatorio)
    texto_invita = "LA PREFECTURA DEL AZUAY INVITA"
    # Calculamos posición centrada arriba (debajo de logos aprox)
    bbox_invita = draw.textbbox((0, 0), texto_invita, font=font_texto)
    ancho_txt = bbox_invita[2] - bbox_invita[0]
    # Dibujar sombra negra y texto blanco
    draw.text(((ancho - ancho_txt)/2 + 2, alto*0.18 + 2), texto_invita, font=font_texto, fill="black")
    draw.text(((ancho - ancho_txt)/2, alto*0.18), texto_invita, font=font_texto, fill="white")

    # 4. CAJA INFERIOR (Contenedor Principal)
    # Convertir hex a RGB para transparencia
    rgb_fondo = tuple(int(color_caja_fondo.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    # Dibuja un rectángulo en el 25% inferior de la imagen
    draw.rectangle([0, alto*0.75, ancho, alto], fill=rgb_fondo + (230,)) # 230 es opacidad alta

    # 5. DESCRIPCIÓN Y LUGAR (Dentro de la caja inferior)
    draw.text((ancho*0.05, alto*0.77), st.session_state.descripcion, font=font_texto, fill="white")
    draw.text((ancho*0.05, alto*0.83), f"📍 {st.session_state.lugar}", font=font_peque, fill="white")

    # 6. CAJAS SEPARADAS PARA FECHA Y HORA (A la derecha de la caja inferior)
    rgb_cajas = tuple(int(color_cajas_fecha.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Caja FECHA
    caja_fecha_x = ancho * 0.65
    caja_fecha_y = alto * 0.80
    ancho_caja = ancho * 0.15
    alto_caja = alto * 0.08
    draw.rectangle([caja_fecha_x, caja_fecha_y, caja_fecha_x + ancho_caja, caja_fecha_y + alto_caja], fill=rgb_cajas + (255,))
    draw.text((caja_fecha_x + 10, caja_fecha_y + 10), st.session_state.fecha, font=font_peque, fill=color_texto_fecha)
    
    # Caja HORA (Al lado)
    caja_hora_x = caja_fecha_x + ancho_caja + 20 # 20px de separación
    draw.rectangle([caja_hora_x, caja_fecha_y, caja_hora_x + ancho_caja, caja_fecha_y + alto_caja], fill=rgb_cajas + (255,))
    draw.text((caja_hora_x + 10, caja_fecha_y + 10), st.session_state.hora, font=font_peque, fill=color_texto_fecha)

    # --- FINALIZAR IMAGEN ---
    img_final = Image.alpha_composite(img, capa).convert("RGB")
    
    # Mostrar en pantalla
    st.image(img_final, caption="Vista Previa del Flyer", use_container_width=True)
    
    # Botones de acción
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Editar Datos"):
            st.session_state.paso = 1
            st.rerun()
    with col_btn2:
        # Convertir a bytes para descargar
        buf = io.BytesIO()
        img_final.save(buf, format="JPEG", quality=95)
        st.download_button(
            label="📥 DESCARGAR FLYER LISTO",
            data=buf.getvalue(),
            file_name="flyer_prefectura.jpg",
            mime="image/jpeg",
            type="primary"
        )
