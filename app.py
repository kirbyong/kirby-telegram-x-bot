from flask import Flask, request
import telebot
import tweepy
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Telegram Bot Setup
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN is not set")
    raise ValueError("TELEGRAM_TOKEN is not set")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
logger.info("Telegram bot initialized")

# X API Setup
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    logger.error("X API credentials are incomplete")
    raise ValueError("X API credentials are incomplete")

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
x_api = tweepy.API(auth)
logger.info("X API initialized")

# Handle Telegram Updates
@bot.channel_post_handler(content_types=['text'])
def handle_channel_post(message):
logger.info(f"Received channel post from chat ID: {message.chat.id}, message: {message.text}")

if str(message.chat.id) == os.getenv('CHAT_ID'):
    post_text = f"New update from my Telegram channel: {message.text}"
    try:
        x_api.update_status(post_text)
        logger.info(f"Posted to X: {post_text}")
    except Exception as e:
        logger.error(f"Error posting to X: {e}")
else:
    logger.warning("Chat ID does not match; message ignored.")

# Flask Route for Telegram Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update_json = request.get_json()
        print(update_json)  # TEMP: print raw Telegram update

        update = telebot.types.Update.de_json(update_json)
        if update.channel_post:
            print("✅ Incoming channel post!")
            print("📢 Channel ID:", update.channel_post.chat.id)
            print("📝 Message Text:", update.channel_post.text)
        else:
            print("⚠️ Not a channel post:", update_json)

        bot.process_new_updates([update])
        return 'OK', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error', 500

if __name__ == '__main__':
    try:
        bot.remove_webhook()
        webhook_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/webhook"
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
        app.run(host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
