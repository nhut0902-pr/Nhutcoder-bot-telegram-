import os
import nest_asyncio
import cloudscraper
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.helpers import escape_markdown
from datetime import datetime
import re

nest_asyncio.apply()

def clean_prize_text(text):
    text = re.sub(r'(Normal|2 số|3 Số|Xem Bảng Loto|Đổi số trúng|In Vé Dò|Hình vé số|KẾT QUẢ .*?ĐIỆN TOÁN|Xem thêm).*', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_full_3mien():
    print("🔥 Hack minhngoc.net.vn như điên...")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
    try:
        r = scraper.get("https://www.minhngoc.net.vn/", timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        today = datetime.now().strftime("%d/%m/%Y")
        raw_msg = f"🤑 **FULL 3 MIỀN - {today}** 🤑\n\n"
        
        # XSMB sạch
        mb_text = "XSMB: Chưa có"
        db_tag = soup.find(string=re.compile(r'Giải ĐB|Giải Đặc Biệt', re.I))
        if db_tag and (parent := db_tag.find_parent(['div', 'table'])):
            mb_text = clean_prize_text(parent.get_text(separator="\n", strip=True))
            mb_text = re.sub(r'Giải ĐB.*?(\d+)', r'🎰 ĐẶC BIỆT: \1', mb_text, flags=re.I)
        
        raw_msg += f"🌟 **XSMB**\n{mb_text}\n\n🌴 **XSMN**\n{clean_prize_text(str(soup))[:900]}...\n\n🌊 **XSMT**\n{clean_prize_text(str(soup))[:900]}..."
        return raw_msg
    except Exception as e:
        return f"Địt mẹ lỗi: {str(e)}"

async def fullmien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Đang phá minhngoc.net.vn, chờ 3s đi cặc...")
    msg = scrape_full_3mien()
    await update.message.reply_text(escape_markdown(msg, version=2), parse_mode='MarkdownV2')

TOKEN = os.getenv("TOKEN")
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler(["fullmien", "scrape"], fullmien))

if __name__ == "__main__":
    print("🚀 Bot Fly.io chạy như hacker chống phá Cloudflare!")
    app.run_polling(drop_pending_updates=True)
