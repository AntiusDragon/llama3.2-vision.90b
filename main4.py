import ollama
import os

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import queue
import time

from rich import print
import streamlit as st

from PyPDF2 import PdfReader
from PIL import Image
import io
import base64

import wave

st.title("Antano Chatbot")

# **Nustatymai**
TRIGGER_WORD = "hi"
SILENCE_DURATION = 2 # seconds
q = queue.Queue()

# **Mikrofono callback funkcija**
def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(indata.copy())

# **Laukia žodžio "hi"**
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Laukia komandos...")
        while True:
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                if TRIGGER_WORD in command:
                    st.write("Komanda aptikta! Pradeda klausytis...")
                    return True
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                st.write("Nepavyko pasiekti atpažinimo paslaugos.")
                break
    return False

# ...existing code...

def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(indata.copy())
    # Pridėkime diagnostikos informaciją
    st.write(f"Received {len(indata)} frames of audio data")
    st.write(f"Audio data: {indata}")
    
# **Įrašo vartotojo kalbą**
def record_speech():
    samplerate = 16000
    channels = 1
    duration = 30

    with sd.InputStream(callback=callback, samplerate=samplerate, channels=channels):
        audio_data = []
        silence_counter = 0
        start_time = time.time()
        st.write("Pradėkite kalbėti...")

        while True:
            try:
                data = q.get()
                audio_data.append(data)

                if np.max(np.abs(data)) < 0.01:
                    silence_counter += 1
                else:
                    silence_counter = 0

                if silence_counter > SILENCE_DURATION * samplerate / 1024:
                    st.write("Įrašymas baigtas.")
                    break

                if time.time() - start_time > duration:
                    st.write("Įrašymo laiko limitas pasiektas.")
                    break

            except KeyboardInterrupt:
                break

    audio_np = np.concatenate(audio_data, axis=0)
    st.write(f"Total frames recorded: {len(audio_np)}")
    st.write(f"Max amplitude: {np.max(np.abs(audio_np))}")
    audio_data_bytes = audio_np.tobytes()

    # Išsaugokime įrašytą garsą į failą
    with wave.open("recorded_audio.wav", "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(samplerate)
        wf.writeframes(audio_data_bytes)

    # Patikrinkime įrašytą garsą
    st.audio(audio_data_bytes, format='audio/wav')

    # Pridėkime diagnostikos informaciją
    st.write(f"Audio data bytes length: {len(audio_data_bytes)}")
    st.write(f"Audio data bytes: {audio_data_bytes[:100]}")  # Rodyti pirmus 100 baitų

    # Pridėkime diagnostikos informaciją apie audio_source
    audio_source = sr.AudioData(audio_data_bytes, samplerate, 2)
    st.write(f"AudioData sample width: {audio_source.sample_width}")
    st.write(f"AudioData frame rate: {audio_source.sample_rate}")
    st.write(f"AudioData frame count: {len(audio_data_bytes) // (audio_source.sample_width * channels)}")

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # Lower the energy threshold for better recognition
    try:
        # Normalize audio data
        audio_data_normalized = np.frombuffer(audio_data_bytes, dtype=np.int16) / 32768.0
        audio_data_bytes_normalized = (audio_data_normalized * 32768).astype(np.int16).tobytes()
        audio_source_normalized = sr.AudioData(audio_data_bytes_normalized, samplerate, 2)
        
        st.write("Normalized audio data bytes:", audio_data_bytes_normalized[:100])  # Log first 100 bytes of normalized data

        text = recognizer.recognize_google(audio_source_normalized, language="lt-LT")
        st.write("Jūs pasakėte:", text)
        return text
    except sr.UnknownValueError:
        st.write("Nepavyko atpažinti kalbos. Patikrinkite, ar kalbate aiškiai ir garsiai.")
    except sr.RequestError as e:
        st.write(f"Nepavyko susisiekti su atpažinimo serveriu: {e}")
    except Exception as e:
        st.write(f"Įvyko klaida: {e}")
        st.write(f"Error details: {str(e)}")

    return None



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        # {"role": "assistant", "content": "Tu esi naudingas asistentas ir visada atcakai tik lietuvių kalba."}
        {"role": "system", "content": "Tu esi naudingas asistentas ir visada atsakai tik lietuvių kalba."}
        # {
        #     "role": "system",
        #     "content": (
        #         "Tu esi naudingas žmogus ir visada atsakai tik lietuvių kalba."
        #         # "Atrašai tik tai kas yra butina, ir kuo mažiau informacijos."
        #         # "Turi bendrauti gražei jei taves neižeidineja."
        #         "Jei tave ižeidžia, ar negražiai rašo tu atrašai tik viena varijanta iš pateikto sarašo arba panašiai: atciknisk asile, ko nori iš manes, eik velniopt, atciknisk, tu mulkis, tu asilas, ko man rašai, aik velniopt, supuvusi varle.."
        #     )
        # }
        # {
        #     "role": "system",
        #     "content": (
        #         "Tu esi naudingas asistentas ir visada atsakai tik lietuvių kalba.\n"
        #         "Nuotraukos apačioje yra juodas fonas per visą nuotraukos plotį su baltu tekstu. "
        #         "Tekstas prasideda nuo žodžių „Camera Info“, o po jų eina papildoma informacija. "
        #         "Nuskaityk visą tekstą nuo „Camera Info“ iki pabaigos ir pateik jį man tiksliai taip, kaip jis parašytas."
        #     )
        # }
    ]

# **Failo įkėlimo funkcija**
uploaded_file = st.file_uploader("Įkelkite failą", type=["txt", "pdf", "jpg", "jpeg", "png", "mp3", "wav"])

file_name = None
file_type = None
file_content = None # priedas

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

    st.success(f"Failas {file_name} sėkmingai įkeltas. Tipas: {file_type}")

# Pokalbio istorijos rodimas
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# **Klausymas iš mikrofono**
if st.button("Pradėti klausymą"):
    if listen_for_command():
        spoken_text = record_speech()
        if spoken_text:
            st.session_state.messages.append({"role": "user", "content": spoken_text})
            st.chat_message("user").markdown(spoken_text)
            
# Accept user input
if prompt := st.chat_input("Klausk bet ko..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages=st.session_state.messages.copy()

        # jei yra įkeltas failas, pridedame jį užklauosos
        if file_type == "text":
            messages.append({"role": "user", "content": f"Pridedu failo turinį: {file_content}"})
        elif file_type == "pdf":
            messages.append({"role": "user", "content": f"Kas yra šiame PDF faile: {file_content}"})
        elif file_type == "image":
            messages.append({"role": "user", "content": f"Pateik informacija apie šia nuotrauka", "images": [file_content]})
            # messages.append({"role": "user", "content": f"Kas yra šioje nuotraukoje?", "images": [file_content]})
            # messages.append({"role": "user", "content": f"Nuotraukos apačioje yra juodas fonas per visą nuotraukos plotį su baltu tekstu. Tekstas prasideda nuo žodžių „Camera Info“, o po jų eina papildoma informacija. Nuskaityk visą tekstą nuo „Camera Info“ iki pabaigos ir pateik jį man tiksliai taip, kaip jis parašytas.", "images": [file_content]})
        elif file_type == "audio":
            messages.append({"role": "user", "content": f"Kas girrdima šiame garso įraše?: {file_content}"}) 
         
        response = ollama.chat(
            model="llama3.2-vision:90b",
            messages=messages
        )

        reply = response["message"]["content"]
        st.markdown(reply)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": reply})