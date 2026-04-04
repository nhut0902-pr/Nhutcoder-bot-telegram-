import feedparser
import requests
import time
import schedule
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

RSS_URL = "https://news.google.com/rss/search?q=artificial+intelligence"

# 🧠 Gemini AI
def ask_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    res = requests.post(url, json=data)
    result = res.json()

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Lỗi AI rồi bro 😅"

# 📰 lấy tin
def get_news():
    feed = feedparser.parse(RSS_URL)
    return feed.entries[:3]

# 📤 format tin
def format_news():
    articles = get_news()
    message = "🔥 Tin AI mới nhất:\n\n"

    for i, article in enumerate(articles, 1):
        summary = ask_gemini(f"Tóm tắt tin sau bằng tiếng Việt:\n{article.title} {article.summary}")
        message += f"{i}. {article.title}\n"
        message += f"🧠 {summary}\n"
        message += f"🔗 {article.link}\n\n"

    return message

# 📌 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot AI News\n\n"
        "/news - Xem tin AI mới nhất\n"
        "/chat <câu hỏi> - Chat với AI\n"
    )

# 📰 /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Đang lấy tin...")
    msg = format_news()
    await update.message.reply_text(msg)

# 🤖 /chat
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)

    if not user_text:
        await update.message.reply_text("❗ Dùng: /chat câu hỏi")
        return

    reply = ask_gemini(user_text)
    await update.message.reply_text(reply)

# ⏰ auto gửi 7h
def auto_send():
    message = format_news()
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message}
    )

# setup bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))
app.add_handler(CommandHandler("chat", chat))

# schedule 7h VN (00h UTC)
schedule.every().day.at("00:00").do(auto_send)

print("Bot đang chạy...")

while True:
    schedule.run_pending()
    app.run_polling()
