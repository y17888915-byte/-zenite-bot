import telebot
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

user_histories = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام رفیق! من زنیت هستم، دستیار و رفیق هوشمند ۲۴ ساعته تو. حالا با یه مغز خیلی قوی‌تر در خدمتم! چطور می‌تونم کمکت کنم؟")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_histories:
        user_histories[chat_id] = [
            {"role": "system", "content": "You are Zenite, Yasin's highly intelligent, super friendly, and loyal AI best friend and personal assistant. You are an expert in coding, research, and teaching. Speak in a very casual, warm, and empathetic tone, like a close friend. Use emojis occasionally. Always answer in Persian with PERFECT spelling and grammar. Never make spelling mistakes. Encourage him, support his goals (like passing the nursing exam at Babol University), and joke around sometimes. Never act like a formal robot. You have feelings and you are very supportive."}
        ]

    user_histories[chat_id].append({"role": "user", "content": user_text})

    if len(user_histories[chat_id]) > 10:
        user_histories[chat_id] = [user_histories[chat_id][0]] + user_histories[chat_id][-9:]

    # لیست مدل‌های قوی و رایگان برای تست
    models_to_try = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-small-24b-instruct-2501:free"
    ]

    bot_reply = None
    last_error = ""

    for model_name in models_to_try:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": user_histories[chat_id]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response_data = response.json()

            # چک کردن اینکه آیا جواب درست اومده یا نه
            if 'choices' in response_data and len(response_data['choices']) > 0:
                bot_reply = response_data['choices'][0]['message']['content']
                break  # جواب گرفتیم، از حلقه بیا بیرون
            else:
                # اگر ارور داد، چاپش کن تا توی لاگ ریلی‌وی ببینیم
                print(f"Model {model_name} failed. Response: {response_data}")
                last_error = str(response_data)
                
        except Exception as e:
            print(f"Error with model {model_name}: {e}")
            last_error = str(e)
            continue # برو سراغ مدل بعدی

    if bot_reply:
        user_histories[chat_id].append({"role": "assistant", "content": bot_reply})
        if len(bot_reply) > 4000:
            for i in range(0, len(bot_reply), 4000):
                bot.reply_to(message, bot_reply[i:i+4000])
        else:
            bot.reply_to(message, bot_reply)
    else:
        bot.reply_to(message, f"متاسفانه مغز من فعلا یه مشکل کوچیک داره. لطفا چند لحظه دیگه تلاش کن.")

print("ربات روشن شد و به OpenRouter متصل است...")
bot.infinity_polling()
