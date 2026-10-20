import telebot
import requests
BOT_TOKEN = "8941757748:AAFFKCFnq9nkpJevtfsBcLVXV525Vz5htV04"
bot = telebot.TeleBot(BOT_TOKEN)

user_histories = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! من زنیت هستم، دستیار هوشمند ۲۴ ساعته تو. چطور می‌تونم کمکت کنم؟")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_histories:
        user_histories[chat_id] = [
            {"role": "system", "content": "You are Zenite, a highly intelligent AI personal assistant. You are an expert in coding, research, and teaching. You must answer in Persian if the user speaks Persian, but you are also fluent in English. Be helpful, friendly, and professional."}
        ]

    user_histories[chat_id].append({"role": "user", "content": user_text})

    if len(user_histories[chat_id]) > 10:
        user_histories[chat_id] = [user_histories[chat_id][0]] + user_histories[chat_id][-9:]

    try:
        url = "https://text.pollinations.ai/openai"
        payload = {
            "model": "openai",
            "messages": user_histories[chat_id]
        }
        
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        bot_reply = response_data['choices'][0]['message']['content']
        
        user_histories[chat_id].append({"role": "assistant", "content": bot_reply})

        if len(bot_reply) > 4000:
            for i in range(0, len(bot_reply), 4000):
                bot.reply_to(message, bot_reply[i:i+4000])
        else:
            bot.reply_to(message, bot_reply)

    except Exception as e:
        bot.reply_to(message, "متاسفانه مغز من فعلا قطع شده. لطفا چند لحظه دیگه دوباره تلاش کن.")

print("ربات روشن شد و در حال کار است...")
bot.infinity_polling()
