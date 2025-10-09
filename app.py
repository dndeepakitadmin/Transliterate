import os
import pandas as pd
from pptx import Presentation
from pptx.util import Pt
from docx import Document
from googletrans import Translator
from indic_transliteration.sanscript import transliterate, KANNADA, DEVANAGARI, TELUGU, HK
import streamlit as st

translator = Translator()

# --- Language Mappings ---
script_codes = {
    "Kannada": KANNADA,
    "Hindi (Devanagari)": DEVANAGARI,
    "Marathi (Devanagari)": DEVANAGARI,
    "Telugu": TELUGU,
    "English (HK)": HK
}

translation_lang_codes = {
    "Kannada": "kn",
    "Hindi (Devanagari)": "hi",
    "Marathi (Devanagari)": "mr",
    "Telugu": "te",
    "English (HK)": "en"
}

# --- Functions ---
def transliterate_text(text, source_script, target_script):
    try:
        return transliterate(text, source_script, target_script)
    except Exception as e:
        return f"(Error: {str(e)})"

def translate_text(text, target_lang):
    try:
        return translator.translate(text, dest=target_lang).text
    except Exception as e:
        return f"(Translation Error: {str(e)})"

def process_txt(content, source_script, target_script, target_lang):
    out_lines = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        translit = transliterate_text(line, source_script, target_script)
        trans = translate_text(line, target_lang)
        out_lines.append(f"{translit}\n{trans}\n")
    return "\n".join(out_lines)

# --- Streamlit App ---
st.set_page_config(page_title="Multilingual Transliterator + Translator", layout="wide")
st.title("🌐 Multi-Language Transliterator + Translator")

st.markdown("Convert any text or file between Indian scripts + get translations instantly!")

source_lang = st.selectbox("Select Source Language", list(script_codes.keys()))
target_lang = st.selectbox("Select Target Language", list(script_codes.keys()))

uploaded_file = st.file_uploader("Upload a file (txt, docx, pptx, xlsx, csv)", type=["txt", "docx", "pptx", "xlsx", "xls", "csv"])
process_btn = st.button("🔄 Transliterate + Translate")

if process_btn and uploaded_file:
    source_script = script_codes[source_lang]
    target_script = script_codes[target_lang]
    target_lang_code = translation_lang_codes[target_lang]

    file_name = uploaded_file.name.lower()
    st.info("Processing... Please wait ⏳")

    try:
        if file_name.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
            output_text = process_txt(text, source_script, target_script, target_lang_code)
            st.download_button("⬇️ Download Translated TXT", output_text, file_name.replace(".txt", f"_{target_lang}.txt"))
            st.text_area("Preview", output_text, height=300)

        else:
            st.warning("Currently only .txt supported online (due to Streamlit sandbox limits). Use desktop version for DOCX/PPTX/EXCEL.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
