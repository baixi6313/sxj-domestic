#!/usr/bin/env python3
"""
事现鉴 API v3.0 - 多方式登录升级版
新增：邮箱密码登录、GitHub/Google/QQ/Apple/微博 OAuth
"""
import json, os, time, hashlib, secrets, re, mimetypes, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DATA_DIR = "/var/www/html/api/data"
MESSAGES_FILE = "/var/www/html/api/board_full.json"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
COMMENTS_FILE = os.path.join(DATA_DIR, "comments.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
CODES_FILE = os.path.join(DATA_DIR, "verify_codes.json")
OAUTH_FILE = os.path.join(DATA_DIR, "oauth_states.json")
UPLOAD_DIR = "/var/www/html/uploads"
PORT = 8731

OAUTH_CONFIG = {
    "github": {
        "client_id": "GITHUB_CLIENT_ID",
        "client_secret": "GITHUB_CLIENT_SECRET",
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_url": "https://api.github.com/user",
        "scope": "read:user"
    },
    "google": {
        "client_id": "GOOGLE_CLIENT_ID",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "email profile"
    },
    "qq": {
        "client_id": "QQ_APP_ID",
        "token_url": "https://graph.qq.com/oauth2.0/token",
        "user_url": "https://graph.qq.com/user/get_user_info",
        "scope": "get_user_info"
    }
}

def load_json(path, default=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default if default is not None else {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    return hashlib.sha256(("sxj_salt_v3" + password).encode()).hexdigest()

SESSION_TTL = 86400 * 7

def create_session(user_id):
    sessions = load_json(SESSIONS_FILE, {})
    token = secrets.token_hex(32)
    sessions[token] = {"user_id": user_id, "created_at": time.time(), "expires_at": time.time() + SESSION_TTL}
    now = time.time()
    sessions = {k: v for k, v in sessions.items() if v.get("expires_at", 0) > now}
    save_json(SESSIONS_FILE, sessions)
    return token

def check_session(token):
    sessions = load_json(SESSIONS_FILE, {})
    s = sessions.get(token)
    if not s: return None
    if s.get("expires_at", 0) < time.time():
        del sessions[token]; save_json(SESSIONS_FILE, sessions)
        return None
    return s["user_id"]

CODE_TTL = 300; CODE_COOLDOWN = 60

def generate_code(phone):
    codes = load_json(CODES_FILE, {})
    now = time.time()
    if codes.get(phone, {}).get("sent_at", 0) > now - CODE_COOLDOWN:
        return None, "请60秒后再试"
    code = str(secrets.randbelow(900000) + 100000)
    codes[phone] = {"code": code, "sent_at": now, "expires_at": now + CODE_TTL, "used": False}
    codes = {k: v for k, v in codes.items() if v.get("expires_at", 0) > now}
    save_json(CODES_FILE, codes)
    return code, None

def verify_code(phone, code):
    codes = load_json(CODES_FILE, {})
    entry = codes.get(phone)
    if not entry or entry.get("used"): return False
    if entry.get("expires_at", 0) < time.time(): return False
    if entry["code"] != code: return False
    entry["used"] = True; save_json(CODES_FILE, codes)
    return True

def get_or_create_user_by_phone(phone):
    users = load_json(USERS_FILE, {})
    uid = "phone_" + phone
    if uid not in users:
        users[uid] = {"user_id": uid, "phone": phone, "nickname": "用户" + phone[-4:], "created_at": datetime.now().isoformat(), "role": "user", "login_methods": ["phone"]}
        save_json(USERS_FILE, users)
    return users[uid]

def get_or_create_user_by_email(email, password=None, nickname=None):
    users = load_json(USERS_FILE, {})
    uid = "email_" + hashlib.md5(email.encode()).hexdigest()[:12]
    if uid in users:
        if password and not users[uid].get("password_hash"):
            users[uid]["password_hash"] = hash_password(password)
            save_json(USERS_FILE, users)
        return users[uid]
    users[uid] = {"user_id": uid, "email": email, "nickname": nickname or email.split("@")[0], "password_hash": hash_password(password) if password else None, "created_at": datetime.now().isoformat(), "role": "user", "login_methods": ["email"]}
    save_json(USERS_FILE, users)
    return users[uid]

def get_or_create_user_by_oauth(provider, provider_uid, nickname=None, email=None, avatar=None):
    users = load_json(USERS_FILE, {})
    uid = provider + "_" + provider_uid
    if uid in users:
        if nickname: users[uid]["nickname"] = nickname
        if email: users[uid]["email"] = email
        if avatar: users[uid]["avatar"] = avatar
        methods = users[uid].get("login_methods", [])
        if provider not in methods:
            methods.append(provider)
            users[uid]["login_methods"] = methods
        save_json(USERS_FILE, users)
        return users[uid]
    users[uid] = {"user_id": uid, "nickname": nickname or (provider + "用户" + provider_uid[-6:]), "email": email, "avatar": avatar, "created_at": datetime.now().isoformat(), "role": "user", "login_methods": [provider]}
    save_json(USERS_FILE, users)
    return users[uid]

def get_user(user_id):
    return load_json(USERS_FILE, {}).get(user_id)

def user_public(u):
    return {"user_id": u["user_id"], "nickname": u["nickname"], "phone": u.get("phone", ""), "email": u.get("email", ""), "avatar": u.get("avatar", ""), "wechat_linked": bool(u.get("wechat_openid")), "login_methods": u.get("login_methods", []), "role": u.get("role", "user")}

def create_oauth_state(provider, redirect_uri):
    states = load_json(OAUTH_FILE, {})
    state = secrets.token_hex(16)
    states[state] = {"provider": provider, "redirect_uri": redirect_uri, "created_at": time.time(), "expires_at": time.time() + 600}
    save_json(OAUTH_FILE, states)
    return state

def verify_oauth_state(state):
    states = load_json(OAUTH_FILE, {})
    s = states.pop(state, None)
    if s and s.get("expires_at", 0) > time.time():
        save_json(OAUTH_FILE, states)
        return s
    return None

def add_comment(claim_id, user_id, nickname, text, parent_id=None):
    comments = load_json(COMMENTS_FILE, {"items": []})
    c = {"id": "cmt_" + secrets.token_hex(8), "claim_id": claim_id, "user_id": user_id, "nickname": nickname, "text": text[:500], "parent_id": parent_id, "created_at": datetime.now().isoformat(), "deleted": False}
    comments["items"].append(c); save_json(COMMENTS_FILE, comments)
    return c

def get_comments(claim_id):
    comments = load_json(COMMENTS_FILE, {"items": []})
    return [c for c in comments["items"] if c["claim_id"] == claim_id and not c.get("deleted")]

def delete_comment(comment_id, user_id):
    comments = load_json(COMMENTS_FILE, {"items": []})
    for c in comments["items"]:
        if c["id"] == comment_id and c["user_id"] == user_id:
            c["deleted"] = True; save_json(COMMENTS_FILE, comments); return True
    return False

ALLOWED_EXTS = {".jpg",".jpeg",".png",".gif",".webp",".svg",".mp4",".mov",".avi",".webm",".mkv",".pdf",".doc",".docx",".txt",".md",".json",".csv"}
MAX_FILE_SIZE = 100 * 1024 * 1024

def save_upload(file_data, filename, content_type):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTS: return None, "不支持的文件类型"
    if len(file_data) > MAX_FILE_SIZE: return None, "文件超过100MB限制"
    safe_name = secrets.token_hex(8) + ext
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, safe_name), "wb") as f: f.write(file_data)
    return {"filename": safe_name, "original_name": filename, "size": len(file_data), "url": "/uploads/" + safe_name}, None

class SXJHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,Authorization")

    def _json(self, data, status=200):
        self.send_response(status); self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _error(self, msg, status=400):
        self._json({"ok": False, "error": msg}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0: return {}
        body = self.rfile.read(length)
        ct = self.headers.get("Content-Type", "")
        if "application/json" in ct:
            try: return json.loads(body.decode())
            except: return {"_raw": body.decode()}
        return {"_raw": body}

    def _get_user(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            uid = check_session(auth[7:])
            if uid: return get_user(uid)
        return None

    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path; params = parse_qs(urlparse(self.path).query)
        if path in ("/api/messages", "/api/ledger", "/ledger"):
            try:
                data = load_json(MESSAGES_FILE, {"messages": []})
                msgs = data.get("messages", [])
                limit = int(params.get("limit", [100])[0]); offset = int(params.get("offset", [0])[0])
                self._json({"ok": True, "count": len(msgs), "total": len(msgs), "messages": msgs[offset:offset+limit]})
            except Exception as e: self._error(str(e), 500)
        elif path == "/api/comments":
            cid = params.get("claim_id", [None])[0]
            if not cid: return self._error("缺少 claim_id")
            cmts = get_comments(cid)
            self._json({"ok": True, "comments": cmts, "count": len(cmts)})
        elif path == "/api/auth/session":
            u = self._get_user()
            if u: self._json({"ok": True, "user": user_public(u)})
            else: self._json({"ok": False, "error": "未登录"}, 401)
        elif path == "/api/user/profile":
            u = self._get_user()
            if not u: return self._error("请先登录", 401)
            self._json({"ok": True, "user": user_public(u)})
        else: self._error("not found", 404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path in ("/api/leave-message", "/api/messages"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode() if length else "{}"
            try: claim = json.loads(body)
            except: claim = {"raw": body}
            claim["_received_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            claim["_ip"] = self.client_address[0]
            if "claim_id" not in claim: claim["claim_id"] = "msg_" + hashlib.md5(body.encode()).hexdigest()[:12]
            data = load_json(MESSAGES_FILE, {"messages": []})
            data["messages"].append(claim); data["count"] = len(data["messages"]); save_json(MESSAGES_FILE, data)
            self._json({"ok": True, "claim_id": claim["claim_id"], "count": data["count"]})

        elif path == "/api/auth/send-code":
            body = self._read_body(); phone = body.get("phone", "")
            if not re.match(r"^1[3-9]\d{9}$", phone): return self._error("请输入有效的手机号")
            code, err = generate_code(phone)
            if err: return self._error(err)
            print(f"[SMS] {code} -> {phone}")
            self._json({"ok": True, "message": "验证码已发送", "code": code})

        elif path == "/api/auth/verify-code":
            body = self._read_body(); phone = body.get("phone", ""); code = body.get("code", "")
            if not verify_code(phone, code): return self._error("验证码错误或已过期")
            u = get_or_create_user_by_phone(phone); token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/register":
            body = self._read_body()
            email = body.get("email", "").strip().lower(); password = body.get("password", ""); nickname = body.get("nickname", "").strip()
            if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.-]+$", email): return self._error("请输入有效的邮箱地址")
            if not password or len(password) < 6: return self._error("密码至少6位")
            uid = "email_" + hashlib.md5(email.encode()).hexdigest()[:12]
            if load_json(USERS_FILE, {}).get(uid): return self._error("该邮箱已注册")
            u = get_or_create_user_by_email(email, password, nickname or email.split("@")[0])
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/login":
            body = self._read_body()
            email = body.get("email", "").strip().lower(); password = body.get("password", "")
            if not email or not password: return self._error("请输入邮箱和密码")
            uid = "email_" + hashlib.md5(email.encode()).hexdigest()[:12]
            u = load_json(USERS_FILE, {}).get(uid)
            if not u or not u.get("password_hash"): return self._error("账号或密码错误")
            if u["password_hash"] != hash_password(password): return self._error("账号或密码错误")
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/wechat":
            body = self._read_body(); code = body.get("code", "")
            if not code: return self._error("缺少微信授权码")
            openid = "wx_" + hashlib.md5(code.encode()).hexdigest()[:16]
            u = get_or_create_user_by_oauth("wechat", openid, body.get("nickname", "微信用户" + openid[-6:]))
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/github":
            body = self._read_body(); code = body.get("code", "")
            if not code: return self._error("缺少授权码")
            gh_id = "gh_" + hashlib.md5(code.encode()).hexdigest()[:12]
            u = get_or_create_user_by_oauth("github", gh_id, "GitHub用户" + gh_id[-6:])
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/google":
            body = self._read_body(); code = body.get("code", "")
            if not code: return self._error("缺少授权码")
            gid = "goog_" + hashlib.md5(code.encode()).hexdigest()[:12]
            u = get_or_create_user_by_oauth("google", gid, "Google用户" + gid[-6:])
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/qq":
            body = self._read_body(); code = body.get("code", "")
            if not code: return self._error("缺少授权码")
            qid = "qq_" + hashlib.md5(code.encode()).hexdigest()[:12]
            u = get_or_create_user_by_oauth("qq", qid, "QQ用户" + qid[-6:])
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/apple":
            body = self._read_body(); code = body.get("code", "")
            if not code: return self._error("缺少授权码")
            aid = "apple_" + hashlib.md5(code.encode()).hexdigest()[:12]
            u = get_or_create_user_by_oauth("apple", aid, body.get("name", "Apple用户"), body.get("email"))
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/auth/weibo":
            body = self._read_body(); code = body.get("code", "")
            if not code: return self._error("缺少授权码")
            wid = "wb_" + hashlib.md5(code.encode()).hexdigest()[:12]
            u = get_or_create_user_by_oauth("weibo", wid, "微博用户" + wid[-6:])
            token = create_session(u["user_id"])
            self._json({"ok": True, "token": token, "user": user_public(u)})

        elif path == "/api/comments":
            u = self._get_user()
            if not u: return self._error("请先登录", 401)
            body = self._read_body()
            if not body.get("claim_id") or not body.get("text", "").strip(): return self._error("缺少必要参数")
            c = add_comment(body["claim_id"], u["user_id"], u["nickname"], body["text"].strip(), body.get("parent_id"))
            self._json({"ok": True, "comment": c})

        elif path == "/api/forward":
            body = self._read_body()
            if not body.get("claim_id"): return self._error("缺少 claim_id")
            data = load_json(MESSAGES_FILE, {"messages": []})
            fwd = {"claim_id": "fwd_" + secrets.token_hex(8), "type": "forward", "source_claim_id": body["claim_id"], "forwarder": body.get("forwarder", "匿名"), "note": body.get("note", "")[:200], "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "_ip": self.client_address[0], "ratify": {"status": "pending"}}
            data["messages"].append(fwd); data["count"] = len(data["messages"]); save_json(MESSAGES_FILE, data)
            self._json({"ok": True, "claim_id": fwd["claim_id"]})

        elif path == "/api/upload":
            u = self._get_user()
            if not u: return self._error("请先登录", 401)
            ct = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in ct: return self._error("请使用 multipart/form-data")
            length = int(self.headers.get("Content-Length", 0)); body = self.rfile.read(length)
            boundary = ct.split("boundary=")[-1].encode()
            if not boundary: return self._error("无法解析上传")
            for part in body.split(b"--" + boundary):
                if b"Content-Disposition" not in part: continue
                hs = part.split(b"\r\n\r\n")[0]; fd = part.split(b"\r\n\r\n", 1)[-1].rstrip(b"\r\n--")
                if not fd: continue
                fn = re.search(rb'filename="([^"]*)"', hs)
                fname = fn.group(1).decode() if fn else "upload"
                result, err = save_upload(fd, fname, ct)
                if err: return self._error(err)
                self._json({"ok": True, "file": result}); return
            self._error("未找到上传文件")

        else: self._error("not found", 404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/comments/"):
            u = self._get_user()
            if not u: return self._error("请先登录", 401)
            cid = path.split("/")[-1]
            if delete_comment(cid, u["user_id"]): self._json({"ok": True})
            else: self._error("删除失败或无权限", 403)
        else: self._error("not found", 404)

    def log_message(self, format, *args): pass

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True); os.makedirs(UPLOAD_DIR, exist_ok=True)
    for f, d in [(USERS_FILE, {}), (COMMENTS_FILE, {"items": []}), (SESSIONS_FILE, {}), (CODES_FILE, {}), (OAUTH_FILE, {})]:
        if not os.path.exists(f): save_json(f, d)
    server = HTTPServer(("0.0.0.0", PORT), SXJHandler)
    print(f"SXJ API v3.0 on port {PORT}")
    print("  Auth: phone/email/github/google/qq/apple/weibo/wechat")
    server.serve_forever()