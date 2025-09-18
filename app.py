# app.py - The final version with limited audio autoplay
import streamlit as st
import speech_recognition as sr
import os
from dotenv import load_dotenv
from main import process_query_stream, generate_audio_summary

load_dotenv()

# --- Helper function for Speech-to-Text (No changes here) ---
def recognize_voice():
    """Microphone se voice ko recognize karke text mein badalta hai."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Aap bolna shuru kar sakte hain...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        with st.spinner("Aawaz ko process kiya jaa raha hai..."):
            query = r.recognize_google(audio, language='hi-IN')
        st.success("Aapki aawaz text mein badal gayi hai.")
        return query
    except sr.UnknownValueError:
        st.error("Maaf kijiye, main aapki aawaz samajh nahi paya.")
        return None
    except sr.RequestError:
        st.error("Speech service se connect nahi ho pa raha hai.")
        return None

# --- Streamlit App UI ---
st.set_page_config(page_title="Hisaab Assistant", page_icon="💡", layout="centered")

st.title("💡 Smart Hisaab Assistant")
st.markdown("Apna hisaab likhein ya bol kar batayein, aur turant jawab paayein.")

# --- NEW: Initialize session state for autoplay counter and user input ---
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'play_count' not in st.session_state:
    st.session_state.play_count = 0

st.session_state.user_input = st.text_area(
    "Apna hisaab yahan likhein...",
    value=st.session_state.user_input,
    height=120
)

col1, col2 = st.columns(2)

with col1:
    if st.button("🎙️ Bol Kar Batayein", use_container_width=True):
        recognized_text = recognize_voice()
        if recognized_text:
            st.session_state.user_input = recognized_text
            st.rerun()

with col2:
    if st.button("🧮 Hisaab Lagayein", type="primary", use_container_width=True):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        final_query = st.session_state.user_input

        if not google_api_key:
            st.error("Error: GOOGLE_API_KEY .env file mein nahi mili.")
        elif not final_query:
            st.warning("Kripya pehle apna hisaab likhein ya record karein.")
        else:
            st.success("Hisaab Taiyaar Hai!")
            
            response_generator = process_query_stream(google_api_key, final_query)
            full_response = st.write_stream(response_generator)
            
            with st.spinner("Audio banayi jaa rahi hai..."):
                audio_path = generate_audio_summary(google_api_key, full_response)
                if audio_path:
                    # --- NEW LOGIC: Check the play count for autoplay ---
                    should_autoplay = st.session_state.play_count < 2
                    
                    st.audio(audio_path, autoplay=should_autoplay)
                    
                    # Increment the counter after displaying the audio
                    st.session_state.play_count += 1
                    
                    os.remove(audio_path)

