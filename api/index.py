import os
import json
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application

app = Flask(name)

# دریافت توکن از Environment Variables ورسل
TOKEN = os.getenv("BOT_TOKEN")

# تابع اصلی پردازش پیام‌ها
async def process_update(update_dict):
    application = Application.builder().token(TOKEN).build()
    
    # تعریف منطق فیلتر و خوش‌آمدگویی در اینجا
    bot = application.bot
    update = Update.de_json(update_dict, bot)
    
    if update.message:
        msg = update.message
        text = (msg.text or msg.caption or "").lower()
        
        # ۱. خوش‌آمدگویی
        if msg.new_chat_members:
            for member in msg.new_chat_members:
                await msg.reply_text(f"سلام {member.full_name} عزیز! به وکسوروم خوش آمدی.\nvaxorum.xyz")
        
        # ۲. فیلتر کردن لینک، عکس، فیلم و کلمات (برای غیر ادمین‌ها)
        bad_words = ["کلمه۱", "کلمه۲"] # لیست خود را اینجا کامل کنید
        
        is_media = msg.photo or msg.video or msg.document
        is_link = "http" in text or "t.me" in text or "@" in text
        is_bad_word = any(word in text for word in bad_words)

        if is_media or is_link or is_bad_word:
            try:
                # بررسی اینکه فرستنده ادمین نباشد (اختیاری)
                member = await bot.get_chat_member(msg.chat_id, msg.from_user.id)
                if member.status not in ['creator', 'administrator']:
                    await msg.delete()
            except Exception as e:
                print(f"Error: {e}")

@app.route('/', methods=['POST'])
def webhook():
    if request.method == "POST":
        update_dict = request.get_json(force=True)
        # اجرای ناهمگام برای جلوگیری از Timeout در ورسل
        asyncio.run(process_update(update_dict))
        return "ok", 200
    return "Method Not Allowed", 405

@app.route('/')
def index():
    return "Vaxorum Bot is Active!"
