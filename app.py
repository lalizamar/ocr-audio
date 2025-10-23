import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Crear carpeta temporal si no existe
try:
    os.mkdir("temp")
except:
    pass

# Limpiar archivos de audio antiguos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

remove_files(7)

# Traducción y conversión de texto a audio
def text_to_speech(input_language, output_language, text, tld):
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20].strip().replace(" ", "_")
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

# Fondo personalizado 🌸
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #ffe6f0, #f7f0ff);
        color: #3d3d3d;
        font-family: 'Comic Sans MS', cursive;
    }
    .stButton>button {
        background-color: #ffc4e1;
        color: black;
        border-radius: 20px;
        padding: 0.5em 2em;
        font-size: 1.1em;
    }
    .st-c5, .st-c6 {
        background-color: #fff0f5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Encabezado principal con estilo ✨
st.markdown("""
# 📄✨ OCR Mágico con Audio y Traducción
Convierte imágenes con texto en audio traducido ✨ Ideal para 📄 apuntes, 📄 facturas y 📄 documentos.  
🎵 Sube una imagen o toma una foto, y escucha la magia. 
""")

# Paso 1️⃣: Subida o captura de imagen
st.markdown("""## 📸 Paso 1: Sube o toma una imagen""")
cam_ = st.checkbox("📷 Usar cámara")
img_file_buffer = st.camera_input("Toma una foto") if cam_ else None
bg_image = st.file_uploader("📁 Sube una imagen (JPG/PNG)", type=["png", "jpg", "jpeg"])

text = ""

if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='🖼 Imagen cargada', use_container_width=True)
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    img_cv = cv2.imread(uploaded_file.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    cv2_img = cv2.bitwise_not(cv2_img) if st.radio("¿Deseas invertir colores?", ('Sí', 'No')) == 'Sí' else cv2_img
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

if text:
    st.success("✅ Texto reconocido exitosamente")
    st.markdown(f"**📋 Texto detectado:**\n\n{text}")

# Paso 2️⃣: Traducción y conversión
st.markdown("""## 🌐 Paso 2: Traduce y escucha tu texto""")
with st.expander("🎧 Parámetros de idioma y voz"):
    translator = Translator()
    in_lang = st.selectbox("🌍 Idioma de entrada", ("Ingles", "Español", "Bengali", "Koreano", "Mandarin", "Japones"))
    input_language = {"Ingles": "en", "Español": "es", "Bengali": "bn", "Koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"}[in_lang]

    out_lang = st.selectbox("🌎 Idioma de salida", ("Ingles", "Español", "Bengali", "Koreano", "Mandarin", "Japones"))
    output_language = {"Ingles": "en", "Español": "es", "Bengali": "bn", "Koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"}[out_lang]

    english_accent = st.selectbox("🎤 Acento del inglés", ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"))
    tld = {"Default": "com", "India": "co.in", "United Kingdom": "co.uk", "United States": "com", "Canada": "ca", "Australia": "com.au", "Ireland": "ie", "South Africa": "co.za"}.get(english_accent, "com")

    display_output_text = st.checkbox("📜 Mostrar texto traducido")

if st.button("🌟 Convertir a Audio"):
    if text:
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("### 🎧 Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("### 📜 Texto traducido:")
            st.write(output_text)
    else:
        st.warning("⚠️ Primero debes subir o capturar una imagen con texto")
