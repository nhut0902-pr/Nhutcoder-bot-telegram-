from flask import Flask, render_template, request
import os
import json
import threading
import time
import requests
import feedparser
import schedule

app = Flask(__name__)

CONFIG_FILE = "config.json"

# ================= CONFIG =================
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE) as f:
        return json.load(f)

# ================= AI =================
def ask_gemini(api_key, text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.0-flash:generateContent?key={api_key}"
    
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }

    try:
        res = requests.post(url, json=data)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "❌ Lỗi AI"

# ================= BOT =================
def send_news():
    config = load_config()
    if not config:
        return

    TOKEN = config["TOKEN"]
    CHAT_ID = config["CHAT_ID"]
    GEMINI = config["GEMINI_API_KEY"]

    feed = feedparser.parse("https://news.google.com/rss/search?q=ai")
    articles = feed.entries[:3]

    msg = "🔥 Tin AI hôm nay:\n\n"

    for a in articles:
        summary = ask_gemini(GEMINI, a.title)
        msg += f"{a.title}\n🧠 {summary}\n🔗 {a.link}\n\n"

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def run_bot():
    schedule.every().day.at("00:00").do(send_news)  # 7h VN

    while True:
        schedule.run_pending()
        time.sleep(60)

# ================= WEB =================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = {
            "TOKEN": request.form["token"],
            "CHAT_ID": request.form["chat_id"],
            "GEMINI_API_KEY": request.form["gemini"]
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

        threading.Thread(target=run_bot).start()

        return "✅ Đã lưu & bot đang chạy!"

    return render_template("index.html")

# ================= START =================
if __name__ == "__main__":
    # chạy bot nền
    threading.Thread(target=run_bot).start()

    # 🔥 FIX PORT RENDER
    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
