import streamlit as st
import whisper
from io import BytesIO

# Load the Whisper model
model = whisper.load_model("base")

# Streamlit app
st.title("Audio Transcription with Whisper")

st.write("Upload an audio file and get its transcription using OpenAI's Whisper model.")

# File uploader
uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "wav", "m4a", "flac"])

if uploaded_file is not None:
    # Load the audio file
    audio_bytes = uploaded_file.read()
    audio_buffer = BytesIO(audio_bytes)

    # Transcribe the audio file
    with st.spinner("Transcribing..."):
        result = model.transcribe(audio_buffer)
        transcription = result['text']

    # Display the transcription
    st.header("Transcription:")
    st.write(transcription)
