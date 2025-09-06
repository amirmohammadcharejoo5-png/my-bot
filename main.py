import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# تنظیمات لاگ‌گیری برای دیباگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن ربات خود را اینجا قرار دهید
# این توکن را از BotFather در تلگرام دریافت کنید
TELEGRAM_TOKEN = "8360202192:AAGK3SqheE4wYqKx1-eeggvdyhf580jv6WQ"

# تابع خوش‌آمدگویی برای دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"سلام {user.mention_html()}! 👋\n\n"
        "نام آهنگ یا لینک یوتیوب مورد نظرت رو برام بفرست تا دانلودش کنم.",
    )

# تابع اصلی برای پردازش پیام‌ها و دانلود آهنگ
async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """جستجو، دانلود و ارسال آهنگ."""
    message = await update.message.reply_text("در حال پردازش درخواست شما... لطفاً صبر کنید. ⏳")
    query = update.message.text

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s', # نام فایل خروجی
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # اگر ورودی یک لینک است مستقیم دانلود می‌کند، در غیر این صورت جستجو می‌کند
            if "http" in query:
                info = ydl.extract_info(query, download=True)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        await message.edit_text("در حال ارسال آهنگ... 📤")
        
        # ارسال فایل صوتی به کاربر
        await context.bot.send_audio(
            chat_id=update.effective_chat.id,
            audio=open(filename, 'rb'),
            title=info.get('title', 'Unknown Title'),
            duration=info.get('duration', 0)
        )

        # حذف فایل از سرور پس از ارسال
        os.remove(filename)
        await message.delete() # حذف پیام "در حال ارسال"

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.edit_text("متاسفانه مشکلی در پردازش درخواست شما پیش آمد. لطفاً دوباره تلاش کنید. 😔")


def main() -> None:
    """اجرای ربات."""
    # ساخت اپلیکیشن ربات
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # تعریف دستورات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_music))

    # اجرای ربات
    print("Bot is running...")
    application.run_polling()

if name == 'main':
    main()