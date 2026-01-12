import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap

st.set_page_config(page_title="Flyer 4K Final V7", layout="centered")

# --- FUNCIÓN AUXILIAR 1: Sombra ---
def dibujar_texto_sombra(draw, xy, texto, fuente, color="white", sombra="black"):
    x, y = xy
    draw.text((x+8, y+8), texto, font=fuente, fill=sombra)
    draw.text((x, y), texto, font=fuente, fill=color)

# --- FUNCIÓN AUXILIAR 2: AJUSTE AUTOMÁTICO DE TEXTO ---
# Esta es la clave para que no se salga del recuadro.
# Mide el texto y si es muy largo, lo baja a la siguiente línea.
def dibujar_texto_ajustado(draw, text, font, color, x_start, y_start, max_width, line_spacing=1.1):
    if not text: return y_start
    
    words = text.split()
    lines = []
    current_line = []
    
    # Obtener altura de la fuente
    bbox_font = font.getbbox("Ay")
    font_height = bbox_font[3] - bbox_font[1]

    # Lógica para dividir en líneas según el ancho disponible
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

    # Dibujar las líneas calculadas
    current_y = y_start
    for i, line in enumerate(lines):
        # Si es la primera línea, añade el icono (si existe)
        prefix = ""
        if i == 0 and "📍" in text: prefix = "📍 "
        elif i == 0 and "🗓️" in text: prefix = "🗓️ "
        elif i == 0 and "🕒" in text: prefix = "🕒 "
        
        # Limpiamos el texto de iconos para dibujarlo bien
        clean_line = line.replace("📍 ", "").replace("🗓️ ", "").replace("🕒 ", "")
        
        # Dibujar
        draw.text((x_start, current_y), prefix + clean_line, font=font, fill=color)
        current_y += font_height * line_spacing
        
    # Devolver la nueva posición Y para el siguiente bloque
    return current_y + (font_height * 0.5) # Un pequeño espacio extra al final

if 'paso' not in st.session_state: st.session_state.paso = 1

st.title("💎 Generador 4K (Texto Ajustado en Tarjeta)")

# ==================== PASO 1: DATOS ====================
if st.session_state.paso == 1:
    st.header("1. Ingresa los datos")
    st.info("ℹ️ El texto dentro de la tarjeta ahora se ajustará automáticamente si es muy largo.")
    
    st.session_state.titulo = st.text_area("TÍTULO PRINCIPAL:", "TE INVITA")
    st.session_state.cuerpo = st.text_area("Descripción:", "Al evento de entrega de la membresía a la Red Mundial de Destinos Turísticos del Cacao.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.fecha = st.text_input("Fecha:", "Miércoles, 6 de Agosto")
        st.session_state.hora = st.text_input("Hora:", "18:30")
    with col2:
        st.session_state.lugar_nombre = st.text_input("Lugar (Nombre):", "Teatrina de la Casa de la Provincia del Azuay")
        st.session_state.lugar_dir = st.text_input("Dirección:", "(Tomás Ordóñez 8-69 y Simón Bolívar esquina)")
        
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
    
    rgb_filtro = tuple(int(color_filtro.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    overlay = Image.new("RGBA", img.size, rgb_filtro + (opacidad_filtro,))
    img = Image.alpha_composite(img, overlay)
    capa = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(capa)
    
    # 2. FUENTES 4K
    try:
        f_titulo = ImageFont.truetype("Canaro-ExtraBold.ttf", 220)
        f_cuerpo = ImageFont.truetype("Canaro-Medium.ttf", 90)
        f_info = ImageFont.truetype("Canaro-Medium.ttf", 75) 
        f_info_peq = ImageFont.truetype("Canaro-Medium.ttf", 55)
    except:
        st.error("⚠️ Fuentes no encontradas.")
        f_titulo = f_cuerpo = f_info = f_info_peq = ImageFont.load_default()

    # 3. LOGO PREFECTURA
    h_logo_p = 700 
    try:
        logo_pref = Image.open("logo_prefectura.png").convert("RGBA")
        ratio = logo_pref.width / logo_pref.height
        logo_pref = logo_pref.resize((int(h_logo_p * ratio), h_logo_p), Image.Resampling.LANCZOS)
        x_logo_p = (canvas_w - logo_pref.width) // 2
        img.paste(logo_pref, (x_logo_p, 50), logo_pref)
    except: pass

    # 4. TEXTOS PRINCIPALES
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

    # 5. TARJETA INFO (CON AJUSTE AUTOMÁTICO DE TEXTO)
    w_card = 1200
    h_card = 950
    y_card = canvas_h - h_card - 750
    margen_derecho_lienzo = 80
    x_inicio_tarjeta = canvas_w - w_card - margen_derecho_lienzo
    
    rgb_t = tuple(int(color_tarjeta.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    draw.rounded_rectangle(
        [x_inicio_tarjeta, y_card, canvas_w - margen_derecho_lienzo, y_card + h_card], 
        radius=60, fill=rgb_t + (230,)
    )
    
    # Definir márgenes internos y ancho máximo para el texto
    padding_x = 70
    padding_y = 70
    margin_x_texto = x_inicio_tarjeta + padding_x
    current_y_texto = y_card + padding_y
    # El ancho máximo permitido para el texto es el ancho de la tarjeta menos los márgenes internos
    max_text_width = w_card - (padding_x * 2)

    # --- DIBUJAR TEXTOS USANDO LA NUEVA FUNCIÓN ---
    # La función devuelve la nueva posición Y donde debe empezar el siguiente bloque
    
    # Bloque Lugar
    current_y_texto = dibujar_texto_ajustado(draw, "📍 " + st.session_state.lugar_nombre, f_info, "white", margin_x_texto, current_y_texto, max_text_width)
    # Bloque Dirección
    current_y_texto = dibujar_texto_ajustado(draw, st.session_state.lugar_dir, f_info_peq, "white", margin_x_texto, current_y_texto, max_text_width)
    
    # Añadimos un poco de espacio extra antes de la fecha
    current_y_texto += 40
    
    # Bloque Fecha
    current_y_texto = dibujar_texto_ajustado(draw, "🗓️ " + st.session_state.fecha, f_info, "white", margin_x_texto, current_y_texto, max_text_width)
    # Bloque Hora
    dibujar_texto_ajustado(draw, "🕒 " + st.session_state.hora, f_info, "white", margin_x_texto, current_y_texto, max_text_width)

    # 6. LOGO VISIT AZUAY
    h_visit = 1150 
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
