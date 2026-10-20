import telebot
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

user_histories = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام رفیق! من زنیت هستم، دستیار و رفیق هوشمند ۲۴ ساعته تو. چطور می‌تونم کمکت کنم؟")

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

    bot_reply = None

    # تلاش اول: استفاده از مدل‌های رایگان پایدارتر در OpenRouter
    models_to_try = [
        "meta-llama/llama-3-8b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "qwen/qwen-2-7b-instruct:free"
    ]

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
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response_data = response.json()

            if 'choices' in response_data and len(response_data['choices']) > 0:
                bot_reply = response_data['choices'][0]['message']['content']
                break 
        except Exception as e:
            print(f"Error with model {model_name}: {e}")
            continue

    # تلاش دوم: اگر OpenRouter جواب نداد، برو سراغ Pollinations (مغز پشتیبان)
    if not bot_reply:
        try:
            url = "https://text.pollinations.ai/openai"
            payload = {
                "model": "openai",
                "messages": user_histories[chat_id]
            }
            response = requests.post(url, json=payload, timeout=20)
            response_data = response.json()
            bot_reply = response_data['choices'][0]['message']['content']
        except Exception as e:
            print(f"Pollinations Error: {e}")

    # اگر هر دو خراب بودن
    if not bot_reply:
        bot_reply = "متاسفانه الان همه مغزهام درگیرن! 😅 چند لحظه دیگه دوباره پیام بده."

    user_histories[chat_id].append({"role": "assistant", "content": bot_reply})

    if len(bot_reply) > 4000:
        for i in range(0, len(bot_reply), 4000):
            bot.reply_to(message, bot_reply[i:i+4000])
    else:
        bot.reply_to(message, bot_reply)

print("ربات روشن شد...")
bot.infinity_polling()
