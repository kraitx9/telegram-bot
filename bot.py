import os
import telebot
from flask import Flask
import threading

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 البوت شغال تمام!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎉 البوت شغال على Render!")

def run_bot():
    print("🚀 البوت بدأ يشتغل...")
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()
    app.run(host='0.0.0.0', port=10000)
