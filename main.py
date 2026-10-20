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

    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": user_histories[chat_id]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        bot_reply = response_data['choices'][0]['message']['content']
        
        user_histories[chat_id].append({"role": "assistant", "content": bot_reply})

        if len(bot_reply) > 4000:
            for i in range(0, len(bot_reply), 4000):
                bot.reply_to(message, bot_reply[i:i+4000])
        else:
            bot.reply_to(message, bot_reply)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "متاسفانه مغز من فعلا یه مشکل کوچیک داره. لطفا چند لحظه دیگه دوباره تلاش کن.")

print("ربات روشن شد و به مدل Gemini متصل است...")
bot.infinity_polling()
