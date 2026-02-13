import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot

app = Flask(name)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

# لیست کلمات نامناسب (می‌توانید کلمات بیشتری اضافه کنید)
BAD_WORDS = ["کلمه۱", "کلمه۲", "تست"]

async def handle_logic(update_dict):
    update = Update.de_json(update_dict, bot)
    if not update.message:
        return

    msg = update.message
    text = (msg.text or msg.caption or "").lower()
    chat_id = msg.chat_id

    # ۱. خوش‌آمدگویی به اعضای جدید
    if msg.new_chat_members:
        for member in msg.new_chat_members:
            welcome_text = f"سلام {member.full_name} عزیز به گروه وکسوروم خوش آمدی!\n🌐 vaxorum.xyz"
            await bot.send_message(chat_id=chat_id, text=welcome_text)

    # ۲. فیلتر محتوا (فقط برای غیر ادمین‌ها)
    is_media = bool(msg.photo or msg.video or msg.document)
    is_link = "http" in text or "t.me/" in text or "@" in text
    is_bad_word = any(word in text for word in BAD_WORDS)

    if is_media or is_link or is_bad_word:
        try:
            # بررسی ادمین بودن فرستنده
            member = await bot.get_chat_member(chat_id, msg.from_user.id)
            if member.status not in ['creator', 'administrator']:
                await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        except Exception as e:
            print(f"Delete Error: {e}")

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
    return "Vaxorum Bot is Online!"
