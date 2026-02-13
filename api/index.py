# api/index.py
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.error import TelegramError

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

bot = Bot(token=TOKEN)

BAD_WORDS = ["کلمه۱", "کلمه۲", "تست"]  # گسترش بده

@app.route('/', methods=['POST'])
def webhook():
    if request.method == "POST":
        try:
            update_dict = request.get_json(force=True)
            if not update_dict:
                return "No JSON", 400

            update = Update.de_json(update_dict, bot)
            if not update or not update.message:
                return "OK", 200

            msg = update.message
            text = (msg.text or msg.caption or "").lower()
            chat_id = msg.chat_id

            # خوش‌آمدگویی (sync)
            if msg.new_chat_members:
                for member in msg.new_chat_members:
                    welcome = f"سلام {member.full_name} عزیز به گروه وکسوروم خوش آمدی!\n🌐 vaxorum.xyz"
                    bot.send_message(chat_id=chat_id, text=welcome)
                return "OK", 200

            # فیلتر
            is_media = bool(msg.photo or msg.video or msg.document or msg.animation or msg.voice)
            is_link = any(x in text for x in ["http", "https", "t.me/", "@"])
            is_bad = any(word in text for word in BAD_WORDS)

            if is_media or is_link or is_bad:
                try:
                    member = bot.get_chat_member(chat_id, msg.from_user.id)
                    if member.status not in ['creator', 'administrator']:
                        bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                except TelegramError as e:
                    print(f"TelegramError: {e}")
                except Exception as e:
                    print(f"Delete error: {e}")

            return "OK", 200

        except Exception as e:
            print(f"Webhook error: {e}")
            return "Error", 500

    return "Method Not Allowed", 405

@app.route('/')
def index():
    return "Vaxorum Bot is Online! 🚀"
