#!/usr/bin/env python3
"""事现鉴 API v2 - 收发室程序（append-only加固版）
Gzz-E-DEPLOY-20260824-002：技术债修复第1项——原子写入 + 自动备份 + 速率限制
"""
import json, os, time, hashlib, tempfile, shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from collections import defaultdict

DATA_FILE = "/var/www/html/api/board_full.json"
BACKUP_DIR = "/var/www/html/api/backups"
PORT = 8731

# 速率限制：每IP每分钟最多30次POST
rate_limit = defaultdict(list)

def atomic_write(filepath, data):
    """原子写入：先写临时文件，再 rename，防止写入中断导致数据损坏"""
    dirname = os.path.dirname(filepath)
    fd, tmp_path = tempfile.mkstemp(dir=".tmp", dir=dirname)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

def backup_data():
    """写入前自动备份"""
    if not os.path.exists(DATA_FILE):
        return
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"board_full_{ts}.json")
    shutil.copy2(DATA_FILE, backup_path)
    # 保留最近100个备份
    backups = sorted(os.listdir(BACKUP_DIR))
    while len(backups) > 100:
        os.unlink(os.path.join(BACKUP_DIR, backups.pop(0)))

def check_rate_limit(ip):
    """检查速率限制，返回True=允许"""
    now = time.time()
    rate_limit[ip] = [t for t in rate_limit[ip] if now - t < 60]
    if len(rate_limit[ip]) >= 30:
        return False
    rate_limit[ip].append(now)
    return True

class SXJHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/api/messages", "/api/ledger", "/ledger", "/api/health"):
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            if path == "/api/health":
                self.wfile.write(json.dumps({"ok": True, "status": "append-only"}).encode())
                return
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                msgs = data.get("messages", [])
                resp = {"ok": True, "count": len(msgs), "messages": msgs}
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()
            self.wfile.write(b'{"ok":false,"error":"not found"}')

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/leave-message", "/api/messages"):
            self.send_response(404)
            self._cors()
            self.end_headers()
            self.wfile.write(b'{"ok":false,"error":"not found"}')
            return

        # 速率限制
        ip = self.client_address[0]
        if not check_rate_limit(ip):
            self.send_response(429)
            self._cors()
            self.end_headers()
            self.wfile.write(b'{"ok":false,"error":"rate limit exceeded"}')
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else "{}"
        try:
            claim = json.loads(body)
        except:
            claim = {"raw": body}

        claim["_received_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        claim["_ip"] = ip
        if "claim_id" not in claim:
            claim["claim_id"] = "msg_" + hashlib.md5(body.encode()).hexdigest()[:12]

        # 写入前备份
        backup_data()

        # 原子写入：加载→追加→原子写入
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {"ok": True, "count": 0, "messages": []}
        data["messages"].append(claim)
        data["count"] = len(data["messages"])

        atomic_write(DATA_FILE, data)

        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        resp = {"ok": True, "claim_id": claim["claim_id"], "count": data["count"]}
        self.wfile.write(json.dumps(resp, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        pass  # silent

if __name__ == "__main__":
    os.makedirs(BACKUP_DIR, exist_ok=True)
    server = HTTPServer(("0.0.0.0", PORT), SXJHandler)
    print(f"SXJ API v2 running on port {PORT} (append-only + atomic write + rate limit)")
    server.serve_forever()