import telebot
import requests
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

user_histories = {}

def search_web(query):
    try:
        url = f"https://www.bing.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for li in soup.select("li.b_algo"):
            title = li.find("h2").text if li.find("h2") else ""
            snippet = li.find("p").text if li.find("p") else ""
            if title and snippet:
                results.append({"title": title, "body": snippet})
        return results[:3]
    except Exception as e:
        print(f"Search error: {e}")
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
                search_context += f"- {r['title']}: {r['body']}\n"
        else:
            search_context = "\n(متاسفانه نتونستم سرچ کنم، بر اساس دانش خودم جواب می‌دم)\n"

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
