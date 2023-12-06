# filename: translator_app.py
import streamlit as st
from googletrans import LANGUAGES, Translator


def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text


if __name__ == "__main__":
    st.title("Basic Translator App")
    st.subheader("Enter text to translate:")

    text = st.text_area(label="Text", value="", height=200, max_chars=200)

    target_language = st.selectbox("Select target language:", list(LANGUAGES.values()))

    if st.button("Translate"):
        translated_text = translate_text(text, target_language)
        st.write("Translated Text:")
        st.write(translated_text)
