import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap
import base64

st.set_page_config(page_title="Generador Oficial", layout="centered")

# --- FUNCIÓN: CARGAR IMÁGENES Y ESTILOS ---
def configurar_diseño():
    # 1. Cargar Fondo Azul
    try:
        main_bg = "fondo_azul.png"
        main_bg_ext = "png"
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
                background-size: cover;
                background-attachment: fixed;
            }}
            /* TEXTOS BLANCOS */
            .stMarkdown, .stText, h1, h2, h3, h4, p, label {{
                color: #FFFFFF !important;
            }}
            /* INPUTS MÁS CLAROS */
            .stTextInput>div>div>input {{
                color: #000000;
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 8px;
            }}
            .stTextArea>div>div>textarea {{
                color: #000000;
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 8px;
            }}
            /* BOTONES MAGENTA */
            div.stButton > button {{
                background-color: #D81B60;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 8px;
                padding: 0.5rem 1rem;
            }}
            /* FIRMA JOTA LLORET (Pegada abajo a la izquierda) */
            .firma-container {{
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 250px;
                z-index: 999;
                pointer-events: none; /* Para que no estorbe clicks */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        st.warning("⚠️ Sube 'fondo_azul.png' a GitHub.")

    # 2. Mostrar Logo Arriba (Centrado y Responsive)
    try:
        # Usamos columnas para centrarlo y controlar el tamaño
        c1, c2, c3 = st.columns([1, 2, 1]) 
        with c2:
            st.image("logo_arriba.png", use_container_width=True)
    except:
        st.warning("⚠️ Sube 'logo_arriba.png'.")

    # 3. Mostrar Firma Abajo (Con HTML/CSS)
    try:
        with open("firma_abajo.png", "rb") as f:
            encoded_img = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div class="firma-container"><img src="data:image/png;base64,{encoded_img}" width="100%"></div>',
            unsafe_allow_html=True
        )
    except:
        pass # Si no hay firma, no pasa nada

# Ejecutar configuración visual
configurar_diseño()

# --- LÓGICA DEL GENERADOR ---
# (El resto del código técnico sigue igual, solo cambia la interfaz visual)

def dibujar_texto_sombra(draw, xy, texto, fuente, color="white", sombra="black"):
    x, y = xy
    draw.text((x+8, y+8), texto, font=fuente, fill=sombra)
    draw.text((x, y), texto, font=fuente, fill=color)

def dibujar_texto_ajustado(draw, text, font, color, x_start, y_start, max_width, line_spacing=1.1):
    if not text: return y_start
    words = text.split()
    lines = []
    current_line = []
    bbox_font = font.getbbox("Ay")
    font_height = bbox_font[3] - bbox_font[1]
    current_w = 0
    for word in words:
        word_w = font.getlength(word + " ")
        if current_w + word_w <= max_width:
            current_line.append(word)
            current_w += word_w
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_w = font.getlength(word)
    if current_line: lines.append(" ".join(current_line))
    current_y = y_start
    for i, line in enumerate(lines):
        prefix = ""
        if i == 0 and "📍" in text: prefix = "📍 "
        elif i == 0 and "🗓️" in text: prefix = "🗓️ "
        elif i == 0 and "🕒" in text: prefix = "🕒 "
        clean_line = line.replace("📍 ", "").replace("🗓️ ", "").replace("🕒 ", "")
        draw.text((x_start, current_y), prefix + clean_line, font=font, fill=color)
        current_y += font_height * line_spacing
    return current_y + (font_height * 0.5)

if 'paso' not in st.session_state: st.session_state.paso = 1

# ==================== PASO 1: FORMULARIO ====================
if st.session_state.paso == 1:
    st.markdown("### 📝 Ingresa los datos del evento")
    
    st.session_state.titulo = st.text_area("TÍTULO:", "TE INVITA")
    st.session_state.cuerpo = st.text_area("DESCRIPCIÓN:", "Al evento de entrega de la membresía...")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.fecha = st.text_input("FECHA:", "Miércoles, 6 de Agosto")
        st.session_state.hora = st.text_input("HORA:", "18:30")
    with col2:
        st.session_state.lugar_nombre = st.text_input("LUGAR:", "Teatrina de la Casa de la Provincia")
        st.session_state.lugar_dir = st.text_input("DIRECCIÓN:", "(Tomás Ordóñez 8-69)")
        
    st.session_state.foto = st.file_uploader("FOTO DEL EVENTO:", type=["jpg", "png", "jpeg"])

    if st.button("GENERAR FLYER ➡️"):
        if st.session_state.foto:
            st.session_state.paso = 2
            st.rerun()
        else:
            st.error("⚠️ Sube una foto para continuar.")

# ==================== PASO 2: RESULTADO ====================
elif st.session_state.paso == 2:
    st.success("¡Diseño listo!")
    
    with st.expander("🎨 Ajustes de Diseño"):
        color_filtro = st.color_picker("Color Filtro", "#002200")
        opacidad_filtro = st.slider("Opacidad", 0, 255, 120)
        color_tarjeta = st.color_picker("Color Tarjeta", "#2E7D32")

    # PROCESAMIENTO 4K
    canvas_w, canvas_h = 2160, 3840
    imagen_usuario = Image.open(st.session_state.foto).convert("RGBA")
    img = ImageOps.fit(imagen_usuario, (canvas_w, canvas_h), centering=(0.5, 0.5), method=Image.Resampling.LANCZOS)
    
    rgb_filtro = tuple(int(color_filtro.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    overlay = Image.new("RGBA", img.size, rgb_filtro + (opacidad_filtro,))
    img = Image.alpha_composite(img, overlay)
    capa = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(capa)
    
    try:
        f_titulo = ImageFont.truetype("Canaro-ExtraBold.ttf", 220)
        f_cuerpo = ImageFont.truetype("Canaro-Medium.ttf", 90)
        f_info = ImageFont.truetype("Canaro-Medium.ttf", 75) 
        f_info_peq = ImageFont.truetype("Canaro-Medium.ttf", 55)
    except:
        f_titulo = f_cuerpo = f_info = f_info_peq = ImageFont.load_default()

    # Logo Prefectura
    h_logo_p = 700 
    try:
        logo_pref = Image.open("logo_prefectura.png").convert("RGBA")
        ratio = logo_pref.width / logo_pref.height
        logo_pref = logo_pref.resize((int(h_logo_p * ratio), h_logo_p), Image.Resampling.LANCZOS)
        x_logo_p = (canvas_w - logo_pref.width) // 2
        img.paste(logo_pref, (x_logo_p, 50), logo_pref)
    except: pass

    # Textos
    y_texto = 880 
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

    # Tarjeta Info
    w_card = 1200; h_card = 950; y_card = canvas_h - h_card - 750
    margen_derecho_lienzo = 80; x_inicio_tarjeta = canvas_w - w_card - margen_derecho_lienzo
    rgb_t = tuple(int(color_tarjeta.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    draw.rounded_rectangle([x_inicio_tarjeta, y_card, canvas_w - margen_derecho_lienzo, y_card + h_card], radius=60, fill=rgb_t + (230,))
    
    padding_x = 70; padding_y = 70
    margin_x_texto = x_inicio_tarjeta + padding_x; current_y_texto = y_card + padding_y
    max_text_width = w_card - (padding_x * 2)

    current_y_texto = dibujar_texto_ajustado(draw, "📍 " + st.session_state.lugar_nombre, f_info, "white", margin_x_texto, current_y_texto, max_text_width)
    current_y_texto = dibujar_texto_ajustado(draw, st.session_state.lugar_dir, f_info_peq, "white", margin_x_texto, current_y_texto, max_text_width)
    current_y_texto += 40
    current_y_texto = dibujar_texto_ajustado(draw, "🗓️ " + st.session_state.fecha, f_info, "white", margin_x_texto, current_y_texto, max_text_width)
    dibujar_texto_ajustado(draw, "🕒 " + st.session_state.hora, f_info, "white", margin_x_texto, current_y_texto, max_text_width)

    # Logo Visit
    try:
        logo_visit = Image.open("logo_visit.png").convert("RGBA")
        h_visit = 1150
        r_visit = logo_visit.width / logo_visit.height
        logo_visit = logo_visit.resize((int(h_visit * r_visit), h_visit), Image.Resampling.LANCZOS)
        img.paste(logo_visit, (0, canvas_h - h_visit), logo_visit)
    except: pass

    # Mostrar
    img_final = Image.alpha_composite(img, capa).convert("RGB")
    st.image(img_final, caption="Flyer Final", width=400)
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ VOLVER"): st.session_state.paso = 1; st.rerun()
    with c2:
        buf = io.BytesIO()
        img_final.save(buf, format="PNG")
        st.download_button("📥 DESCARGAR", data=buf.getvalue(), file_name="flyer_prefectura.png", mime="image/png")
