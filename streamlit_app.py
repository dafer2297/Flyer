import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap

st.set_page_config(page_title="Flyer 4K Tarjeta Ajustada", layout="centered")

def dibujar_texto_sombra(draw, xy, texto, fuente, color="white", sombra="black"):
    x, y = xy
    draw.text((x+8, y+8), texto, font=fuente, fill=sombra)
    draw.text((x, y), texto, font=fuente, fill=color)

if 'paso' not in st.session_state: st.session_state.paso = 1

st.title("💎 Generador 4K (Tarjeta Compacta)")

# ==================== PASO 1: DATOS ====================
if st.session_state.paso == 1:
    st.header("1. Ingresa los datos")
    st.info("ℹ️ Generando en ULTRA HD (2160x3840) - Formato PNG.")
    
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
    st.header("2. Resultado Final")
    
    st.sidebar.header("🎨 Ajustes")
    color_filtro = st.sidebar.color_picker("Color del Filtro", "#002200")
    opacidad_filtro = st.sidebar.slider("Oscuridad del Fondo", 0, 255, 120)
    color_tarjeta = st.sidebar.color_picker("Color Tarjeta", "#2E7D32")

    # 1. LIENZO 4K
    canvas_w, canvas_h = 2160, 3840
    
    imagen_usuario = Image.open(st.session_state.foto).convert("RGBA")
    img = ImageOps.fit(imagen_usuario, (canvas_w, canvas_h), centering=(0.5, 0.5), method=Image.Resampling.LANCZOS)
    
    # Capa de color
    rgb_filtro = tuple(int(color_filtro.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    overlay = Image.new("RGBA", img.size, rgb_filtro + (opacidad_filtro,))
    img = Image.alpha_composite(img, overlay)

    capa = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(capa)
    
    # 2. FUENTES 4K
    try:
        f_titulo = ImageFont.truetype("Canaro-ExtraBold.ttf", 220)
        f_cuerpo = ImageFont.truetype("Canaro-Medium.ttf", 90)
        f_info = ImageFont.truetype("Canaro-Medium.ttf", 85) # Un poco más pequeña para encajar
        f_info_peq = ImageFont.truetype("Canaro-Medium.ttf", 65)
    except:
        st.error("⚠️ Fuentes no encontradas.")
        f_titulo = f_cuerpo = f_info = f_info_peq = ImageFont.load_default()

    # 3. LOGO PREFECTURA (PEQUEÑO)
    h_logo_p = 600 
    try:
        logo_pref = Image.open("logo_prefectura.png").convert("RGBA")
        ratio = logo_pref.width / logo_pref.height
        logo_pref = logo_pref.resize((int(h_logo_p * ratio), h_logo_p), Image.Resampling.LANCZOS)
        x_logo_p = (canvas_w - logo_pref.width) // 2
        img.paste(logo_pref, (x_logo_p, 50), logo_pref)
    except: pass

    # 4. TEXTOS
    y_texto = 750 
    
    bbox = draw.textbbox((0,0), st.session_state.titulo, font=f_titulo)
    w_tit = bbox[2] - bbox[0]
    dibujar_texto_sombra(draw, ((canvas_w - w_tit)/2, y_texto), st.session_state.titulo, f_titulo)
    
    y_texto += 260 
    
    lineas = textwrap.wrap(st.session_state.cuerpo, width=35) 
    for linea in lineas:
        bbox_l = draw.textbbox((0,0), linea, font=f_cuerpo)
        w_l = bbox_l[2] - bbox_l[0]
        dibujar_texto_sombra(draw, ((canvas_w - w_l)/2, y_texto), linea, f_cuerpo)
        y_texto += 110

    # 5. TARJETA INFO (AJUSTADA Y FLOTANTE)
    # Reducimos tamaño
    w_card = 1100  # Antes 1300
    h_card = 850   # Antes 1000
    y_card = canvas_h - h_card - 750
    
    # Margen derecho de 100px para que "flote" dentro de la imagen
    margen_derecho = 80
    x_inicio_tarjeta = canvas_w - w_card - margen_derecho
    
    rgb_t = tuple(int(color_tarjeta.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Dibujamos el rectángulo
    draw.rounded_rectangle(
        [x_inicio_tarjeta, y_card, canvas_w - margen_derecho, y_card + h_card], 
        radius=60, 
        fill=rgb_t + (230,)
    )
    
    # Texto dentro de la tarjeta
    margin_x = x_inicio_tarjeta + 60
    margin_y = y_card + 60
    
    # Apretamos un poco el espaciado vertical
    draw.text((margin_x, margin_y), "📍 " + st.session_state.lugar_nombre, font=f_info, fill="white")
    draw.text((margin_x, margin_y + 110), st.session_state.lugar_dir, font=f_info_peq, fill="white")
    draw.text((margin_x, margin_y + 280), "🗓️ " + st.session_state.fecha, font=f_info, fill="white")
    draw.text((margin_x, margin_y + 450), "🕒 " + st.session_state.hora, font=f_info, fill="white")

    # 6. LOGO VISIT AZUAY
    h_visit = 1000 
    try:
        logo_visit = Image.open("logo_visit.png").convert("RGBA")
        r_visit = logo_visit.width / logo_visit.height
        logo_visit = logo_visit.resize((int(h_visit * r_visit), h_visit), Image.Resampling.LANCZOS)
        img.paste(logo_visit, (0, canvas_h - h_visit), logo_visit)
    except: pass

    # --- FINALIZAR ---
    img_final = Image.alpha_composite(img, capa).convert("RGB")
    
    st.image(img_final, caption="Vista Previa", width=400)
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ Editar", type="secondary"): st.session_state.paso = 1; st.rerun()
    with c2:
        buf = io.BytesIO()
        img_final.save(buf, format="PNG")
        st.download_button("📥 DESCARGAR 4K (PNG)", data=buf.getvalue(), file_name="flyer_prefectura_4k.png", mime="image/png", type="primary")
