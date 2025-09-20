import streamlit as st
import speech_recognition as sr
from main1 import process_query_stream, generate_audio_summary
import os

# ---------------------------
# Voice Recognition (safe)
# ---------------------------
def recognize_voice():
    r = sr.Recognizer()
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            st.warning("⚠️ No microphone detected. Please type your query instead.")
            return None

        # Use first available mic
        with sr.Microphone() as source:
            st.info(f"🎤 Using mic: {mic_list[0]}")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)

        return r.recognize_google(audio, language='hi-IN')

    except Exception as e:
        st.error(f"Mic error: {e}. Switching to text input mode.")
        return None


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
    if st.button("🎙️ Record Voice"):
        recognized_text = recognize_voice()
        if recognized_text:
            st.success(f"📝 Aapne kaha: {recognized_text}")
            user_story = recognized_text
        else:
            st.warning("Voice input fail hua. Kripya text box use karein.")
else:
    user_story = st.text_area("Apni kahani likhiye:", placeholder="Example: Ravi aur main movie gaye...")

# ---------------------------
# Process Query
# ---------------------------
if user_story:
    st.subheader("📊 Detailed Hisaab")
    api_key = os.getenv("GOOGLE_API_KEY")

    detailed_text = ""
    for chunk in process_query_stream(api_key, user_story):
        st.write(chunk)
        detailed_text += chunk

    # ---------------------------
    # Audio Summary
    # ---------------------------
    if detailed_text:
        st.subheader("🔊 Audio Summary")
        audio_file = generate_audio_summary(api_key, detailed_text, slow=True, lang="hi")
        if audio_file and os.path.exists(audio_file):
            st.audio(audio_file, format="audio/mp3")
        else:
            st.warning("Audio summary generate nahi ho paya.")