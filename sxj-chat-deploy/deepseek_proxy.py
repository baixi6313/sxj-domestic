#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事现鉴 · SXJ 模型调度代理 v2（Lighthouse 版，零第三方依赖）
POST /api/chat  { "messages":[...], "model":"...", "stream":true, "session":"..." }
GET  /api/models → 已配置 Key 的可用模型列表（label=对外品牌，sub=底层驱动）
对话落库 /opt/sxj-chat/history.db（SQLite，只增不删）
对话记录自动同步公示墙（开关：/opt/sxj-chat/wall_on.txt 存在即开启）
站内知识 RAG：/opt/sxj-chat/knowledge.json（hygzz.cn 站内页面切片）
Key 文件（同目录）：key.txt=DeepSeek，glm_key.txt=智谱，hy4_key.txt=腾讯TokenHub
监听 127.0.0.1:8812，由 Nginx location = /api/chat 反代
"""
import json, os, re, sqlite3, hashlib, threading, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8812
DB = os.path.join(DIR, "history.db")
WALL_FLAG = os.path.join(DIR, "wall_on.txt")
WALL_URL = "http://127.0.0.1/api/messages"

MODELS = {
    "deepseek-v4-flash": {"label": "SXJ · 快速", "sub": "DeepSeek V4-Flash",
                          "upstream": "https://api.deepseek.com/chat/completions",
                          "key_file": "key.txt", "env": "DEEPSEEK_API_KEY", "vendor": "DeepSeek"},
    "deepseek-v4-pro":   {"label": "SXJ · 深度", "sub": "DeepSeek V4-Pro",
                          "upstream": "https://api.deepseek.com/chat/completions",
                          "key_file": "key.txt", "env": "DEEPSEEK_API_KEY", "vendor": "DeepSeek"},
    "glm-5.3-flash":     {"label": "SXJ · 均衡", "sub": "智谱 GLM-5.3-Flash",
                          "upstream": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                          "key_file": "glm_key.txt", "env": "ZHIPU_API_KEY", "vendor": "智谱GLM"},
    "hy4-preview":       {"label": "SXJ · 强力", "sub": "腾讯混元 Hy4 预览版",
                          "upstream": "https://tokenhub.tencentmaas.com/v1/chat/completions",
                          "key_file": "hy4_key.txt", "env": "TOKENHUB_API_KEY", "vendor": "腾讯混元"},
}

SYSTEM_PROMPT = """你是「事现鉴」（hygzz.cn）站内的 AI 助手，对外统一名称为「SXJ 模型」。

当访客问你是谁/由什么模型生成时：回答"我的回答由 SXJ 模型生成，涉及事实请以 hygzz.cn 公示墙与 GitHub 公开记录为准"。只有当访客明确追问底层技术架构时，才如实说明：SXJ 是多模型调度架构，当前可选底层包括 DeepSeek、智谱GLM、腾讯混元等，页面下拉框中可切换，不要主动罗列厂商。

事现鉴（SXJ）是基于可验证公共事实的开放协议：银行征信看你能借多少钱，事现鉴征信看你创造多少价值。核心概念：
- 事实记录与验证：对现实中发生的事进行识别、记录、验证、映射，让事实成为协作与制度设计的基础。
- Gzz 编码体系：给术语、实体、事件分配可验证的哈希编码，公开可复算（公式形如 sha256(summary|REC|timestamp)[:8]）。
- 贡献征信：记录个人与组织的真实贡献，服务于社会保障与共创分配。
- 只增不删：记录一旦上链公示，不删改、只追加修正。本页对话记录会同步至公示墙公开留档。

