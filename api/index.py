import os
import re
from flask import Flask, request
from telegram import Update, Bot
from telegram.error import BadRequest, Unauthorized, TimedOut

app = Flask(__name__)

# تنظیمات ثابت
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables!")

MAX_MESSAGE_LENGTH = 600
ADMIN_STATUSES = {'creator', 'administrator'}

BAD_WORDS = {
    "لاشی", "کص", "کیر", "کون", "جنده", "کصکش", "کونی", "مادرجنده", "خواهرجنده",
    "گوه", "جق", "کیرم", "کص ننه", "کون مادرت", "کسکش", "جاکش", "حرومزاده",
    "پورن", "گاییدمت", "فیلم سوپر", "کسشر", "مادر قبحه", "کص ننت", "زن جنده",
    "گاییدم", "دیوس", "بی ناموس", "ننت", "ننه‌ت", "حشری", "جقی", "شهوتی",
    "کصک", "کیرتو", "جق زدن", "جق بزن", "کونم", "کیرش", "کسشعر", "کون گشاد",
    # اگر کلمات بیشتری می‌خواهید اینجا اضافه کنید
}

# الگوهای لینک / تبلیغ / یوزرنیم مشکوک
LINK_PATTERNS = [
    r'https?://',
    r't\.me/',
    r'telegram\.me/',
    r'bit\.ly',
    r'goo\.gl',
    r'discord\.gg',
    r'youtu\.be',
]

LINK_REGEX = re.compile('|'.join(LINK_PATTERNS), re.IGNORECASE)

# برای تشخیص دقیق‌تر کلمات (با مرز کلمه)
WORD_BOUNDARY = re.compile(r'(?<!\w)%s(?!\w)', re.IGNORECASE)

bot = Bot(token=TOKEN)


def contains_bad_word(text: str) -> bool:
    """تشخیص دقیق‌تر کلمات ممنوعه با توجه به مرز کلمه"""
    text_with_space = f" {text} "
    for word in BAD_WORDS:
        if WORD_BOUNDARY.sub(word, text_with_space):
            return True
    return False


@app.route('/', methods=['POST'])
def webhook():
    try:
        update_dict = request.get_json(force=True)
        if not update_dict:
            return "No JSON data", 400

        update = Update.de_json(update_dict, bot)
        if not update or not update.message:
            return "OK", 200

        msg = update.message
        if not msg:
            return "OK", 200

        # ---------------- خوش‌آمدگویی ----------------
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
                    "هر پیش‌بینی، تحلیل و نظری داری بگو.\n"
                    "لطفاً قوانین گروه رو رعایت کن و از بحث‌های سازنده لذت ببر!\n\n"
                    "🌐 وب‌سایت: vaxorum.xyz"
                )
                try:
                    bot.send_message(chat_id=msg.chat_id, text=welcome_text)
                except Exception:
                    pass  # اگر ارسال نشد مهم نیست
            return "OK", 200

        # ---------------- فیلتر محتوا ----------------
        text = (msg.text or msg.caption or "").lower().strip()
        chat_id = msg.chat_id
        user_id = msg.from_user.id if msg.from_user else None

        if not user_id:
            return "OK", 200

        # چک‌های سریع (بدون درخواست API)
        is_media = bool(
            msg.photo or msg.video or msg.document or msg.animation or
            msg.voice or msg.video_note or msg.sticker or msg.poll
        )
        is_suspicious_link = bool(LINK_REGEX.search(text)) or any(
            s in text for s in ("@admin", "@everyone", "t.me/joinchat", "t.me/+")
        )
        is_too_long = len(text) > MAX_MESSAGE_LENGTH
        is_bad_word = contains_bad_word(text)

        # اگر هیچ کدام از موارد ممنوعه نبود → ادامه
        if not (is_media or is_suspicious_link or is_too_long or is_bad_word):
            return "OK", 200

        # فقط در صورتی که نیاز به حذف باشد → چک ادمین بودن
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status in ADMIN_STATUSES:
                return "OK", 200  # ادمین → آزاد

            # حذف پیام
            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)

            # پیام توضیحی (اختیاری اما توصیه می‌شود)
            reasons = []
            if is_too_long:        reasons.append(f"بیش از {MAX_MESSAGE_LENGTH} کاراکتر")
            if is_bad_word:        reasons.append("کلمه غیرمجاز")
            if is_media:           reasons.append("رسانه (عکس/فیلم/گیف/صدا)")
            if is_suspicious_link: reasons.append("لینک / دعوت")

            if reasons:
                reason_text = "، ".join(reasons)
                bot.send_message(
                    chat_id=chat_id,
                    text=f"پیام حذف شد.\nدلیل: {reason_text}\n\nلطفاً قوانین را رعایت کنید.",
                    disable_notification=True
                )

        except BadRequest as e:
            if "message can't be deleted" in str(e) or "Message to delete not found" in str(e):
                pass  # پیام قبلاً حذف شده یا مشکلی ندارد
            else:
                print(f"BadRequest در حذف پیام: {e}")

        except (Unauthorized, TimedOut):
            print("مشکل دسترسی یا تایم‌اوت تلگرام")

        except Exception as e:
            print(f"خطای غیرمنتظره در فیلتر: {type(e).__name__} → {e}")

        return "OK", 200

    except Exception as e:
        print(f"خطای کلی در webhook: {type(e).__name__} → {e}")
        import traceback
        traceback.print_exc()
        return "Server error", 500


@app.route('/')
def index():
    return "Vaxorum Anti-Spam Bot is Online! 🚀"


if __name__ == "__main__":
    app.run()
