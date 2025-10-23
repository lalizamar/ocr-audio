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

# 💾 Crear carpeta para audios temporales si no existe
try:
    os.mkdir("temp")
except:
    pass

# 🧼 Eliminar audios antiguos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)

# 🗣️ Función de texto a voz
def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text


# 🎀 DISEÑO ESTÉTICO LINDO
st.set_page_config(page_title="🌸 OCR Mágico de Audio", layout="centered", page_icon="🎀")
st.markdown(
    """
    <style>
    body {
        background-color: #fff0f5;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #ffb6c1;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTextInput>div>input {
        border-radius: 10px;
    }
    .stSidebar {
        background-color: #ffe4e1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 🎀 ENCABEZADO
st.image("https://i.imgur.com/jWcqK4i.png", width=200)
st.title("📝✨ OCR Mágico con Audio y Traducción")
st.markdown(
    """
    Convierte imágenes con texto en audio traducido en segundos.  
    Ideal para 📚 apuntes, 🧾 facturas, 📜 documentos y más.  
    ¡Sube una imagen o toma una foto y escucha la magia! 🎧💫
    """
)

# 📸 FUENTE DE IMAGEN
st.markdown("### 📷 Paso 1: Sube o toma una imagen")

cam_ = st.checkbox("📸 Usar cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una foto con tu cámara 📷")
else:
    img_file_buffer = None

bg_image = st.file_uploader("📁 Sube una imagen (JPG/PNG)", type=["png", "jpg", "jpeg"])
text = ""

# 📋 PROCESAMIENTO DE IMAGEN
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='🖼️ Vista previa de la imagen', use_container_width=True)
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    st.success("✅ Imagen cargada correctamente")
    img_cv = cv2.imread(f"{uploaded_file.name}")
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.markdown("### 🔍 Texto detectado:")
    st.write(text)

# 📋 Procesar imagen de cámara si está habilitada
if img_file_buffer is not None:
    st.markdown("### 🎞️ Procesando foto tomada...")
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    filtro = st.radio("🎨 Aplicar Filtro a la imagen", ('Con Filtro', 'Sin Filtro'))
    if filtro == 'Con Filtro':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.markdown("### 🔍 Texto detectado:")
    st.write(text)


# 🔤 PARÁMETROS DE TRADUCCIÓN Y AUDIO
st.markdown("### 🌐 Paso 2: Traduce y escucha tu texto")

with st.expander("🎚️ Parámetros de idioma y voz"):

    translator = Translator()

    in_lang = st.selectbox("🌍 Idioma del texto detectado:", ("Español", "Inglés", "Japonés", "Mandarín", "Coreano", "Bengalí"))
    out_lang = st.selectbox("🎧 Idioma de salida para el audio:", ("Español", "Inglés", "Japonés", "Mandarín", "Coreano", "Bengalí"))
    accent = st.selectbox("🎙️ Acento del audio (si aplica)", ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"))

    lang_dict = {
        "Español": "es", "Inglés": "en", "Japonés": "ja", "Mandarín": "zh-cn",
        "Coreano": "ko", "Bengalí": "bn"
    }

    tld_dict = {
        "Default": "com", "India": "co.in", "United Kingdom": "co.uk",
        "United States": "com", "Canada": "ca", "Australia": "com.au",
        "Ireland": "ie", "South Africa": "co.za"
    }

    input_language = lang_dict[in_lang]
    output_language = lang_dict[out_lang]
    tld = tld_dict[accent]

    show_text = st.checkbox("📄 Mostrar texto traducido antes de reproducir")

# ▶️ BOTÓN PARA CONVERTIR
if st.button("✨ Convertir a Audio"):
    if text.strip() == "":
        st.warning("⚠️ No se detectó texto para convertir.")
    else:
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.success("✅ Audio generado exitosamente")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if show_text:
            st.markdown("### 📜 Texto traducido:")
            st.write(output_text)

