import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap

st.set_page_config(page_title="Flyer Prefectura Final V3", layout="centered")

# --- FUNCIÓN PARA TEXTO CON SOMBRA ---
def dibujar_texto_sombra(draw, xy, texto, fuente, color="white", sombra="black"):
    x, y = xy
    # Sombra un poco más fuerte
    draw.text((x+6, y+6), texto, font=fuente, fill=sombra)
    draw.text((x, y), texto, font=fuente, fill=color)

if 'paso' not in st.session_state: st.session_state.paso = 1

st.title("🎨 Generador de Flyers (Logos Gigantes)")

# ==================== PASO 1: DATOS ====================
if st.session_state.paso == 1:
    st.header("1. Ingresa los datos")
    
    st.session_state.titulo = st.text_area("TÍTULO PRINCIPAL:", "TE INVITA")
    st.session_state.cuerpo = st.text_area("Descripción:", "Al evento de entrega de la membresía a la Red Mundial de Destinos Turísticos del Cacao.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.fecha = st.text_input("Fecha:", "Miércoles, 6 de Agosto")
        st.session_state.hora = st.text_input("Hora:", "18:30")
    with col2:
        st.session_state.lugar_nombre = st.text_input("Lugar:", "Teatrina de la Casa de la Provincia")
        st.session_state.lugar_dir = st.text_input("Dirección:", "(Tomás Ordóñez 8-69 y Simón Bolívar)")
        
    st.session_state.foto = st.file_uploader("Sube tu foto:", type=["jpg", "png", "jpeg"])

    if st.button("Diseñar Flyer ➡️", type="primary"):
        if st.session_state.foto:
            st.session_state.paso = 2
            st.rerun()
        else:
            st.error("⚠️ Sube una foto primero.")

# ==================== PASO 2: DISEÑO ====================
elif st.session_state.paso == 2:
    st.header("2. Ajustes Finales y Descarga")
    
    st.sidebar.header("🎨 Ajustes")
    st.sidebar.subheader("Filtro sobre la foto")
    color_filtro = st.sidebar.color_picker("Color del Filtro", "#003300") # Verde muy oscuro por defecto
    opacidad_filtro = st.sidebar.slider("Intensidad del Filtro", 0, 255, 150) # Un poco más oscuro
    st.sidebar.subheader("Colores Tarjeta")
    color_tarjeta = st.sidebar.color_picker("Color de la Tarjeta", "#2E7D32")

    # 1. LIENZO VERTICAL
    canvas_w, canvas_h = 1080, 1920
    
    imagen_usuario = Image.open(st.session_state.foto).convert("RGBA")
    img = ImageOps.fit(imagen_usuario, (canvas_w, canvas_h), centering=(0.5, 0.5))
    
    # --- APLICAR CAPA DE COLOR (OVERLAY) ---
    rgb_filtro = tuple(int(color_filtro.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    overlay = Image.new("RGBA", img.size, rgb_filtro + (opacidad_filtro,))
    img = Image.alpha_composite(img, overlay)

    capa = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(capa)
    
    # 2. FUENTES (Canaro)
    try:
        f_titulo = ImageFont.truetype("Canaro-ExtraBold.ttf", 140)
        f_invita = ImageFont.truetype("Canaro-ExtraBold.ttf", 90)
        f_cuerpo = ImageFont.truetype("Canaro-Medium.ttf", 55)
        f_info = ImageFont.truetype("Canaro-Medium.ttf", 45)
        f_info_peq = ImageFont.truetype("Canaro-Medium.ttf", 35)
    except:
        st.error("⚠️ Fuentes Canaro no encontradas.")
        f_titulo = f_invita = f_cuerpo = f_info = f_info_peq = ImageFont.load_default()

    # 3. LOGO PREFECTURA (ARRIBA - GIGANTE SUPREMO)
    try:
        # AUMENTADO A 650px (Era 450)
        h_logo_p = 650 
        logo_pref = Image.open("logo_prefectura.png").convert("RGBA")
        ratio = logo_pref.width / logo_pref.height
        logo_pref = logo_pref.resize((int(h_logo_p * ratio), h_logo_p))
        x_logo_p = (canvas_w - logo_pref.width) // 2
        img.paste(logo_pref, (x_logo_p, 30), logo_pref)
    except: pass

    # 4. TEXTOS (Movidos más abajo para dar espacio al logo gigante)
    y_texto = 750 # BAJADO DE 500 A 750
    
    # Título
    bbox = draw.textbbox((0,0), st.session_state.titulo, font=f_titulo)
    w_tit = bbox[2] - bbox[0]
    dibujar_texto_sombra(draw, ((canvas_w - w_tit)/2, y_texto), st.session_state.titulo, f_titulo)
    
    y_texto += 180
    
    # Descripción
    lineas = textwrap.wrap(st.session_state.cuerpo, width=28) 
    for linea in lineas:
        bbox_l = draw.textbbox((0,0), linea, font=f_cuerpo)
        w_l = bbox_l[2] - bbox_l[0]
        dibujar_texto_sombra(draw, ((canvas_w - w_l)/2, y_texto), linea, f_cuerpo)
        y_texto += 70

    # 5. TARJETA INFO (DERECHA)
    w_card = 650
    h_card = 500
    y_card = canvas_h - h_card - 350 # Ajustado altura
    
    rgb_t = tuple(int(color_tarjeta.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    draw.rounded_rectangle([canvas_w - w_card, y_card, canvas_w + 50, y_card + h_card], radius=40, fill=rgb_t + (230,))
    
    margin_x = canvas_w - w_card + 40
    margin_y = y_card + 40
    
    draw.text((margin_x, margin_y), "📍 " + st.session_state.lugar_nombre, font=f_info, fill="white")
    draw.text((margin_x, margin_y + 60), st.session_state.lugar_dir, font=f_info_peq, fill="white")
    draw.text((margin_x, margin_y + 160), "🗓️ " + st.session_state.fecha, font=f_info, fill="white")
    draw.text((margin_x, margin_y + 260), "🕒 " + st.session_state.hora, font=f_info, fill="white")

    # 6. LOGO VISIT AZUAY (ESQUINA INFERIOR IZQUIERDA EXACTA)
    try:
        logo_visit = Image.open("logo_visit.png").convert("RGBA")
        # AUMENTADO A 700px (Era 550)
        h_visit = 700 
        r_visit = logo_visit.width / logo_visit.height
        logo_visit = logo_visit.resize((int(h_visit * r_visit), h_visit))
        
        # Posición: X = -30 (para asegurar que pegue al borde izquierdo)
        # Posición: Y = canvas_h - h_visit (borde inferior exacto)
        img.paste(logo_visit, (-30, canvas_h - h_visit), logo_visit)
    except: pass

    # --- FINALIZAR ---
    img_final = Image.alpha_composite(img, capa).convert("RGB")
    
    st.image(img_final, caption="Flyer Final", width=400)
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ Editar", type="secondary"): st.session_state.paso = 1; st.rerun()
    with c2:
        buf = io.BytesIO()
        img_final.save(buf, format="JPEG", quality=100)
        st.download_button("📥 DESCARGAR FLYER", data=buf.getvalue(), file_name="flyer_prefectura_final.jpg", mime="image/jpeg", type="primary")
