import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

# 🔥 2 API (1 chính + 1 backup)
API_MB = [
    "https://freeapi.pro.vn/api/xo-so/mien-bac",
    "https://api.xoso.com.vn/mien-bac"
]

API_MT = [
    "https://freeapi.pro.vn/api/xo-so/mien-trung",
    "https://api.xoso.com.vn/mien-trung"
]

API_MN = [
    "https://freeapi.pro.vn/api/xo-so/mien-nam",
    "https://api.xoso.com.vn/mien-nam"
]

# ================= FETCH (có fallback) =================
def fetch(urls):
    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data:
                    return data
        except:
            continue
    return None

# ================= FORMAT =================
def format_mb(data):
    try:
        return f"""
📅 {data.get('date')}
🎯 ĐB: {data.get('db')}
🥇 G1: {data.get('g1')}
"""
    except:
        return "❌ Lỗi format"

# ================= COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot xổ số OK")

async def mb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = fetch(API_MB)

    if not data:
        await update.message.reply_text("❌ API chết hết rồi 😭")
        return

    await update.message.reply_text(format_mb(data))

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mb", mb))

app.run_polling()
