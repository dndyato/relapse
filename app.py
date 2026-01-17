import os
import sys
import subprocess
import platform
import shutil
from flask import Flask, render_template, request
from threading import Thread
import time

app = Flask(__name__)

# ----------------------- FLASK ROUTE -----------------------
@app.route("/", methods=["GET", "POST"])
def home():
    trigger = False
    if request.method == "POST":
        expr = request.form.get("expr")
        if expr == "1+1":
            trigger = True
    return render_template("index.html", trigger=trigger)

# ------------------- NGROK SETUP --------------------------
def start_ngrok():
    # Check if ngrok exists
    if not shutil.which("ngrok"):
        print("[*] Downloading ngrok...")
        arch = platform.machine()
        url = ""
        if arch == "aarch64":
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.zip"
        elif arch.startswith("arm"):
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.zip"
        elif platform.system() == "Windows":
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        elif platform.system() == "Darwin":
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip"
        else:
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"

        # Download
        fname = "ngrok.zip"
        os.system(f"wget -O {fname} {url} -q")
        os.system(f"unzip -o {fname}")
        os.system("chmod +x ngrok")
        shutil.move("ngrok", os.path.join(os.getcwd(), "ngrok"))
        os.remove(fname)
        ngrok_path = os.path.join(os.getcwd(), "ngrok")
    else:
        ngrok_path = shutil.which("ngrok")

    # Start ngrok
    print("[*] Starting ngrok tunnel...")
    # ngrok command
    cmd = [ngrok_path, "http", "5000"]
    # Use subprocess and capture output
    ngrok_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait a few seconds for ngrok to start
    time.sleep(5)
    # Try to fetch public url
    try:
        import requests
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        public_url = tunnels['tunnels'][0]['public_url']
        print("\n🔥 Public URL:", public_url)
    except:
        print("[!] Could not get ngrok public URL. Check ngrok manually.")

# -------------------- MAIN -------------------------------
if __name__ == "__main__":
    # Start ngrok in a thread
    t = Thread(target=start_ngrok)
    t.daemon = True
    t.start()

    print("[*] Starting Flask server at http://127.0.0.1:5000")
    app.run(port=5000)