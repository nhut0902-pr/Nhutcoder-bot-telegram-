from flask import Flask, request, render_template_string
import requests
import os
import feedparser

app = Flask(__name__)

# lưu tạm (có thể thay bằng DB sau)
TOKEN = ""
CHAT_ID = ""

HTML = """
<h2>🤖 Setup Telegram Bot</h2>
<form method="post">
    Token:<br>
    <input name="token"><br><br>
    Chat ID:<br>
    <input name="chat_id"><br><br>
    <button type="submit">Save</button>
</form>
"""

@app.route("/", methods=["GET", "POST"])
def setup():
    global TOKEN, CHAT_ID

    if request.method == "POST":
        TOKEN = request.form["token"]
        CHAT_ID = request.form["chat_id"]

        set_webhook()

        return "✅ Đã lưu & set webhook!"

    return render_template_string(HTML)

# ===== WEBHOOK =====
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
