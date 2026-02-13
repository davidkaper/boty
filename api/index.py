import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(name)

# تنظیمات اصلی
TOKEN = os.getenv("BOT_TOKEN")
WEBSITE_URL = "vaxorum.xyz"
BAD_WORDS = ["کلمه۱", "کلمه۲", "کلمه۳"] # لیست کلمات نامناسب را اینجا کامل کنید

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"خوش آمدید به وکسوروم!\nمرجع بازارهای جهانی و سهام آمریکا\n{WEBSITE_URL}")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"سلام {member.full_name} عزیز به گروه وکسوروم خوش آمدی!\n"
            f"برای تحلیل‌های روزانه سهام و بیت‌کوین همراه ما باش.\n{WEBSITE_URL}"
        )

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = msg.text or msg.caption or ""
    
    # بررسی کلمات نامناسب
    if any(word in text for word in BAD_WORDS):
        await msg.delete()
        return

    # حذف پیام‌های حاوی لینک، عکس یا فیلم
    # این بخش طبق خواسته شما تمام رسانه‌ها را پاک می‌کند
    if msg.photo or msg.video or msg.document or "http" in text or "@" in text:
        try:
            await msg.delete()
        except Exception as e:
            print(f"Error deleting: {e}")

# تنظیمات Flask برای Webhook
@app.route('/', methods=['POST'])
async def webhook():
    if request.method == "POST":
        application = Application.builder().token(TOKEN).build()
        
        # ثبت هندلرها
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, filter_messages))
        
        async with application:
            update = Update.de_json(request.get_json(force=True), application.bot)
            await application.process_update(update)
            
        return "ok", 200

@app.route('/')
def index():
    return "Bot is running!"
