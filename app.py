from flask import Flask, request, render_template_string
import requests
import os
import feedparser

app = Flask(__name__)

TOKEN = ""
HTML = """
<h2>🤖 Setup Bot</h2>
<form method="post">
Token:<br><input name="token"><br><br>
<button type="submit">Save</button>
</form>
"""

# ====== GEMINI CONFIG ======
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.0-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    res = requests.post(url, headers=headers, json=data)
    try:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "❌ AI lỗi rồi bro!"

# ====== SETUP WEB ======
@app.route("/", methods=["GET", "POST"])
def setup():
    global TOKEN

    if request.method == "POST":
        TOKEN = request.form["token"]
        set_webhook()
        return "✅ Bot ready!"

    return render_template_string(HTML)

# ====== WEBHOOK ======
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # ===== START =====
        if text == "/start":
            send(chat_id, "🤖 Bot AI PRO ready!\n\nCommands:\n/news ai\n/news crypto\n/news tech\n/trend\n/ai hỏi")

        # ===== AI =====
        elif text.startswith("/ai"):
            question = text.replace("/ai", "").strip()
            reply = ask_ai(question)
            send(chat_id, reply)

        # ===== NEWS =====
        elif text.startswith("/news"):
            parts = text.split()
            if len(parts) < 2:
                send(chat_id, "❌ Dùng: /news ai | crypto | tech")
            else:
                send(chat_id, get_news(parts[1]))

        # ===== TREND =====
        elif text == "/trend":
            send(chat_id, get_trend())

        else:
            send(chat_id, "❓ Không hiểu lệnh")

    return "ok"

# ====== SEND ======
def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
        "chat_id": chat_id,
        "text": text[:4000]
    })

# ====== NEWS ======
def get_news(category):
    urls = {
        "ai": "https://feeds.feedburner.com/oreilly/radar/atom",
        "crypto": "https://cointelegraph.com/rss",
        "tech": "https://feeds.arstechnica.com/arstechnica/index"
    }

    if category not in urls:
        return "❌ Category sai!"

    feed = feedparser.parse(urls[category])
    text = f"📰 Tin {category}:\n\n"

    for entry in feed.entries[:5]:
        text += f"🔹 {entry.title}\n{entry.link}\n\n"

    return text

# ====== TREND ======
def get_trend():
    return "🔥 Trending hôm nay:\n\n- AI tools\n- ChatGPT\n- Crypto pump\n- TikTok viral 😆"

# ====== WEBHOOK SET ======
def set_webhook():
    url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}")

# ====== RUN ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    global TOKEN

    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send(chat_id, "🤖 Bot AI đã sẵn sàng!")

        elif text == "/news":
            send(chat_id, get_news())

        elif text.startswith("/ai"):
            question = text.replace("/ai", "").strip()
            reply = fake_ai(question)
            send(chat_id, reply)

        else:
            send(chat_id, "❓ Không hiểu lệnh")

    return "ok"

# ===== SEND MESSAGE =====
def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# ===== NEWS =====
def get_news():
    feed = feedparser.parse("https://feeds.feedburner.com/oreilly/radar/atom")
    news = "🧠 Tin AI hôm nay:\n\n"

    for entry in feed.entries[:3]:
        news += f"📰 {entry.title}\n{entry.link}\n\n"

    return news

# ===== FAKE AI (test) =====
def fake_ai(text):
    return f"🤖 AI: M vừa hỏi '{text}' (chưa gắn Gemini 😆)"

# ===== SET WEBHOOK =====
def set_webhook():
    global TOKEN
    url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"

    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}"
    )

# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
