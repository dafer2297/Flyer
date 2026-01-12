import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

st.set_page_config(page_title="Generador Flyer Canaro", layout="centered")

# --- FUNCIÓN PARA TEXTO CON SOMBRA (Para que se lea bien) ---
def dibujar_texto_sombra(draw, xy, texto, fuente, color="white", sombra="black"):
    x, y = xy
    # Dibuja sombra (desplazada 3 pixeles)
    draw.text((x+3, y+3), texto, font=fuente, fill=sombra)
    # Dibuja texto real
    draw.text((x, y), texto, font=fuente, fill=color)

if 'paso' not in st.session_state: st.session_state.paso = 1

st.title("🎨 Generador de Flyers (Estilo Canaro)")

# ==================== PASO 1: DATOS ====================
if st.session_state.paso == 1:
    st.header("1. Ingresa los datos")
    st.info("💡 Tip: Sube una foto vertical para que el diseño cuadre perfecto.")

    st.session_state.titulo = st.text_area("TÍTULO DEL EVENTO (Ej: TE INVITA):", "TE INVITA")
    st.session_state.cuerpo = st.text_area("Descripción Principal:", "Al evento de entrega de la membresía a la Red Mundial de Destinos Turísticos del Cacao.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.fecha = st.text_input("Fecha:", "Miércoles, 6 de Agosto")
        st.session_state.hora = st.text_input("Hora:", "18:30")
    with col2:
        st.session_state.lugar_nombre = st.text_input("Lugar (Nombre):", "Teatrina de la Casa de la Provincia")
        st.session_state.lugar_dir = st.text_input("Dirección:", "(Tomás Ordóñez 8-69 y Simón Bolívar)")
        
    st.session_state.foto = st.file_uploader("Sube tu FOTO VERTICAL:", type=["jpg", "png", "jpeg"])

    if st.button("Generar Diseño ➡️", type="primary"):
        if st.session_state.foto:
            st.session_state.paso = 2
            st.rerun()
        else:
            st.error("⚠️ Falta subir la foto.")

# ==================== PASO 2: DISEÑO ====================
elif st.session_state.paso == 2:
    st.header("2. Resultado Final")
    
    # Colores personalizables
    color_tarjeta = st.sidebar.color_picker("Color Tarjeta Info", "#2E7D32") # Verde oscuro
    
    # 1. CARGAR IMAGEN
    img = Image.open(st.session_state.foto).convert("RGBA")
    ancho, alto = img.size
    capa = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(capa)
    
    # 2. CARGAR FUENTES CANARO (Ajuste automático de tamaño)
    try:
        # ExtraBold para títulos grandes
        f_titulo = ImageFont.truetype("Canaro-ExtraBold.ttf", int(alto * 0.08)) 
        f_invita = ImageFont.truetype("Canaro-ExtraBold.ttf", int(alto * 0.05))
        # Medium para textos de lectura
        f_cuerpo = ImageFont.truetype("Canaro-Medium.ttf", int(alto * 0.03))
        f_info = ImageFont.truetype("Canaro-Medium.ttf", int(alto * 0.025))
        f_info_peq = ImageFont.truetype("Canaro-Medium.ttf", int(alto * 0.02))
    except:
        st.error("⚠️ ERROR DE FUENTES: Asegúrate de que 'Canaro-ExtraBold.ttf' y 'Canaro-Medium.ttf' estén en GitHub.")
        f_titulo = f_invita = f_cuerpo = f_info = f_info_peq = ImageFont.load_default()

    # 3. LOGOS (Parte Superior)
    try:
        # Ajustamos logos al 12% del alto de la imagen
        h_logo = int(alto * 0.12)
        
        # Prefectura (Centro-Arriba o Izquierda según prefieras, la referencia lo tiene arriba)
        # Vamos a ponerlos como en la referencia: Prefectura Arriba Centro
        logo_pref = Image.open("logo_prefectura.png").convert("RGBA")
        ratio = logo_pref.width / logo_pref.height
        logo_pref = logo_pref.resize((int(h_logo * ratio), h_logo))
        x_logo_p = (ancho - logo_pref.width) // 2
        img.paste(logo_pref, (x_logo_p, int(alto*0.02)), logo_pref)
    except: pass

    # 4. TEXTOS PRINCIPALES (TE INVITA + DESCRIPCIÓN)
    y_texto = alto * 0.18 # Empezamos debajo del logo
    
    # Título "TE INVITA"
    bbox = draw.textbbox((0,0), st.session_state.titulo, font=f_titulo)
    w_tit = bbox[2] - bbox[0]
    dibujar_texto_sombra(draw, ((ancho-w_tit)/2, y_texto), st.session_state.titulo, f_titulo)
    
    y_texto += alto * 0.10 # Espacio
    
    # Descripción (Centrada y con saltos de línea automáticos)
    margen_lat = int(ancho * 0.1)
    lineas = textwrap.wrap(st.session_state.cuerpo, width=30) # Ajusta el ancho del texto
    for linea in lineas:
        bbox_l = draw.textbbox((0,0), linea, font=f_cuerpo)
        w_l = bbox_l[2] - bbox_l[0]
        dibujar_texto_sombra(draw, ((ancho-w_l)/2, y_texto), linea, f_cuerpo)
        y_texto += alto * 0.04

    # 5. TARJETA FLOTANTE DE INFORMACIÓN (Esquina Inferior Derecha)
    # Dimensiones de la tarjeta verde
    w_card = ancho * 0.55
    h_card = alto * 0.25
    x_card = ancho * 0.40 # Pegado a la derecha
    y_card = alto * 0.65  # Altura media-baja
    
    # Dibujar rectángulo redondeado verde (Tarjeta)
    rgb = tuple(int(color_tarjeta.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    draw.rounded_rectangle([x_card, y_card, ancho - (ancho*0.05), y_card + h_card], radius=30, fill=rgb + (230,)) # 230 es opacidad
    
    # Contenido de la tarjeta (Iconos simulados con texto o emojis)
    margin_card_x = x_card + (ancho*0.03)
    margin_card_y = y_card + (alto*0.02)
    
    # Fila 1: Lugar
    draw.text((margin_card_x, margin_card_y), "📍 " + st.session_state.lugar_nombre, font=f_info, fill="white")
    draw.text((margin_card_x + 35, margin_card_y + (alto*0.03)), st.session_state.lugar_dir, font=f_info_peq, fill="white")
    
    # Fila 2: Fecha (Separada)
    y_fecha = margin_card_y + (alto*0.08)
    draw.text((margin_card_x, y_fecha), "🗓️ " + st.session_state.fecha, font=f_info, fill="white")
    
    # Fila 3: Hora (Separada)
    y_hora = y_fecha + (alto*0.06)
    draw.text((margin_card_x, y_hora), "🕒 " + st.session_state.hora, font=f_info, fill="white")

    # 6. LOGO VISIT AZUAY (Esquina Inferior Izquierda, grande como referencia)
    try:
        logo_visit = Image.open("logo_visit.png").convert("RGBA")
        h_visit = int(alto * 0.25) # Grande
        r_visit = logo_visit.width / logo_visit.height
        logo_visit = logo_visit.resize((int(h_visit * r_visit), h_visit))
        # Lo pegamos abajo a la izquierda, saliendo un poco si es estilo burbuja
        img.paste(logo_visit, (int(ancho*0.02), int(alto - h_visit - (alto*0.02))), logo_visit)
    except: pass

    # --- RENDER FINAL ---
    img_final = Image.alpha_composite(img, capa).convert("RGB")
    st.image(img_final, caption="Flyer Final", use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ Editar", type="secondary"): st.session_state.paso = 1; st.rerun()
    with c2:
        buf = io.BytesIO()
        img_final.save(buf, format="JPEG", quality=100)
        st.download_button("📥 DESCARGAR IMAGEN", data=buf.getvalue(), file_name="flyer_oficial.jpg", mime="image/jpeg", type="primary")
