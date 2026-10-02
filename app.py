import os
from threading import Thread
from flask import Flask
import telebot

# ----------------------------------------------
# ១. បង្កើត Flask App សម្រាប់ Keep-Alive
# ----------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is alive!"

def run_flask():
    # Render នឹងបញ្ជូន PORT មកតាម Environment Variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ----------------------------------------------
# ២. Telegram Bot Logic
# ----------------------------------------------
# យក BOT_TOKEN ពី Environment Variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "សួស្ដី! Telegram Bot របស់អ្នកកំពុងដំណើរការ ២៤/៧។")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"អ្នកបានផ្ញើ៖ {message.text}")

# ----------------------------------------------
# ៣. រត់ Web Server និង Bot ព្រមគ្នា
# ----------------------------------------------
if __name__ == "__main__":
    # រត់ Flask server លើ Thread ផ្សេងដើម្បីកុំឱ្យ Blocking Bot
    t = Thread(target=run_flask)
    t.start()
    
    # រត់ Bot Polling
    print("Bot starting...")
    bot.infinity_polling()