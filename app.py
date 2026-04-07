import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

# API endpoints
API_MB = "https://freeapi.pro.vn/api/xo-so/mien-bac"
API_MT = "https://freeapi.pro.vn/api/xo-so/mien-trung"
API_MN = "https://freeapi.pro.vn/api/xo-so/mien-nam"

# ================== HELPER ==================
def fetch(url):
    try:
        return requests.get(url, timeout=10).json()
    except:
        return None

def format_kq(data):
    try:
        return f"""
📅 {data['date']}
🎯 ĐB: {data['db']}
🥇 G1: {data['g1']}
🥈 G2: {', '.join(data['g2'])}
🥉 G3: {', '.join(data['g3'])}
"""
    except:
        return "❌ Lỗi format dữ liệu"

# ================== COMMAND ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot xổ số\n\n"
        "/mb - Miền Bắc\n"
        "/mt - Miền Trung\n"
        "/mn - Miền Nam\n"
        "/tinh khanhhoa\n"
        "/do 68"
    )

# ===== MIỀN =====
async def mb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = fetch(API_MB)
    await update.message.reply_text(format_kq(data) if data else "❌ Lỗi API")

async def mt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = fetch(API_MT)
    await update.message.reply_text(format_kq(data) if data else "❌ Lỗi API")

async def mn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = fetch(API_MN)
    await update.message.reply_text(format_kq(data) if data else "❌ Lỗi API")

# ===== THEO TỈNH =====
async def tinh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Ví dụ: /tinh khanhhoa")
        return

    name = context.args[0].lower()

    data_mt = fetch(API_MT)
    data_mn = fetch(API_MN)

    # gộp miền trung + nam
    all_data = []
    if data_mt: all_data.append(data_mt)
    if data_mn: all_data.append(data_mn)

    for region in all_data:
        for province in region.get("provinces", []):
            if name in province["name"].lower().replace(" ", ""):
                msg = f"📍 {province['name']}\n"
                msg += f"🎯 ĐB: {province['db']}\n"
                msg += f"🥇 G1: {province['g1']}\n"
                await update.message.reply_text(msg)
                return

    await update.message.reply_text("❌ Không tìm thấy tỉnh")

# ===== DÒ SỐ =====
async def do(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Ví dụ: /do 68")
        return

    number = context.args[0]

    data_all = [fetch(API_MB), fetch(API_MT), fetch(API_MN)]
    found = []

    for data in data_all:
        if not data:
            continue

        # miền Bắc
        if "db" in data:
            for key, val in data.items():
                if isinstance(val, list):
                    for v in val:
                        if number in str(v):
                            found.append(v)
                else:
                    if number in str(val):
                        found.append(val)

        # miền Trung/Nam
        if "provinces" in data:
            for p in data["provinces"]:
                for key, val in p.items():
                    if isinstance(val, list):
                        for v in val:
                            if number in str(v):
                                found.append(v)
                    else:
                        if number in str(val):
                            found.append(val)

    if found:
        await update.message.reply_text(f"🎉 TRÚNG: {', '.join(found)}")
    else:
        await update.message.reply_text("❌ Không trúng")

# ================== RUN ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mb", mb))
app.add_handler(CommandHandler("mt", mt))
app.add_handler(CommandHandler("mn", mn))
app.add_handler(CommandHandler("tinh", tinh))
app.add_handler(CommandHandler("do", do))

app.run_polling()
