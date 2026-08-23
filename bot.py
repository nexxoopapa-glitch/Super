import sqlite3
import requests
import time

TOKEN = "8817520531:AAEfkAhpIEtgT_lsGjCzg8PRiinavpsMaAc"
DB_PATH = "avj1.db"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

last_update_id = 0

def get_updates():
    global last_update_id
    url = BASE_URL + "getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 10}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json().get("result", [])
    except:
        return []

def send(chat_id, text):
    try:
        requests.get(BASE_URL + "sendMessage", params={"chat_id": chat_id, "text": text[:4000]}, timeout=10)
    except:
        pass

def search_db(query):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT mobile, name, fname, address, circle FROM data WHERE name LIKE ? OR address LIKE ? LIMIT 5", (f'%{query}%', f'%{query}%'))
    rows = c.fetchall()
    conn.close()
    return rows

def search_mobile(num):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT mobile, name, fname, address, circle FROM data WHERE mobile LIKE ? LIMIT 5", (f'%{num}%',))
    rows = c.fetchall()
    conn.close()
    return rows

print("🤖 Bot chal raha hai...")

while True:
    updates = get_updates()
    for upd in updates:
        last_update_id = upd["update_id"]
        msg = upd.get("message")
        if not msg:
            continue
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            send(chat_id, "✅ Bot ready!\n/search name\n/mobile number")

        elif text.startswith("/search"):
            q = text.replace("/search", "").strip()
            if not q:
                send(chat_id, "Type: /search name")
                continue
            rows = search_db(q)
            if not rows:
                send(chat_id, "❌ Not found")
            else:
                reply = "✅ Results:\n\n"
                for r in rows:
                    reply += f"📱 {r[0]}\n👤 {r[1]}\n👨 {r[2]}\n📍 {r[3][:50]}...\n📡 {r[4]}\n---\n"
                send(chat_id, reply)

        elif text.startswith("/mobile"):
            num = text.replace("/mobile", "").strip()
            if not num:
                send(chat_id, "Type: /mobile 9905681420")
                continue
            rows = search_mobile(num)
            if not rows:
                send(chat_id, "❌ Not found")
            else:
                reply = "📱 Mobile results:\n\n"
                for r in rows:
                    reply += f"Name: {r[1]}\nFather: {r[2]}\nAddress: {r[3][:50]}\nCircle: {r[4]}\n---\n"
                send(chat_id, reply)

        else:
            send(chat_id, "Use /search or /mobile")

    time.sleep(1)
