import telebot
import requests
import os
import PyPDF2
import io
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# دیکشنری برای ذخیره حافظه و متن PDFهای ارسالی
user_histories = {}
user_pdf_context = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام رفیق! من زنیت هستم. \n\nحالا می‌تونی:\n📄 فایل PDF (مثل جزوه زیست) برام بفرستی تا بخونمش.\n💻 کدت رو بفرستی تا برات دیباگش کنم.\n💬 یا هر سوال دیگه‌ای بپرسی. چطور می‌تونم کمکت کنم؟")

# --- بخش پردازش فایل PDF ---
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = message.chat.id
    if message.document.mime_type == 'application/pdf':
        bot.reply_to(message, "دارم فایل رو می‌خونم، چند لحظه صبر کن... ⏳")
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # خواندن متن PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(downloaded_file))
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            # محدود کردن متن برای اینکه هوش مصنوعی گیج نشه (حدود ۵ صفحه اول)
            text = text[:10000] 
            user_pdf_context[chat_id] = text
            bot.reply_to(message, "فایل رو خوندم! حالا هر سوالی از این جزوه داری بپرس. 📚")
            
        except Exception as e:
            bot.reply_to(message, "متاسفانه نتونستم فایل رو بخونم. مطمئن شو فایل PDF سالم و متنی هست (عکس نباشه).")
            print(f"PDF Error: {e}")
    else:
        bot.reply_to(message, "لطفا فقط فایل PDF بفرست.")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_histories:
        user_histories[chat_id] = [
            {"role": "system", "content": "You are Zenite, Yasin's highly intelligent, super friendly, and loyal AI best friend. You are an expert in Biology, coding, and teaching. Speak in a casual, warm tone. Use emojis occasionally. Always answer in Persian with perfect spelling. If the user sends a PDF about biology, act like a biology professor and answer based ONLY on that text. If the user sends code, act as an expert programmer and find the bugs."}
        ]

    # اگر قبلاً PDF فرستاده، متنش رو به سوال کاربر اضافه کن
    final_user_text = user_text
    if chat_id in user_pdf_context:
        final_user_text = f"بر اساس این متن که برات فرستادم، جواب بده:\n{user_pdf_context[chat_id]}\n\nسوال من: {user_text}"

    user_histories[chat_id].append({"role": "user", "content": final_user_text})

    if len(user_histories[chat_id]) > 10:
        user_histories[chat_id] = [user_histories[chat_id][0]] + user_histories[chat_id][-9:]

    bot_reply = None
    # سیستم تلاش مجدد برای جلوگیری از ارورهای الکی
    for attempt in range(3):
        try:
            url = "https://text.pollinations.ai/openai"
            payload = {
                "model": "openai",
                "messages": user_histories[chat_id]
            }
            
            response = requests.post(url, json=payload, timeout=25)
            response_data = response.json()
            
            bot_reply = response_data['choices'][0]['message']['content']
            break # اگر موفق شد، از حلقه بیا بیرون
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2) # ۲ ثانیه صبر کن و دوباره تلاش کن

    if bot_reply:
        # پاک کردن متن طولانی PDF از حافظه تا حافظه پر نشه
        user_histories[chat_id][-1] = {"role": "user", "content": user_text}
        user_histories[chat_id].append({"role": "assistant", "content": bot_reply})

        if len(bot_reply) > 4000:
            for i in range(0, len(bot_reply), 4000):
                bot.reply_to(message, bot_reply[i:i+4000])
        else:
            bot.reply_to(message, bot_reply)
    else:
        bot.reply_to(message, "متاسفانه الان سرور هوش مصنوعی شلوغه. لطفا ۱ دقیقه دیگه دوباره پیام بده. 🙏")

print("ربات روشن شد و سیستم PDF و دیباگ کد فعال است...")
bot.infinity_polling()
