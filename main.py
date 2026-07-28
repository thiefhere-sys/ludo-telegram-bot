import os
from threading import Thread
import telebot
from google import genai
from PIL import Image
from flask import Flask

# 1. Fake Web Server for Render Free Tier
app = Flask(__name__)

@app.route('/')
def home():
    return "Universal AI Game Master Bot is Running Live!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Bot & Gemini API Setup
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# 3. Gemini Vision AI Game Analyzer
def analyze_game_board(image_path):
    try:
        image = Image.open(image_path)
        
        prompt = (
            "You are an expert World-Class Grandmaster Game Analyst trained for 100% winning accuracy in board games. "
            "Examine this image carefully and follow these rules:\n\n"
            "1. First, identify the game (e.g., Chess, Ludo, Carrom, Tic-Tac-Toe, Sudoku, etc.).\n"
            "2. Carefully scan the board positions, pieces, or tokens.\n"
            "3. Give the absolute BEST NEXT MOVE that guarantees maximum winning probability (100% winning tactic).\n"
            "4. Format your response strictly in simple Hinglish (Hindi + English) like this:\n\n"
            "🎮 **GAME DETECTED:** [Game Name]\n\n"
            "🎯 **100% BEST MOVE:**\n"
            "[Exact piece/token to move and target position]\n\n"
            "⚔️ **WHY THIS MOVE:**\n"
            "[Short tactical advantage]\n\n"
            "🏆 **WINNING STRATEGY:**\n"
            "[Next steps to win]\n\n"
            "Keep the reply concise, sharp, direct, and encouraging."
        )

        # Updated model name here
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[image, prompt]
        )
        return response.text

    except Exception as e:
        return f"⚠️ Board scan karne me problem aayi: {str(e)}"

# 4. Telegram Handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎮 **UNIVERSAL AI GAME MASTER BOT READY!** 🎮\n\n"
        "Main Chess, Ludo, Carrom ya kisi bhi board game ko scan karke 100% winning moves bata sakta hoon!\n\n"
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

        image_path = "game_board.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        analysis_result = analyze_game_board(image_path)
        bot.reply_to(message, analysis_result, parse_mode="Markdown")

        if os.path.exists(image_path):
            os.remove(image_path)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# 5. Main Execution
if __name__ == "__main__":
    server_thread = Thread(target=run_web_server)
    server_thread.start()
    
    print("Bot starting...")
    bot.polling(non_stop=True)
