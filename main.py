# main.py - The Final Core Logic Engine with 4 smart scenarios
import os
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

# PROMPT 1: THE FINAL, "EXPERT" PROMPT WITH 4 SCENARIOS
PROMPT_DETAILED = """
You are an expert financial assistant. Your primary task is to analyze a user's story in Hinglish and provide a clear financial summary in Hindi. First, determine the type of request from the four types below.

**TYPE 1: Simple Personal Calculation**
If the story is about one person's income and daily expenses, calculate the final balance or total expense.

*Example for Type 1:*
User Text: "30 rp bus ke, 250 ka khana, 500 ki shirt"
Your Response: Aapke kul kharch is prakaar hain:
- Bus: ₹30
- Khana: ₹250
- Shirt: ₹500
**Kul Kharch: ₹830**

**TYPE 2: Group Trip Settlement**
If the story is about settling expenses among multiple friends, calculate the total cost, share per person, and the final settlement.

*Example for Type 2:*
User Text: "Hum 2 dost, main aur Ravi, movie gaye. Maine tickets ke 600 kharch kiye. Ravi ne 100 de diye."
Your Response:
**Trip ka Hisaab:**
- **Kul Kharch:** ₹600
- **Log:** 2
- **Prati Vyakti Hissa:** ₹300
**Settlement:**
- Ravi ne ₹100 diye hain, jabki unka hissa ₹300 hai.
- **Isliye, Ravi ko aapko ₹200 aur dene hain.**

**TYPE 3: Monthly Budget & Savings**
If the story is about monthly income and recurring expenses, calculate the total monthly savings.

*Example for Type 3:*
User Text: "Meri monthly salary 30000 hai. Ghar ka kiraya 10000, bijli ka bill 2000, aur 5000 ka ration aata hai. To kitni bachat hoti hai?"
Your Response:
**Aapka Maheene ka Hisaab:**
- **Kul Aamdani (Salary):** ₹30,000
- **Kul Kharch:** ₹17,000 (₹10000 Kiraya + ₹2000 Bill + ₹5000 Ration)
- **Isliye, aapki kul bachat ₹13,000 hai.**

**TYPE 4: Price Comparison**
If the story is about comparing the price of two items, calculate the price difference and state which one is cheaper.

*Example for Type 4:*
User Text: "Ek mobile 15000 ka hai aur doosra 12500 ka hai. Kaunsa sasta hai aur kitna?"
Your Response:
**Cheezon ki Tulna:**
- Dusra mobile pehle waale se sasta hai.
- **Dono ke beech ₹2,500 ka antar hai.**
"""

# PROMPT 2: For the short, audio summary (This remains the same and works for all types)
PROMPT_SUMMARY = """
Analyze the final result from the following detailed text. Create a single, concise summary sentence in Hindi that is perfect for a voice assistant.

Example:
Detailed Text: "Trip ka Hisaab: ... Ravi ko aapko ₹200 aur dene hain."
Your Summary: "Hisaab ke anusaar, Ravi ko aapko ₹200 aur dene hain."
"""

def process_query_stream(api_key: str, user_story: str):
    """
    This function STREAMS the detailed LLM response chunk by chunk.
    """
    if not api_key:
        yield "Error: Google API Key is missing."
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_request = PROMPT_DETAILED + "\nUser Text: \"" + user_story + "\""
        
        response_stream = model.generate_content(full_request, stream=True)

        for chunk in response_stream:
            yield chunk.text

    except Exception as e:
        yield f"An error occurred: {e}"

def generate_audio_summary(api_key: str, detailed_text: str):
    """
    This function uses the free gTTS library with a slower voice for clarity.
    """
    if not api_key:
        return "Error: Google API Key is missing."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_request = PROMPT_SUMMARY + "\nDetailed Text: \"" + detailed_text + "\""
        response = model.generate_content(full_request)
        audio_text = response.text

        tts = gTTS(text=audio_text, lang='hi', slow=True)
        audio_file_path = "response.mp3"
        tts.save(audio_file_path)
        return audio_file_path

    except Exception as e:
        print(f"Audio summary error: {e}")
        return None

