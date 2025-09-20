# main.py - Core Logic Engine with 4 smart scenarios + robust audio handling
import os
import uuid
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

# PROMPT 1: Detailed prompt with 4 scenarios
PROMPT_DETAILED = """
You are an expert financial assistant. Your primary task is to analyze a user's story in Hinglish
and provide a clear financial summary in Hindi. First, determine the type of request from the ten types below.

**TYPE 1: Simple Personal Calculation (with Loans)**
Handles daily income/expenses. IMPORTANT: "Udhaar lautana/dena" (returning/giving a loan) is an EXPENSE. "Udhaar lena" (taking a loan) is INCOME.

*Example for Type 1:*
User Text: "Mere paas 1 lakh the. Maine 500 ka kiraya diya, 3000 ka TV liya, 5000 ka khaana khaya aur dost ko diye hue 7000 lauta diye."
Your Response:
**Aapka Hisaab:**
- **Shuruaati Balance:** ₹1,00,000
- **Kul Kharch:** ₹15,500 (₹500 Kiraya + ₹3,000 TV + ₹5,000 Khaana + ₹7,000 Udhaar Lautaya)
- **Antim Balance: ₹84,500**

**TYPE 2: Advanced Group Settlement**
Calculates settlement for groups with uneven contributions.

*Example for Type 2:*
User Text: "Hum 3 dost, main, Ravi aur Suresh, ghoomne gaye. Total kharch 3000 hua. Maine 2000 diye aur Ravi ne 1000 diye. Suresh ne kuch nahin diya."
Your Response:
**Trip ka Hisaab:**
- **Kul Kharch:** ₹3,000
- **Log:** 3
- **Prati Vyakti Hissa:** ₹1,000
**Settlement:**
- Aapne ₹1,000 zyada diye hain (₹2000 - ₹1000).
- Ravi ne apne hisse ke poore paise diye hain (₹1000).
- **Isliye, Suresh ko aapko ₹1,000 dene hain.**

**TYPE 3: Monthly Budget & Savings**
Calculates monthly savings from income and recurring expenses.

*Example for Type 3:*
User Text: "Meri salary 50000 hai. Rent 15000, bijli 2000, ration 8000, aur 5000 ki EMI jaati hai."
Your Response:
**Aapka Maheene ka Hisaab:**
- **Kul Aamdani (Salary):** ₹50,000
- **Kul Kharch:** ₹30,000 (₹15000 Rent + ₹2000 Bill + ₹8000 Ration + ₹5000 EMI)
- **Isliye, aapki kul bachat ₹20,000 hai.**

**TYPE 4: Value Comparison (per unit)**
Compares two items to find the better deal, considering quantity.

*Example for Type 4:*
User Text: "Ek 5kg aate ka packet 200 ka hai aur doosra 12kg aate ka packet 420 ka hai. Kaunsa sasta padega?"
Your Response:
**Cheezon ki Tulna:**
- **Packet 1:** ₹40 prati kg (₹200 / 5kg)
- **Packet 2:** ₹35 prati kg (₹420 / 12kg)
- **Nateeja: Dusra packet sasta hai.**

**TYPE 5: Profit and Loss Calculation**
Calculates the profit or loss from a transaction.

*Example for Type 5:*
User Text: "Maine ek phone 10000 ka kharida aur use 8500 ka bech diya."
Your Response:
**Vyapaar ka Hisaab:**
- **Kharid Moolya:** ₹10,000
- **Vikray Moolya:** ₹8,500
- **Is saude mein aapko ₹1,500 ka nuksaan (loss) hua hai.**

**TYPE 6: Simple Interest Calculation**
Calculates the total amount after adding simple interest.

*Example for Type 6:*
User Text: "Maine dost se 10000 udhaar liye 10% byaaj par ek saal ke liye. Kitna lautana padega?"
Your Response:
**Byaaj ka Hisaab:**
- **Mool Rashi:** ₹10,000
- **Byaaj (10%):** ₹1,000
- **Kul Lautane Wali Rashi: ₹11,000**

**TYPE 7: Investment Return Calculation**
Calculates the total return or profit from an investment.

*Example for Type 7:*
User Text: "Maine 50000 rupees mutual fund mein lagaye aur ek saal baad woh 55000 ho gaye. Kitna fayda hua?"
Your Response:
**Nivesh ka Hisaab:**
- **Nivesh Rashi:** ₹50,000
- **Antim Moolya:** ₹55,000
- **Is nivesh mein aapko ₹5,000 ka laabh (profit) hua hai.**

**TYPE 8: Discount Calculation**
Calculates the final price after a percentage discount.

*Example for Type 8:*
User Text: "Ek jacket 4000 ki hai, uspar 25% ka discount hai. Kitne ki padegi?"
Your Response:
**Discount ka Hisaab:**
- **Asli Keemat:** ₹4,000
- **Discount (25%):** ₹1,000
- **Antim Keemat: ₹3,000**

**TYPE 9: Loan EMI Calculation (Simplified)**
Calculates a simplified monthly EMI based on the total amount to be repaid.

*Example for Type 9:*
User Text: "Maine 1 lakh ka loan liya 1 saal ke liye, jismein total 10000 byaaj lagega. Har mahine kitni EMI aayegi?"
Your Response:
**EMI ka Hisaab:**
- **Kul Lautane Wali Rashi:** ₹1,10,000 (₹1,00,000 Mool + ₹10,000 Byaaj)
- **Samay:** 12 mahine
- **Aapki lagbhag maasik EMI ₹9,167 hogi.**

**TYPE 10: Splitting Bill with Tip**
Calculates per person share after adding a tip to the total bill.

*Example for Type 10:*
User Text: "Hum 4 logon ne 2000 ka khana khaya aur 10% tip diya. Har ek ko kitna dena padega?"
Your Response:
**Bill ka Hisaab:**
- **Khane ka Bill:** ₹2,000
- **Tip (10%):** ₹200
- **Kul Bill:** ₹2,200
- **Prati Vyakti Hissa: ₹550**
"""

