import ollama
import os
from rich import print
import streamlit as st

from PyPDF2 import PdfReader
from PIL import Image
import io
import base64

st.title("AntiusDragon Chatbot")

# Tikriname, ar jau yra išsaugota žinučių istorija
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu esi naudingas asistentas ir visada atsakai tik lietuvių kalba."}
    ]

# **Failo įkėlimo funkcija**
uploaded_file = st.file_uploader("Įkelkite failą", type=["txt", "pdf", "jpg", "jpeg", "png", "mp3", "wav"])

file_content = None
file_type = None

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_extension = file_name.split(".")[-1].lower()
    
    if file_extension in ["txt"]:
        file_content = uploaded_file.getvalue().decode("utf-8")
        file_type = "text"
    
    elif file_extension in ["pdf"]:
        pdf_reader = PdfReader(uploaded_file)
        file_content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        file_type = "text"
    
    elif file_extension in ["jpg", "jpeg", "png"]:
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image.save(buffered, format=image.format)
        file_content = base64.b64encode(buffered.getvalue()).decode()
        file_type = "image"
    
    elif file_extension in ["mp3", "wav"]:
        file_content = uploaded_file.getvalue()
        file_type = "audio"

    st.success(f"Failas {file_name} sėkmingai įkeltas.")

# **Pokalbio istorijos rodymas**
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# **Vartotojo įvesties laukelis**
if prompt := st.chat_input("Klausk bet ko..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages = st.session_state.messages.copy()

        # Jei yra įkeltas failas, pridėti jį prie užklausos
        if file_type == "text":
            messages.append({"role": "user", "content": f"Pridedu failo turinį: {file_content}"})
        elif file_type == "image":
            messages.append({"role": "user", "content": "Kas yra šioje nuotraukoje?", "images": [file_content]})
        elif file_type == "audio":
            messages.append({"role": "user", "content": "Kas girdima šiame garso įraše?"})
        
        response = ollama.chat(
            model="llama3.2-vision:90b",
            messages=messages
        )

        reply = response["message"]["content"]
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
