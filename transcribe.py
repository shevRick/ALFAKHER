import streamlit as st
import whisper
from io import BytesIO
from moviepy.editor import VideoFileClip

# Load the Whisper model
model = whisper.load_model("base")

def extract_audio_from_video(video_file):
    # Load video file using moviepy
    video = VideoFileClip(video_file)
    
    # Extract the audio
    audio = video.audio
    audio_file = "extracted_audio.wav"
    audio.write_audiofile(audio_file, codec='pcm_s16le')  # Save as WAV
    
    return audio_file

# Streamlit app
st.title("Audio/Video Transcription with Whisper")

st.write("Upload an audio or video file (MP4) and get its transcription using OpenAI's Whisper model.")

# File uploader
uploaded_file = st.file_uploader("Choose an audio or video file...", type=["mp3", "wav", "m4a", "flac", "mp4"])

if uploaded_file is not None:
    # Handle MP4 file separately by extracting audio
    if uploaded_file.name.endswith(".mp4"):
        with st.spinner("Extracting audio from video..."):
            audio_file_path = extract_audio_from_video(uploaded_file)
    else:
        audio_file_path = uploaded_file

    # Transcribe the audio file
    with st.spinner("Transcribing..."):
        result = model.transcribe(audio_file_path)
        transcription = result['text']

    # Display the transcription
    st.header("Transcription:")
    st.write(transcription)
