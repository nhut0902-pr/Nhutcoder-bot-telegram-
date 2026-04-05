from flask import Flask, render_template, request
import os
import json
import threading
from bot import start_bot

app = Flask(__name__)

CONFIG_FILE = "config.json"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = {
            "TOKEN": request.form["token"],
            "CHAT_ID": request.form["chat_id"],
            "GEMINI_API_KEY": request.form["gemini"]
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

        # chạy bot sau khi lưu
        threading.Thread(target=start_bot).start()

        return "✅ Đã lưu và chạy bot!"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
