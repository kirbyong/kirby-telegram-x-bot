from flask import Flask, request
import telebot
import tweepy
import os

app = Flask(__name__)

# Telegram Bot Setup
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# X API Setup
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
x_api = tweepy.API(auth)

# Handle Telegram Updates
@bot.channel_post_handler(content_types=['text'])
def handle_channel_post(message):
    if str(message.chat.id) == os.getenv('CHAT_ID'):
        post_text = f"New update from my Telegram channel: {message.text}"
        try:
            x_api.update_status(post_text)
            print(f"Posted to X: {post_text}")
        except Exception as e:
            print(f"Error posting to X: {e}")

# Flask Route for Telegram Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return 'OK', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/webhook")
    app.run(host='0.0.0.0', port=8000)
