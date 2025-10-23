# -*- coding: utf-8 -*-
# OCR → Audio Kawaii — Mantiene el flujo del profesor con UI creativa
# Requisitos: streamlit, opencv-python-headless, numpy, pytesseract, pillow, gTTS, googletrans

import os, time, glob, io, base64
from datetime import datetime

import streamlit as st
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
from PIL import Image, ImageOps
from gtts import gTTS
from googletrans import Translator

# -------------------------------------------------------------------
# 0) Utilidades base del profe (TEMP + limpieza)  →  NO TOCAR
# -------------------------------------------------------------------
os.makedirs("temp", exist_ok=True)

def remove_files(n=7):
    mp3_files = glob.glob("temp/*.mp3")
    if mp3_files:
        now = time.time()
        limit = n * 86400
        for f in mp3_files:
            try:
                if os.stat(f).st_mtime < now - limit:
                    os.remove(f)
            except Exception:
                pass

remove_files(7)

# -------------------------------------------------------------------
# 1) Tema kawaii con MÚLTIPLES PALETAS (selector)
# -------------------------------------------------------------------
st.set_page_config(page_title="OCR → Audio (Cute Edition)", page_icon="✨", layout="centered")

PALETTES = {
    "Rosa Sakura 🌸": {
        "--bg1": "#fff5fb", "--bg2": "#ffe6f0",
        "--card": "rgba(255,255,255,0.92)",
        "--accent": "#ff91c1", "--accent-2": "#ffd1e6",
        "--text": "#111", "--chip": "#ffe0ef", "--shadow": "0 14px 38px rgba(255,145,193,.25)"
    },
    "Lavanda Leche 💜": {
        "--bg1": "#fefcff", "--bg2": "#eee8ff",
        "--card": "rgba(255,255,255,0.92)",
        "--accent": "#8a6bff", "--accent-2": "#d8ceff",
        "--text": "#111", "--chip": "#ece6ff", "--shadow": "0 14px 38px rgba(138,107,255,.22)"
    },
    "Menta Peach 🍑": {
        "--bg1": "#f7fff9", "--bg2": "#ffeede",
        "--card": "rgba(255,255,255,0.92)",
        "--accent": "#2fbf71", "--accent-2": "#b8f2cf",
        "--text": "#111", "--chip": "#e7fff0", "--shadow": "0 14px 38px rgba(47,191,113,.22)"
    },
}

with st.sidebar:
    st.markdown("## 🎀 Estilo")
    theme_name = st.selectbox("Paleta kawaii", list(PALETTES.keys()), index=0)
    show_sparkles = st.toggle("✨ Efectos (confetti al generar audio)", value=True)
    st.markdown("---")
    st.markdown("## 📸 Fuente de imagen")
    cam_ = st.checkbox("Usar cámara", value=False, key="use_cam_kawaii")
    st.markdown("---")
    st.markdown("## 🧪 Filtro para cámara")
    filtro = st.radio("Aplicar filtro invertido", ('Sí', 'No'), index=1, key="filtro_cam")

P = PALETTES[theme_name]

