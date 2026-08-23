from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
import json
import time
import os

DB_PATH = "avj1.db"
API_KEY = "YOUR_SECRET_KEY_123"

rate_store = {}

def is_rate_limited(api_key):
    now = time.time()
    if api_key not in rate_store:
        rate_store[api_key] = []
    rate_store[api_key] = [t for t in rate_store[api_key] if now - t < 60]
    if len(rate_store[api_key]) >= 10:
        return True
    rate_store[api_key].append(now)
    return False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        headers = self.headers
        provided_key = headers.get("X-API-Key")
        if not provided_key or provided_key != API_KEY:
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid or missing API key"}).encode())
            return

        if is_rate_limited(provided_key):
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Rate limit exceeded (10 req/min)"}).encode())
            return

        if path == "/search" and "q" in query:
            q = query["q"][0]
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT mobile, name, fname, address, circle FROM data WHERE name LIKE ? OR address LIKE ? LIMIT 10", (f'%{q}%', f'%{q}%'))
            rows = cursor.fetchall()
            conn.close()

            results = []
            for row in rows:
                results.append({
                    "mobile": row[0],
                    "name": row[1],
                    "fname": row[2],
                    "address": row[3],
                    "circle": row[4]
                })

            response = {"status": "success", "query": q, "count": len(results), "results": results}

        elif path == "/mobile" and "num" in query:
            num = query["num"][0]
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT mobile, name, fname, address, circle FROM data WHERE mobile LIKE ? LIMIT 10", (f'%{num}%',))
            rows = cursor.fetchall()
            conn.close()

            results = []
            for row in rows:
                results.append({
                    "mobile": row[0],
                    "name": row[1],
                    "fname": row[2],
                    "address": row[3],
                    "circle": row[4]
                })

            response = {"status": "success", "query": num, "count": len(results), "results": results}

        else:
            response = {"status": "error", "message": "Use /search?q=name OR /mobile?num=123"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

print("🔐 Secure API chal raha hai: http://localhost:8000")
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
