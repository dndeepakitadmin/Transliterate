import os
import streamlit as st
from pptx import Presentation
from pptx.util import Pt
from docx import Document
import pandas as pd
from deep_translator import GoogleTranslator
from indic_transliteration.sanscript import transliterate, KANNADA, DEVANAGARI, TELUGU, HK

# ------------------------------
# LANGUAGE + SCRIPT CONFIG
# ------------------------------
script_codes = {
    "Kannada": KANNADA,
    "Hindi (Devanagari)": DEVANAGARI,
    "Marathi (Devanagari)": DEVANAGARI,
    "Telugu": TELUGU,
    "English (HK)": HK
}

# ISO Language Codes for deep_translator
translation_lang_codes = {
    "Kannada": "kn",
    "Hindi (Devanagari)": "hi",
    "Marathi (Devanagari)": "mr",
    "Telugu": "te",
    "English (HK)": "en"
}

# ------------------------------
# TRANSLITERATION + TRANSLATION
# ------------------------------
def transliterate_text(text, source_script, target_script):
    try:
        return transliterate(text, source_script, target_script)
    except Exception as e:
        return f"(Transliteration Error: {str(e)})"

def translate_text(text, target_lang_code):
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(text)
    except Exception as e:
        return f"(Translation Error: {str(e)})"

# ------------------------------
# FILE PROCESSING FUNCTIONS
# ------------------------------
def process_pptx(uploaded_file, source_script, target_script, target_lang_code):
    prs = Presentation(uploaded_file)
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                lines = shape.text_frame.text.split('\n')
                shape.text_frame.clear()
                for line in lines:
                    if not line.strip():
                        continue
                    translit_line = transliterate_text(line, source_script, target_script)
                    translated_line = translate_text(line, target_lang_code)

                    para1 = shape.text_frame.add_paragraph()
                    run1 = para1.add_run()
                    run1.text = translit_line
                    run1.font.size = Pt(32)

                    para2 = shape.text_frame.add_paragraph()
                    run2 = para2.add_run()
                    run2.text = translated_line
                    run2.font.size = Pt(32)

                    shape.text_frame.add_paragraph().text = ""  # spacing

    output_path = "output_translated.pptx"
    prs.save(output_path)
    return output_path


def process_docx(uploaded_file, source_script, target_script, target_lang_code):
    doc = Document(uploaded_file)
    new_doc = Document()

    for para in doc.paragraphs:
        line = para.text.strip()
        if not line:
            continue
        translit_line = transliterate_text(line, source_script, target_script)
        translated_line = translate_text(line, target_lang_code)

        new_doc.add_paragraph(translit_line)
        new_doc.add_paragraph(translated_line)
        new_doc.add_paragraph("")  # spacing

    output_path = "output_translated.docx"
    new_doc.save(output_path)
    return output_path


def process_excel_csv(uploaded_file, source_script, target_script, target_lang_code, ext):
    if ext in [".xls", ".xlsx"]:
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    for col in df.columns:
        df[col] = df[col].astype(str).apply(
            lambda x: f"{transliterate_text(x, source_script, target_script)}\n{translate_text(x, target_lang_code)}"
        )

    output_path = "output_translated.xlsx" if ext in [".xls", ".xlsx"] else "output_translated.csv"
    if ext in [".xls", ".xlsx"]:
        df.to_excel(output_path, index=False)
    else:
        df.to_csv(output_path, index=False)
    return output_path


def process_txt(uploaded_file, source_script, target_script, target_lang_code):
    text = uploaded_file.read().decode("utf-8").splitlines()
    output_path = "output_translated.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        for line in text:
            line = line.strip()
            if not line:
                continue
            translit_line = transliterate_text(line, source_script, target_script)
            translated_line = translate_text(line, target_lang_code)
            f.write(translit_line + "\n")
            f.write(translated_line + "\n\n")

    return output_path

# ------------------------------
# STREAMLIT UI
# ------------------------------
st.set_page_config(page_title="Multi-Language Transliterator + Translator", layout="wide")
st.title("🌍 Multi-Language Transliterator + Translator")

uploaded_file = st.file_uploader("📂 Upload a file", type=["pptx", "docx", "xlsx", "xls", "csv", "txt"])
source_lang = st.selectbox("Select Source Language", list(script_codes.keys()))
target_lang = st.selectbox("Select Target Language", list(script_codes.keys()))

if st.button("🚀 Transliterate + Translate"):
    if not uploaded_file:
        st.warning("Please upload a file first.")
    elif source_lang == target_lang:
        st.warning("Source and target languages must be different.")
    else:
        with st.spinner("Processing... Please wait ⏳"):
            source_script = script_codes[source_lang]
            target_script = script_codes[target_lang]
            target_lang_code = translation_lang_codes[target_lang]
            ext = os.path.splitext(uploaded_file.name)[-1].lower()

            try:
                if ext == ".pptx":
                    output_path = process_pptx(uploaded_file, source_script, target_script, target_lang_code)
                elif ext == ".docx":
                    output_path = process_docx(uploaded_file, source_script, target_script, target_lang_code)
                elif ext in [".xls", ".xlsx", ".csv"]:
                    output_path = process_excel_csv(uploaded_file, source_script, target_script, target_lang_code, ext)
                elif ext == ".txt":
                    output_path = process_txt(uploaded_file, source_script, target_script, target_lang_code)
                else:
                    st.error("Unsupported file format.")
                    st.stop()

                st.success("✅ Translation + Transliteration completed!")
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download Result", f, file_name=output_path)

            except Exception as e:
                st.error(f"❌ Error: {e}")