# CSS que SÍ aplica a los contenedores de Streamlit
st.markdown(f"""
<style>
/* Fondo pastel degradado en el contenedor principal */
[data-testid="stAppViewContainer"] {{
  background: linear-gradient(180deg, {P['--bg1']} 0%, {P['--bg2']} 100%) !important;
}}
/* Sidebar suave */
[data-testid="stSidebar"] > div:first-child {{
  background: transparent !important;
}}
[data-testid="stSidebarContent"] {{
  background: {P['--card']};
  border: 2px solid {P['--accent-2']};
  border-radius: 18px;
  padding: .6rem .8rem;
  box-shadow: {P['--shadow']};
}}
/* Tipografía y color global */
h1, h2, h3, label, p, span, div {{
  color: {P['--text']} !important;
}}
/* Tarjetas glass */
.card {{
  background: {P['--card']};
  border: 2px solid {P['--accent-2']};
  border-radius: 22px;
  padding: 1rem 1.1rem;
  box-shadow: {P['--shadow']};
  backdrop-filter: blur(6px);
}}
/* Chips pastel */
.chip {{
  display:inline-flex; align-items:center; gap:.4rem;
  padding:.35rem .7rem; border-radius:999px; font-weight:700; font-size:.8rem;
  background:{P['--chip']}; color:{P['--text']};
  border:1.5px solid {P['--accent-2']}; margin-right:.25rem;
}}
/* Botones jelly */
div.stButton > button {{
  background: {P['--accent']}; color: #fff; font-weight:800;
  border: none; border-radius: 18px; padding: .7rem 1.2rem;
  box-shadow: 0 10px 18px rgba(0,0,0,.08); transition: transform .06s ease, filter .2s ease;
}}
div.stButton > button:hover {{ transform: translateY(-1px); filter: brightness(1.06); }}
/* Inputs */
.stTextArea textarea, .stTextInput input, .stSelectbox [data-baseweb="select"]>div {{
  border-radius: 14px !important; border: 2px solid {P['--accent-2']} !important;
}}
/* Audio ancho */
.stAudio audio {{ width: 100% !important; }}
/* Divider jelly */
.divider {{
  width:100%; height:12px; border-radius:999px; opacity:.65; margin: .8rem 0 1rem 0;
  background: linear-gradient(90deg, {P['--accent']}, {P['--accent-2']});
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2) Cabecera creativa (SVG inline, cero enlaces rotos)
# -------------------------------------------------------------------
SVG_BANNER = f"""
<svg viewBox="0 0 680 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g1" x1="0" x2="1">
      <stop stop-color="{P['--accent-2']}" />
      <stop offset="1" stop-color="{P['--bg2']}" />
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="680" height="120" rx="18" fill="url(#g1)" opacity="0.55"/>
  <!-- Mascota mini: gatito lector -->
  <g transform="translate(28,25)">
    <ellipse cx="38" cy="38" rx="36" ry="28" fill="#fff"/>
    <path d="M20 28 L30 10 L34 30 Z" fill="#fff"/>
    <path d="M56 28 L46 10 L42 30 Z" fill="#fff"/>
    <circle cx="32" cy="38" r="5" fill="#111"/><circle cx="46" cy="38" r="5" fill="#111"/>
    <path d="M32 50 Q39 56 46 50" stroke="#111" stroke-width="3" fill="none"/>
    <rect x="22" y="58" width="32" height="10" rx="3" fill="{P['--accent']}"/><line x1="38" y1="58" x2="38" y2="68" stroke="#fff"/>
  </g>
  <text x="130" y="48" font-size="22" fill="#111" font-family="Arial Black">OCR mágico → texto → audio</text>
  <text x="130" y="86" font-size="14" fill="#111" font-family="Arial">Convierte imágenes en voz en segundos</text>
</svg>
"""
st.markdown(f'<div class="card">{SVG_BANNER}</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.markdown("### ¿Qué hace esta interfaz?")
st.write(
    "- **1)** Captura o sube una **imagen con texto**.\n"
    "- **2)** (Opcional) Aplica un **filtro invertido** si la foto sale oscura.\n"
    "- **3)** **OCR** (Tesseract) extrae el **texto editable**.\n"
    "- **4)** **Traduce** y convierte el resultado a **audio (gTTS)**.\n"
)
st.markdown('<div class="chip">📸 Cámara</div> <div class="chip">🖼️ Upload</div> <div class="chip">🔤 OCR</div> <div class="chip">🌍 Traducción</div> <div class="chip">🔊 TTS</div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3) Entrada de imagen — MISMO FLUJO DEL PROFE (no rompemos cámara)
# -------------------------------------------------------------------
st.markdown("## 📷 Paso 1: Sube o toma una imagen")
img_file_buffer = st.camera_input("Toma una Foto", key="camera_widget") if cam_ else None
bg_image = st.file_uploader("📁 Sube una imagen (PNG/JPG)", type=["png", "jpg", "jpeg"], key="uploader_widget")

text = ""  # texto OCR

# Ruta A: archivo subido
if bg_image is not None and img_file_buffer is None:
    st.image(bg_image, caption="🖼 Vista previa", use_container_width=True)
    bytes_data = bg_image.read()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.success("✅ Texto detectado desde imagen subida.")

# Ruta B: cámara
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    if st.sidebar.session_state.get("filtro_cam") == "Sí":
        cv2_img = cv2.bitwise_not(cv2_img)        # Filtro del profesor
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    st.image(img_rgb, caption="📸 Captura (vista previa)", use_container_width=True)
    text = pytesseract.image_to_string(img_rgb)
    st.success("✅ Texto detectado desde cámara.")

# Mostrar texto OCR (si hay)
if text.strip():
    st.markdown("### 📝 Texto reconocido")
    st.text_area("Resultado", value=text, height=200, key="ocr_out_area")

# -------------------------------------------------------------------
# 4) Parámetros de traducción y voz (sidebar, como el profe)
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🌍 Parámetros de traducción")
    # Diccionario de lenguajes (igual estructura que el profe)
    in_lang = st.selectbox("Idioma del texto de entrada", ("Ingles", "Español", "Bengali", "koreano", "Mandarin", "Japones"), index=1)
    out_lang = st.selectbox("Idioma de salida (audio)", ("Ingles", "Español", "Bengali", "koreano", "Mandarin", "Japones"), index=0)

    def lang_code(label):
        return {
            "Ingles": "en", "Español": "es", "Bengali": "bn",
            "koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"
        }[label]

    input_language = lang_code(in_lang)
    output_language = lang_code(out_lang)

    english_accent = st.selectbox("Acento (tld)", (
        "Default","India","United Kingdom","United States","Canada","Australia","Ireland","South Africa"
    ), index=0)

    TLD = {
        "Default": "com", "India": "co.in", "United Kingdom": "co.uk",
        "United States": "com", "Canada": "ca", "Australia": "com.au",
        "Ireland": "ie", "South Africa": "co.za"
    }[english_accent]

    display_output_text = st.checkbox("Mostrar texto traducido", value=True)

# -------------------------------------------------------------------
# 5) Traducción + TTS — MISMO FONDO LÓGICO DEL PROFE (pero robusto)
# -------------------------------------------------------------------
def text_to_speech(input_language, output_language, text, tld):
    """Traduce con googletrans y convierte con gTTS. (no depende de globales)"""
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    my_file_name = (text[:20] or "audio").strip().replace(" ", "_")
    path = f"temp/{my_file_name}_{datetime.now().strftime('%H%M%S')}.mp3"
    tts.save(path)
    return path, trans_text

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("## 🔊 Paso 2: Traduce y escucha tu texto")

btn = st.button("🎙️ Convertir a Audio", type="primary", use_container_width=False)
if btn:
    if not text.strip():
        st.warning("⚠️ Primero sube o captura una imagen con texto.")
    else:
        try:
            path, out_text = text_to_speech(input_language, output_language, text, TLD)
            with open(path, "rb") as f:
                audio_bytes = f.read()

            st.success("✨ ¡Audio generado!")
            st.audio(audio_bytes, format="audio/mp3")

            st.download_button("⬇️ Descargar MP3", data=audio_bytes,
                               file_name=os.path.basename(path), mime="audio/mpeg")

            # Autoplay sutil
            b64 = base64.b64encode(audio_bytes).decode()
            st.markdown(f'<audio controls autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)

            if display_output_text:
                st.markdown("### 📜 Texto traducido")
                st.text_area("Salida", value=out_text, height=150)

            if show_sparkles:
                st.balloons()
        except Exception as e:
            st.error("No fue posible traducir o generar el audio.")
            st.caption(f"Detalle técnico: {e}")

# -------------------------------------------------------------------
# 6) Extra opcional: mostrar cajas OCR (para aprender)
# -------------------------------------------------------------------
with st.expander("🔎 Ver palabras detectadas (experimental)"):
    try:
        if text.strip() and 'img_rgb' in locals():
            data = pytesseract.image_to_data(img_rgb, lang=input_language, output_type=Output.DICT)
            overlay = img_rgb.copy()
            for i, t in enumerate(data["text"]):
                conf = int(data["conf"][i]) if str(data["conf"][i]).isdigit() else -1
                if t and conf > 50:
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    cv2.rectangle(overlay, (x, y), (x+w, y+h), (255, 105, 180), 2)  # rosa
            st.image(overlay, caption="Cajas de OCR", use_column_width=True)
        else:
            st.caption("Sube una imagen o usa la cámara para ver detecciones.")
    except Exception:
        st.caption("No se pudieron dibujar las cajas esta vez.")

# -------------------------------------------------------------------
# 7) Tip útil final
# -------------------------------------------------------------------
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption("Tip: para mejores resultados, usa buena luz y mantén el documento lo más recto posible. Si la foto sale oscura, activa el filtro invertido en la barra lateral.")
