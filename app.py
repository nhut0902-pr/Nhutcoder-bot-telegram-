from flask import Flask, request, render_template_string
import requests
import os
import feedparser
from google import genai

app = Flask(__name__)

TOKEN = ""
client = genai.Client()  # lấy API từ ENV

HTML = """
<h2>🤖 Setup Bot</h2>
<form method="post">
Token:<br><input name="token"><br><br>
<button type="submit">Save</button>
</form>
"""

# ===== AI (Gemini 3 Flash) =====
def ask_ai(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ AI lỗi: {e}"

# ===== SEARCH =====
def search_web(query):
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json"}
    res = requests.get(url, params=params).json()

    if res.get("AbstractText"):
        return res["AbstractText"]

    if res.get("RelatedTopics"):
        try:
            return res["RelatedTopics"][0]["Text"]
        except:
            return "❌ Không tìm thấy!"

    return "❌ Không có kết quả!"

def search_ai(query):
    raw = search_web(query)
    return ask_ai(f"Tóm tắt ngắn gọn:\n{raw}")

# ===== IMAGE =====
def search_image(query):
    return f"https://source.unsplash.com/600x400/?{query}"

# ===== YOUTUBE =====
def search_youtube(query):
    return f"https://www.youtube.com/results?search_query={query}"

# ===== NEWS =====
def get_news(category):
    urls = {
        "ai": "https://feeds.feedburner.com/oreilly/radar/atom",
        "crypto": "https://cointelegraph.com/rss",
        "tech": "https://feeds.arstechnica.com/arstechnica/index"
    }

    if category not in urls:
        return "❌ Sai category!"

    feed = feedparser.parse(urls[category])
    text = f"📰 Tin {category}:\n\n"

    for entry in feed.entries[:5]:
        text += f"🔹 {entry.title}\n{entry.link}\n\n"

    return text

# ===== TREND =====
def get_trend():
    return "🔥 Trending:\n- AI tools\n- Crypto pump\n- TikTok viral 😆"

# ===== SEND =====
def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
        "chat_id": chat_id,
        "text": text[:4000]
    })

# ===== WEBHOOK =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send(chat_id,
                "🤖 Bot PRO ready!\n\n"
                "/ai hỏi\n"
                "/search keyword\n"
                "/image keyword\n"
                "/yt keyword\n"
                "/news ai|crypto|tech\n"
                "/trend"
            )

        elif text.startswith("/ai"):
            q = text.replace("/ai", "").strip()
            send(chat_id, ask_ai(q))

        elif text.startswith("/search"):
            q = text.replace("/search", "").strip()
            send(chat_id, search_ai(q))

        elif text.startswith("/image"):
            q = text.replace("/image", "").strip()
            send(chat_id, search_image(q))

        elif text.startswith("/yt"):
            q = text.replace("/yt", "").strip()
            send(chat_id, search_youtube(q))

        elif text.startswith("/news"):
            parts = text.split()
            if len(parts) < 2:
                send(chat_id, "❌ /news ai | crypto | tech")
            else:
                send(chat_id, get_news(parts[1]))

        elif text == "/trend":
            send(chat_id, get_trend())

        else:
            send(chat_id, "❓ Không hiểu lệnh")

    return "ok"

# ===== SETUP WEB =====
@app.route("/", methods=["GET", "POST"])
def setup():
    global TOKEN

    if request.method == "POST":
        TOKEN = request.form["token"]
        set_webhook()
        return "✅ Bot ready!"

    return render_template_string(HTML)

def set_webhook():
    url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}")

# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
