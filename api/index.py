# api/index.py
import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot

app = Flask(__name__)           # ← اینجا حتماً __name__ باشه

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables!")

bot = Bot(token=TOKEN)

# لیست کلمات نامناسب
BAD_WORDS = ["کلمه۱", "کلمه۲", "تست", "کص", "کون"]  # مثال – خودت کامل کن

async def handle_logic(update_dict):
    try:
        update = Update.de_json(update_dict, bot)
        if not update or not update.message:
            return

        msg = update.message
        text = (msg.text or msg.caption or "").lower()
        chat_id = msg.chat_id

        # ۱. خوش‌آمدگویی
        if msg.new_chat_members:
            for member in msg.new_chat_members:
                welcome_text = f"سلام {member.full_name} عزیز به گروه وکسوروم خوش آمدی!\n🌐 vaxorum.xyz"
                await bot.send_message(chat_id=chat_id, text=welcome_text)
            return

        # ۲. فیلتر
        is_media = bool(msg.photo or msg.video or msg.animation or msg.document or msg.voice or msg.video_note)
        is_link = any(x in text for x in ["http", "https", "t.me/", "@", "telegram.me"])
        is_bad_word = any(word in text for word in BAD_WORDS)

        if is_media or is_link or is_bad_word:
            try:
                member = await bot.get_chat_member(chat_id, msg.from_user.id)
                if member.status not in ['creator', 'administrator']:
                    await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                    # اختیاری: اخطار هم بده
                    # await bot.send_message(chat_id, "محتوای غیرمجاز ارسال کردی!")
            except Exception as e:
                print(f"حذف پیام ناموفق: {e}")

    except Exception as e:
        print(f"خطا در پردازش آپدیت: {e}")

@app.route('/', methods=['POST'])
def webhook():
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            asyncio.run(handle_logic(data))
            return "OK", 200
        except Exception as e:
            print(f"Webhook Error: {e}")
            return "Error", 500
    return "Method Not Allowed", 405

@app.route('/')
def index():
    return "Vaxorum Bot is Online! 🚀"
