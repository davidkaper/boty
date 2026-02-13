import os
from flask import Flask, request
from telegram import Update, Bot

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables!")

bot = Bot(token=TOKEN)

BAD_WORDS = [
    "کص", "جقی", "کیر", "کون", "کونی", "جنده", "جق", "گاییدمت", "گوه", "گوه خوردن",
    "مادرجنده", "کس ننت", "خواهرجنده", "خار مادر", "کص ننه", "کیرم تو", "کیر خر",
    "کون گشاد", "کون نشور", "دیوث", "خواهرت", "دخترجنده", "پفیوز", "هرزه", "فاحشه",
    "کیرم تو کون", "کصکش", "کیرکش", "کونکش", "گوه خور", "کیرم دهنت", "کیر تو کون",
    "ننه جنده", "آب کیر", "آب کص", "کیرم تو دهن", "کون لیس", "جنده مادر", "کص لیس",
    "گاییدم", "گاییدنت", "گاییده", "کیرم", "کصم", "کونم", "مادرتو", "خواهرتو",
    "خارتو", "کیرتو", "کصتو", "کونتو", "کص ننت", "فاحشه‌تون", "کسکش",
    "حشری", "پورن", "سوپر", "گوساله", "گاو", "حرومزاده", "لاشی", "بی‌شعور", "فیلم سوپر"
]
@app.route('/', methods=['POST'])
def webhook():
    try:
        update_dict = request.get_json(force=True)
        if not update_dict:
            return "No data", 400

        update = Update.de_json(update_dict, bot)
        if not update or not update.message:
            return "OK", 200

        msg = update.message
        text = (msg.text or msg.caption or "").lower()
        chat_id = msg.chat_id

        # خوش آمدگویی
        if msg.new_chat_members:
            for member in msg.new_chat_members:
                welcome_text = (
    f"سلام {member.full_name} جان! 😊\n"
    f"به گروه وکسوروم خیلی خوش اومدی 🌟\n"
    f"اینجا جای خودته، راحت باش و لذت ببر ~\n"
    f"🌐 vaxorum.xyz"
)
                bot.send_message(chat_id=chat_id, text=welcome_text)
            return "OK", 200

        # فیلتر
        is_media = bool(msg.photo or msg.video or msg.document or msg.animation or msg.voice or msg.video_note)
        is_link = any(sub in text for sub in ["http", "https", "t.me/", "@"])
        is_bad_word = any(
        re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE)
        for word in BAD_WORDS
          )

        if is_media or is_link or is_bad_word:
            try:
                member = bot.get_chat_member(chat_id, msg.from_user.id)
                if member.status not in ['creator', 'administrator']:
                    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            except Exception as e:
                print(f"Error deleting/checking: {e}")

        return "OK", 200

    except Exception as e:
        print(f"Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return "Error", 500

@app.route('/')
def index():
    return "Vaxorum Bot is Online! 🚀"
