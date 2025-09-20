import streamlit as st
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from main1 import process_query_stream, generate_audio_summary
import os
import io  # In-memory file handling ke liye zaroori
from pydub import AudioSegment  # Audio conversion ke liye zaroori

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="💰 Hissab Assistant", layout="centered")

st.title("💰 Hissab Assistant")
st.write("Apni kahani bolkar ya likhkar bhejiye, main aapka hisaab nikal dunga.")

# Input mode selection
mode = st.radio("Input kaise dena chahte ho:", ["🎤 Voice", "⌨️ Text"], horizontal=True)

user_story = None

if mode == "🎤 Voice":
    st.write("Record karne ke liye start par click karein aur bolna shuru karein. Bolna khatm hone par stop par click karein.")
    
    audio_info = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", key='recorder')
    
    if audio_info and audio_info['bytes']:
        st.audio(audio_info['bytes'])
        
        r = sr.Recognizer()
        try:
            # Browser se aaye audio bytes ko memory mein load karein
            audio_bytes = audio_info['bytes']
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # Audio ko sahi WAV format mein memory mein convert karein
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)  # Buffer ko shuru mein le jaayein
            
            # Memory mein bani WAV file ko source ke roop mein istemal karein
            with sr.AudioFile(wav_io) as source:
                audio_data = r.record(source)
            
            # Aawaz ko text mein badlein
            recognized_text = r.recognize_google(audio_data, language='hi-IN')
            st.success(f"📝 Aapne kaha: {recognized_text}")
            user_story = recognized_text

        except sr.UnknownValueError:
            st.warning("Maaf kijiye, main aapki aawaz samajh nahin paya. Kripya dobara koshish karein.")
        except sr.RequestError as e:
            st.error(f"Google Speech Recognition service se connect nahin ho paya; {e}")
        except Exception as e:
            st.error(f"Audio process karte samay error aaya: {e}")

else:
    user_story = st.text_area("Apni kahani likhiye:", placeholder="Example: Ravi aur main movie gaye...")

# ---------------------------
# Process Query
# (Yah section bilkul waisa hi rahega)
# ---------------------------
if user_story:
    st.subheader("📊 Detailed Hisaab")
    api_key = os.getenv("GOOGLE_API_KEY")

    with st.spinner('Hisaab lagaya ja raha hai...'):
        placeholder = st.empty()
        detailed_text = ""
        for chunk in process_query_stream(api_key, user_story):
            detailed_text += chunk
            placeholder.write(detailed_text)

    # ---------------------------
    # Audio Summary
    # ---------------------------
    if detailed_text:
        st.subheader("🔊 Audio Summary")
        with st.spinner('Audio summary banaya ja raha hai...'):
            audio_file = generate_audio_summary(api_key, detailed_text, slow=False, lang="hi")
            if audio_file and os.path.exists(audio_file):
                st.audio(audio_file, format="audio/mp3")
            else:
                st.warning("Audio summary generate nahi ho paya.")