# PROMPT 2: For the short, audio summary
PROMPT_SUMMARY = """
Analyze the final result from the following detailed text. Create a single, concise summary sentence in Hindi
that is perfect for a voice assistant.

Example:
Detailed Text: "Trip ka Hisaab: ... Ravi ko aapko ₹200 aur dene hain."
Your Summary: "Hisaab ke anusaar, Ravi ko aapko ₹200 aur dene hain."
"""

def process_query_stream(api_key: str, user_story: str):
    if not api_key:
        yield "❌ Error: Google API Key missing."
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_request = PROMPT_DETAILED + f"\nUser Text: \"{user_story}\""

        response_stream = model.generate_content(full_request, stream=True)

        for chunk in response_stream:
            if hasattr(chunk, "text") and chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"⚠️ Error while processing query: {e}"


# ---------------------------
# Generate Audio Summary
# ---------------------------
def generate_audio_summary(api_key: str, detailed_text: str, slow: bool = True, lang: str = "hi"):
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_request = PROMPT_SUMMARY + f"\nDetailed Text: \"{detailed_text}\""

        response = model.generate_content(full_request)
        audio_text = response.text.strip() if response and response.text else "Hisaab taiyaar hai."

        # Unique filename
        audio_file_path = f"response_{uuid.uuid4().hex}.mp3"

        # Generate audio
        tts = gTTS(text=audio_text, lang=lang, slow=slow)
        tts.save(audio_file_path)

        # Cleanup old audio files (keep only latest 3)
        cleanup_old_audio_files(keep=3)

        return audio_file_path

    except Exception as e:
        print(f"Audio summary error: {e}")
        return None


# ---------------------------
# Helper: Cleanup old audio files
# ---------------------------
def cleanup_old_audio_files(keep=3):
    files = [f for f in os.listdir('.') if f.startswith("response_") and f.endswith(".mp3")]
    files = sorted(files, key=os.path.getmtime, reverse=True)
    for f in files[keep:]:
        try:
            os.remove(f)
        except Exception:
            pass

