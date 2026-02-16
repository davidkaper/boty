import os
from flask import Flask, request
from telegram import Update, Bot

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables!")

bot = Bot(token=TOKEN)

BAD_WORDS = [
    "لاشی", "کص", "کیر", "کون", "جنده",
    "کصکش", "کونی", "مادرجنده", "خواهرجنده",
    "گوه", "جق", "کیرم", "کص ننه", "کون مادرت",
    "کسکش", "جاکش", "حرومزاده", "پورن", "گاییدمت", "فیلم سوپر", "کسشر", "مادر قبحه", "کص ننت", "زن جنده", "گاییدم", "دیوس", "بی ناموس" , "ننت", "حشری", "جقی", "شهوتی"
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
    f"سلام {member.full_name} عزیز 👋\n"
    "به گروه **وکسوروم** خوش آمدی!\n\n"
    "اینجا جمع تحلیلگران و علاقه‌مندان به:\n"
    "• قیمت دلار و ارزهای جهانی\n"
    "• بیت‌کوین، آلت‌کوین‌ها و بازار کریپتو\n"
    "• سهام آمریکا (نزدک، S&P500، داوجونز)\n"
    "• کالاهای جهانی (طلا، نفت، نقره و ...)\n\n"
    "هرپیش بینی و تحلیل و نظری داری بگو.\n"
    "لطفاً قوانین گروه رو رعایت کن و از بحث‌های سازنده لذت ببر!\n\n"
    "🌐 وب‌سایت: vaxorum.xyz"
)
                bot.send_message(chat_id=chat_id, text=welcome_text)
            return "OK", 200

        # فیلتر
        is_media = bool(msg.photo or msg.video or msg.document or msg.animation or msg.voice or msg.video_note)
        is_link = any(sub in text for sub in ["http", "https", "t.me/", "@"])
        words = text.split()  # تقسیم بر اساس فاصله‌ها
        is_bad_word = any(bad_word in words for bad_word in BAD_WORDS)

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
