import telebot
import cv2
import numpy as np
import os

# Render ya hosting server se Token uthayega (Security ke liye)
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def analyze_ludo_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Image read nahi ho paayi, kripya clear photo bhejein."

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Red color range detection
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    red_count = cv2.countNonZero(mask_red)

    suggestion = "🎯 **LUDO BOT BEST MOVE:**\n\n"
    
    if red_count > 300:
        suggestion += "1. ⚔️ **Priority 1:** Opponent ki goti cut kar sakte ho toh pehle KILL karo!\n"
        suggestion += "2. 🛡️ **Priority 2:** Safe zone (Star) par apni goti shift karo.\n"
        suggestion += "3. 🚀 **Priority 3:** Home Path ki taraf goti ko aage badhao."
    else:
        suggestion += "1. Gotiyan sahi se scan nahi ho paayi, board ki seedhi photo bhejein.\n"
        suggestion += "2. Agar 6 aaya hai toh naya token open karein."

    return suggestion

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 **Ludo AI Bot Ready Hai!**\n\nGame board ki photo bhejo, main best move batata hoon.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "🔍 Board scan ho raha hai, wait karein...")

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        image_path = "ludo_board.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        result = analyze_ludo_image(image_path)
        bot.reply_to(message, result, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

if __name__ == "__main__":
    print("Bot starting...")
    bot.polling()
