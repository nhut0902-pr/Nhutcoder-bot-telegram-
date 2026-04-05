from flask import Flask, render_template, request
import os, json, threading, time, requests, feedparser, schedule, asyncio

# Telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

CONFIG_FILE = "config.json"
bot_started = False

# ================= CONFIG =================
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE) as f:
        return json.load(f)

# ================= AI =================
def ask_gemini(api_key, text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.0-flash:generateContent?key={api_key}"
    data = {"contents": [{"parts": [{"text": text}]}]}

    try:
        res = requests.post(url, json=data)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "❌ Lỗi AI"

# ================= NEWS =================
def get_news():
    feed = feedparser.parse("https://news.google.com/rss/search?q=ai")
    return feed.entries[:3]

def send_news(chat_id=None):
    config = load_config()
    if not config:
        return

    TOKEN = config["TOKEN"]
    CHAT_ID = chat_id if chat_id else config["CHAT_ID"]
    GEMINI = config["GEMINI_API_KEY"]

    msg = "🔥 Tin AI mới:\n\n"

    for a in get_news():
        summary = ask_gemini(GEMINI, a.title)
        msg += f"{a.title}\n🧠 {summary}\n🔗 {a.link}\n\n"

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

# ================= SCHEDULE =================
def run_scheduler():
    schedule.every().day.at("00:00").do(send_news)

    while True:
        schedule.run_pending()
        time.sleep(60)

# ================= TELEGRAM BOT =================
async def bot_main():
    config = load_config()
    if not config:
        print("❌ Chưa có config")
        return

    TOKEN = config["TOKEN"]
    GEMINI = config["GEMINI_API_KEY"]

    app_bot = ApplicationBuilder().token(TOKEN).build()

    # /start
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 Bot AI\n\n/news - Tin AI\n/chat <câu hỏi>"
        )

    # /news
    async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⏳ Đang lấy tin...")
        send_news(update.message.chat_id)
        await update.message.reply_text("✅ Xong!")

    # /chat
    async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = " ".join(context.args)
        if not text:
            await update.message.reply_text("❗ /chat câu hỏi")
            return

        reply = ask_gemini(GEMINI, text)
        await update.message.reply_text(reply)

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("news", news))
    app_bot.add_handler(CommandHandler("chat", chat))

    print("🤖 Bot đang chạy...")
    await app_bot.run_polling()

# chạy bot trong thread riêng (fix event loop)
def start_bot():
    asyncio.run(bot_main())

# ================= WEB =================
@app.route("/", methods=["GET", "POST"])
def index():
    global bot_started

    if request.method == "POST":
        data = {
            "TOKEN": request.form["token"],
            "CHAT_ID": request.form["chat_id"],
            "GEMINI_API_KEY": request.form["gemini"]
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

        if not bot_started:
            threading.Thread(target=start_bot).start()
            threading.Thread(target=run_scheduler).start()
            bot_started = True

        return "✅ Bot đang chạy!"

    return render_template("index.html")

# ================= START =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
