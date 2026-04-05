import json
import requests
import feedparser
import schedule
import time

def load_config():
    with open("config.json") as f:
        return json.load(f)

def ask_gemini(api_key, text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }

    res = requests.post(url, json=data)
    try:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Lỗi AI"

def send_news():
    config = load_config()
    TOKEN = config["TOKEN"]
    CHAT_ID = config["CHAT_ID"]
    GEMINI = config["GEMINI_API_KEY"]

    feed = feedparser.parse("https://news.google.com/rss/search?q=ai")
    articles = feed.entries[:3]

    msg = "🔥 Tin AI:\n\n"

    for a in articles:
        summary = ask_gemini(GEMINI, a.title)
        msg += f"{a.title}\n🧠 {summary}\n🔗 {a.link}\n\n"

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def start_bot():
    schedule.every().day.at("00:00").do(send_news)

    while True:
        schedule.run_pending()
        time.sleep(60)
