import streamlit as st
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from main1 import process_query_stream, generate_audio_summary
import os

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
    
    # The component returns a dictionary with audio info
    audio_info = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording", key='recorder')
    
    # Check if the dictionary and the 'bytes' key exist
    if audio_info and audio_info['bytes']:
        # Use audio_info['bytes'] to get the raw audio data
        st.audio(audio_info['bytes'], format="audio/wav")
        
        # Process the audio bytes to convert to text
        r = sr.Recognizer()
        try:
            # Save audio bytes to a temporary file
            with open("audio.wav", "wb") as f:
                f.write(audio_info['bytes'])
            
            # Use the temporary file as the audio source
            with sr.AudioFile("audio.wav") as source:
                audio_data = r.record(source)
            
            # Recognize the speech
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
# (This section remains unchanged)
# ---------------------------
if user_story:
    st.subheader("📊 Detailed Hisaab")
    api_key = os.getenv("GOOGLE_API_KEY")

    # Display spinner while processing
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

