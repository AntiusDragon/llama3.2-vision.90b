import ollama
import os
from rich import print
import streamlit as st

# from PyPDF2 import PdfReader
# from PIL import Image
# import io
# import base64

st.title("AntiusDragon Chatbot")

# Tikriname, ar jau yra išsaugota žinučių istorija
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu esi naudingas asistentas ir visada atsakai tik lietuvių kalba."}
    ]

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
        
        response = ollama.chat(
            model="llama3.2-vision:90b",
            messages=messages
        )

        reply = response["message"]["content"]
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