回答要求：
1. 立场中立、克制，不夸大，不代替官方承诺。
2. 用简体中文回答，简洁直接；技术问题可给代码或公式。
3. 不知道的事就说不知道，不要编造。"""

def json_bytes(obj, status=200):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return status, [("Content-Type", "application/json; charset=utf-8"),
                    ("Access-Control-Allow-Origin", "*")], body

def load_key(mid):
    m = MODELS[mid]
    k = os.environ.get(m["env"], "").strip()
    if k:
        return k
    p = os.path.join(DIR, m["key_file"])
    if os.path.exists(p):
        try:
            return open(p, encoding="utf-8").read().strip()
        except Exception:
            return ""
    return ""

def load_knowledge():
    try:
        d = json.load(open(os.path.join(DIR, "knowledge.json"), encoding="utf-8"))
        return d if isinstance(d, list) else []
    except Exception:
        return []

KNOWLEDGE = load_knowledge()

def search_knowledge(q, topk=3):
    """字符 2-gram 打分检索站内知识切片，零依赖轻量 RAG"""
    if not KNOWLEDGE or not q:
        return []
    q = q.strip()
    if len(q) > 1:
        grams = {q[i:i + 2] for i in range(len(q) - 1)}
    else:
        grams = {q}
    grams = {g for g in grams if g.strip()}
    if not grams:
        return []
    scored = []
    for c in KNOWLEDGE:
        text = c.get("text", "")
        s = 0
        for g in grams:
            if g in text:
                s += text.count(g)
        if s > 0:
            scored.append((s, c))
    if not scored:
        return []
    scored.sort(key=lambda x: -x[0])
    threshold = max(2, len(grams) // 12)
    return [c for s, c in scored[:topk] if s >= threshold]

def db_init():
    try:
        c = sqlite3.connect(DB)
        c.execute("""CREATE TABLE IF NOT EXISTS chat_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, session TEXT, model TEXT,
            user_msg TEXT, ai_reply TEXT,
            wall_ok INTEGER DEFAULT 0, wall_msg TEXT DEFAULT '')""")
        c.commit(); c.close()
    except Exception:
        pass

def save_chat(session, model, umsg, areply):
    try:
        c = sqlite3.connect(DB)
        c.execute("INSERT INTO chat_log(ts,session,model,user_msg,ai_reply) VALUES(?,?,?,?,?)",
                  (time.strftime("%Y-%m-%d %H:%M:%S"), (session or "anon")[:64], model,
                   (umsg or "")[:6000], (areply or "")[:12000]))
        c.commit(); c.close()
    except Exception:
        pass

def post_wall(session, model, umsg, areply):
    """对话记录作为公开事实投递公示墙（异步线程中执行，失败静默）。
    v1.1: 端点与payload对齐公示墙规范 /api/messages（agent+content.text），补必需头4项。"""
    if not os.path.exists(WALL_FLAG):
        return
    try:
        u = (umsg or "").strip()[:300].replace("\n", " ")
        a = (areply or "").strip()[:600].replace("\n", " ")
        if not u:
            return
        h = hashlib.sha256(((session or "anon") + "|" + u + "|" + a).encode("utf-8")).hexdigest()
        text = ("【AI对话记录】\n访客问：%s\n鉴答（%s）：%s\n\n"
                "[对话哈希 sha256:%s] [事现鉴·只增不删] [内容由 AI 生成，可能存在偏差]" % (u, model, a, h[:16]))
        payload = json.dumps({
            "agent": {"name": "SXJ·对话存证", "platform": "hygzz-chat"},
            "content": {"text": text},
        }, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(WALL_URL, data=payload, headers={
            "Content-Type": "application/json",
            "User-Agent": "SXJ-ChatLogger/1.1 (+https://hygzz.cn/chat.html)",
            "X-SXJ-Protocol": "SXJ/2026-08-15",
            "Origin": "https://hygzz.xn--fiqs8s/",
            "Referer": "https://hygzz.xn--fiqs8s/"}, method="POST")
        urllib.request.urlopen(req, timeout=15).read()
    except Exception:
        pass

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204); self._cors()
        self.send_header("Content-Length", "0"); self.end_headers()

    def _reply(self, status, headers, body, stream=False):
        self.send_response(status)
        for k, v in headers:
            self.send_header(k, v)
        if not stream:
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if stream:
            return
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") == "/api/models":
            items = [{"id": mid, "label": m["label"], "sub": m.get("sub", ""), "vendor": m["vendor"],
                      "ready": bool(load_key(mid))} for mid, m in MODELS.items()]
            s, h, b = json_bytes({"ok": True, "knowledge_chunks": len(KNOWLEDGE), "models": items})
            return self._reply(s, h, b)
        s, h, b = json_bytes({"ok": False, "error": "not found"}, 404)
        return self._reply(s, h, b)

    def do_POST(self):
        if self.path.rstrip("/") != "/api/chat":
            s, h, b = json_bytes({"ok": False, "error": "not found"}, 404)
            return self._reply(s, h, b)

        try:
            n = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            s, h, b = json_bytes({"error": "请求体不是合法 JSON"}, 400)
            return self._reply(s, h, b)

        msgs = body.get("messages") if isinstance(body.get("messages"), list) else []
        msgs = [{"role": m.get("role"), "content": str(m.get("content", ""))[:6000]}
                for m in msgs if isinstance(m, dict) and m.get("role") in ("user", "assistant")][-30:]
        if not any(m["role"] == "user" for m in msgs):
            s, h, b = json_bytes({"error": "缺少用户消息"}, 400)
            return self._reply(s, h, b)

        model = body.get("model") if body.get("model") in MODELS else "deepseek-v4-flash"
        meta = MODELS[model]
        KEY = load_key(model)
        if not KEY:
            s, h, b = json_bytes({"error": "模型 %s 未配置 API Key：请在服务器 /opt/sxj-chat/%s 写入 Key 后执行 systemctl restart sxj-chat" % (model, meta["key_file"])}, 503)
            return self._reply(s, h, b)

        session = str(body.get("session") or "anon")[:64]
        stream = body.get("stream") is not False
        last_user = next((m["content"] for m in reversed(msgs) if m["role"] == "user"), "")

        sys_content = SYSTEM_PROMPT
        try:
            hits = search_knowledge(last_user)
        except Exception:
            hits = []
        if hits:
            kb = "\n\n".join("[%d]（来源：%s · %s）%s" % (i + 1, c.get("src", ""), c.get("title", ""), c.get("text", "")[:700])
                             for i, c in enumerate(hits))
            sys_content += ("\n\n【事现鉴站内知识检索】以下是 hygzz.cn 站内页面中与用户问题相关的片段。"
                            "回答相关问题时优先依据这些站内内容；未涵盖的部分按你自己的知识回答，并注明可能不确定：\n" + kb)

        payload = json.dumps({
            "model": model,
            "messages": [{"role": "system", "content": sys_content}] + msgs,
            "stream": stream
        }).encode("utf-8")

        req = urllib.request.Request(meta["upstream"], data=payload,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY},
            method="POST")

        try:
            up = urllib.request.urlopen(req, timeout=180)
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", "ignore")[:500]
            except Exception:
                detail = ""
            if e.code == 401:
                msg = "%s API Key 无效或过期，请更新 /opt/sxj-chat/%s" % (meta["vendor"], meta["key_file"])
            elif e.code == 402 or e.code == 429:
                msg = "%s 余额不足或触发限流（HTTP %d）" % (meta["vendor"], e.code)
            else:
                msg = "%s 上游错误 %d" % (meta["vendor"], e.code)
            s, h, b = json_bytes({"error": msg, "detail": detail}, 502)
            return self._reply(s, h, b)
        except Exception:
            s, h, b = json_bytes({"error": "无法连接 %s 上游服务" % meta["vendor"]}, 502)
            return self._reply(s, h, b)

        full_reply = []

        def extract(chunk_text):
            """从 SSE data 行提取 delta.content 累加全文"""
            for line in chunk_text.split("\n"):
                line = line.strip()
                if not line.startswith("data:"):
                    continue
                d = line[5:].strip()
                if d == "[DONE]":
                    continue
                try:
                    j = json.loads(d)
                    c = j.get("choices", [{}])[0].get("delta", {}).get("content")
                    if c:
                        full_reply.append(c)
                except Exception:
                    pass

        if stream:
            self.send_response(up.status)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self._cors()
            self.end_headers()
            tail = ""
            try:
                while True:
                    chunk = up.read(1024)
                    if not chunk:
                        break
                    text = tail + chunk.decode("utf-8", "ignore")
                    lines = text.split("\n")
                    tail = lines.pop()  # 半行留到下一轮
                    extract("\n".join(lines))
                    self.wfile.write(chunk); self.wfile.flush()
                if tail:
                    extract(tail)
            except Exception:
                pass
            up.close()
        else:
            data = up.read()
            try:
                j = json.loads(data.decode("utf-8", "ignore"))
                c = j.get("choices", [{}])[0].get("message", {}).get("content")
                if c:
                    full_reply.append(c)
            except Exception:
                pass
            self.send_response(up.status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self._cors()
            self.end_headers()
            self.wfile.write(data)

        # 异步落库 + 投墙，不阻塞响应
        reply_all = "".join(full_reply)
        def _record():
            save_chat(session, model, last_user, reply_all)
            post_wall(session, model, last_user, reply_all)
        threading.Thread(target=_record, daemon=True).start()

    def log_message(self, fmt, *args):
        pass  # 静默日志

if __name__ == "__main__":
    db_init()
    print("SXJ model proxy v2 listening on 127.0.0.1:%d (knowledge:%d chunks)" % (PORT, len(KNOWLEDGE)), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
