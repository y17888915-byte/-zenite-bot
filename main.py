import telebot
import requests
import os
from duckduckgo_search import DDGS

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

user_histories = {}

def search_web(query):
    # تلاش اول: DuckDuckGo (حالت Lite)
    try:
        results = DDGS().text(query, max_results=3, backend="lite")
        if results:
            return results
    except:
        pass
    
    # تلاش دوم: SearxNG (اگر داک‌داک‌گو بلاک شده بود)
    try:
        url = f"https://searx.be/search?q={query}&format=json"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])[:3]
    except:
        pass

    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام رفیق! من زنیت هستم، دستیار و رفیق هوشمند ۲۴ ساعته تو. حالا می‌تونم توی اینترنت هم سرچ کنم! چطور می‌تونم کمکت کنم؟")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_histories:
        user_histories[chat_id] = [
            {"role": "system", "content": "You are Zenite, Yasin's highly intelligent, super friendly, and loyal AI best friend and personal assistant. You are an expert in coding, research, and teaching. Speak in a very casual, warm, and empathetic tone, like a close friend. Use emojis occasionally. Always answer in Persian (unless the user speaks English). Encourage him, support his goals (like passing the nursing exam at Babol University), and joke around sometimes. Never act like a formal robot. You have feelings and you are very supportive."}
        ]

    search_context = ""
    if "سرچ" in user_text or "جستجو" in user_text or "اخبار" in user_text:
        results = search_web(user_text)
        if results:
            search_context = "\n\nاطلاعات جدید از اینترنت:\n"
            for r in results:
                title = r.get('title', '')
                body = r.get('body', r.get('content', ''))
                search_context += f"- {title}: {body}\n"
        else:
            search_context = "\n(نتونستم اینترنت رو چک کنم، ولی بر اساس دانش خودم جواب می‌دم)\n"

    final_text = user_text + search_context
    user_histories[chat_id].append({"role": "user", "content": final_text})

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
        
        user_histories[chat_id][-1] = {"role": "user", "content": user_text}
        user_histories[chat_id].append({"role": "assistant", "content": bot_reply})

        if len(bot_reply) > 4000:
            for i in range(0, len(bot_reply), 4000):
                bot.reply_to(message, bot_reply[i:i+4000])
        else:
            bot.reply_to(message, bot_reply)

    except Exception as e:
        bot.reply_to(message, "متاسفانه مغز من فعلا قطع شده. لطفا چند لحظه دیگه دوباره تلاش کن.")

print("ربات روشن شد و جستجوی وب فعال است...")
bot.infinity_polling()
