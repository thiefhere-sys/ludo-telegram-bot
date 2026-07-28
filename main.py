import os
import time
from threading import Thread
import telebot
from google import genai
from PIL import Image
from flask import Flask

# -------------------------------------------------------------
# 1. Fake Web Server (Render Free Tier Active Rakhne Ke Liye)
# -------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Universal AI Game Master Bot is Live & Running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# -------------------------------------------------------------
# 2. API Setup & Credentials
# -------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------------------------------------------
# 3. Smart Vision Engine with Fallback & Error Handling
# -------------------------------------------------------------
def analyze_game_board(image_path):
    image = Image.open(image_path)
    
    prompt = (
        "You are an expert World-Class Grandmaster Game Analyst trained for maximum winning accuracy in all board games. "
        "Examine this board image carefully and follow these rules:\n\n"
        "1. First, identify the exact game (e.g., Chess, Ludo, Carrom, Tic-Tac-Toe, Sudoku, etc.).\n"
        "2. Carefully scan piece/token positions and board situation.\n"
        "3. Determine the absolute BEST NEXT MOVE that guarantees maximum winning probability (100% winning tactic).\n"
        "4. Format your response strictly in clean Hinglish (Hindi + English) as follows:\n\n"
        "🎮 **GAME DETECTED:** [Game Name]\n\n"
        "🎯 **100% BEST MOVE:**\n"
        "[Exact piece/token to move and target position]\n\n"
        "⚔️ **WHY THIS MOVE:**\n"
        "[Tactical advantage, e.g., Attack/Defense/Cutting opponent/Safe spot]\n\n"
        "🏆 **WINNING STRATEGY:**\n"
        "[Next 1-2 steps to force a win]\n\n"
        "Keep the reply concise, sharp, direct, and encouraging."
    )

    # Primary Try: gemini-1.5-flash (Highest free rate limit)
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[image, prompt]
        )
        return response.text
    except Exception as e1:
        print(f"Gemini 1.5 Flash limit/error: {e1}")
        
        # Backup Try: gemini-2.0-flash
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[image, prompt]
            )
            return response.text
        except Exception as e2:
            print(f"Gemini 2.0 Flash limit/error: {e2}")
            if "429" in str(e2) or "429" in str(e1):
                return "⏳ **Google AI Free Limit Hit!**\n\nAapne 1 minute me zyada photos bhej di hain. Kripya **45-60 seconds wait karein** aur phir se photo bhejein."
            return f"⚠️ Board scan karne me problem aayi: {str(e2)}"

# -------------------------------------------------------------
# 4. Telegram Message Handlers
# -------------------------------------------------------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎮 **UNIVERSAL AI GAME MASTER BOT READY!** 🎮\n\n"
        "Main **Chess, Ludo, Carrom** ya kisi bhi board game ko scan karke 100% winning moves bata sakta hoon!\n\n"
        "📸 Bas apne game board ki clear photo click karke mujhe bhejien."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(
            message, 
            "🧠 **AI Board Scan Kar Raha Hai...**\n"
            "⚡ 100% Winning Move Calculate Ho Rahi Hai, Wait Karein! ⏳"
        )

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        image_path = "temp_game_board.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        analysis_result = analyze_game_board(image_path)
        bot.reply_to(message, analysis_result, parse_mode="Markdown")

        if os.path.exists(image_path):
            os.remove(image_path)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# -------------------------------------------------------------
# 5. Main Execution Loop
# -------------------------------------------------------------
if __name__ == "__main__":
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("Bot is starting polling loop...")
    
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=20)
        except Exception as e:
            print(f"Polling Exception Caught: {e}")
            time.sleep(3)
