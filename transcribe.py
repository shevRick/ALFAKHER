import streamlit as st
import whisperx
from io import BytesIO
from moviepy.editor import VideoFileClip
import tempfile
import os
from pydub import AudioSegment

# Load the WhisperX model
model = whisperx.load_model("base")

def extract_audio_from_video(video_file):
    # Create a temporary file to save the uploaded video file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_file.getbuffer())
        temp_video_path = temp_video_file.name

    # Load video file using moviepy
    video = VideoFileClip(temp_video_path)
    
    # Extract the audio
    audio_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    video.audio.write_audiofile(audio_file_path, codec='pcm_s16le')  # Save as WAV

    # Clean up the temporary video file
    video.close()
    os.remove(temp_video_path)
    
    return audio_file_path

def convert_to_wav(input_path):
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path

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
        # Save the uploaded audio file as a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
            temp_audio_file.write(uploaded_file.getbuffer())
            audio_file_path = temp_audio_file.name

    # Convert to WAV format if necessary
    with st.spinner("Converting audio to WAV format..."):
        audio_file_path = convert_to_wav(audio_file_path)

    # Transcribe the audio file
    with st.spinner("Transcribing..."):
        result = model.transcribe(audio_file_path)
        transcription = result['text']

    # Clean up the temporary audio file
    os.remove(audio_file_path)

    # Display the transcription
    st.header("Transcription:")
    st.write(transcription)
