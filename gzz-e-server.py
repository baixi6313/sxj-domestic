#!/usr/bin/env python3
"""Gzz-E 事件码 API 服务器 - Python http.server + JSON 文件存储"""
import json, os, time, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 8787
DATA_DIR = "/var/www/html/data/gzz-e"
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
EVIDENCE_DIR = os.path.join(DATA_DIR, "evidence")
RULINGS_FILE = os.path.join(DATA_DIR, "rulings.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)
for f, default in [(EVENTS_FILE, "[]"), (RULINGS_FILE, "[]")]:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as fp:
            fp.write(default)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

VALID_TRANSITIONS = {
    "created": ["submitted", "closed"],
    "submitted": ["verifying", "rejected", "closed"],
    "verifying": ["verified", "disputed", "closed"],
    "verified": ["ruling", "closed"],
    "disputed": ["ruling", "closed"],
    "ruling": ["resolved", "closed"],
    "resolved": ["closed"],
    "rejected": ["closed"],
    "closed": [],
}

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, data, status=200):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length > 0 else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/api/events":
            events = load_json(EVENTS_FILE)
            for k in ["category", "subcategory", "status"]:
                if k in qs:
                    events = [e for e in events if e.get(k) == qs[k][0]]
            if "search" in qs:
                s = qs["search"][0].lower()
                events = [e for e in events if s in e.get("code","").lower() or s in e.get("title","").lower() or s in e.get("description","").lower()]
            self._json(events)

        elif m := re.match(r"^/api/events/(.+)$", path):
            code = m.group(1)
            events = load_json(EVENTS_FILE)
            for ev in events:
                if ev["code"] == code:
                    self._json(ev)
                    return
            self._json({"error": f"not found: {code}"}, 404)

        elif path == "/api/evidence":
            event_code = qs.get("eventCode", [None])[0]
            if not event_code:
                self._json([])
                return
            events = load_json(EVENTS_FILE)
            ev = next((e for e in events if e["code"] == event_code), None)
            if not ev:
                self._json([])
                return
            evidences = []
            for eid in ev.get("evidenceIds", []):
                ef = os.path.join(EVIDENCE_DIR, f"{eid}.json")
                if os.path.exists(ef):
                    evidences.append(load_json(ef))
            self._json(evidences)

        elif m := re.match(r"^/api/evidence/(.+)$", path):
            eid = m.group(1)
            ef = os.path.join(EVIDENCE_DIR, f"{eid}.json")
            if os.path.exists(ef):
                self._json(load_json(ef))
            else:
                self._json({"error": "evidence not found"}, 404)

        elif path == "/api/rulings":
            rulings = load_json(RULINGS_FILE)
            event_code = qs.get("eventCode", [None])[0]
            if event_code:
                rulings = [r for r in rulings if r.get("eventCode") == event_code]
            self._json(rulings)

        elif path == "/api/stats":
            events = load_json(EVENTS_FILE)
            rulings = load_json(RULINGS_FILE)
            evidence_count = len([f for f in os.listdir(EVIDENCE_DIR) if f.endswith(".json")])
            self._json({"totalEvents": len(events), "totalRulings": len(rulings), "totalEvidence": evidence_count})

        else:
            self._json({"error": "Not Found", "path": path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._body()

        if path == "/api/events":
            events = load_json(EVENTS_FILE)
            date = datetime.now().strftime("%Y%m%d")
            prefix = f"Gzz-E-{body['category']}-{body['subcategory']}-{date}-"
            seq = sum(1 for e in events if e.get("code","").startswith(prefix)) + 1
            code = f"{prefix}{seq:03d}"
            ev = {
                "code": code, "category": body["category"], "subcategory": body["subcategory"],
                "title": body["title"], "description": body.get("description",""),
                "status": "created", "evidenceLevel": body.get("evidenceLevel","E1"),
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "evidenceIds": [], "rulingIds": []
            }
            events.append(ev)
            save_json(EVENTS_FILE, events)
            self._json(ev, 201)

        elif path == "/api/evidence":
            import uuid
            eid = uuid.uuid4().hex[:12]
            ev = {
                "id": eid, "eventCode": body["eventCode"], "level": body["level"],
                "type": body.get("type",""), "title": body["title"],
                "content": body.get("content",""), "source": body.get("source",""),
                "hash": body.get("hash",""), "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_json(os.path.join(EVIDENCE_DIR, f"{eid}.json"), ev)
            events = load_json(EVENTS_FILE)
            for e in events:
                if e["code"] == body["eventCode"]:
                    e.setdefault("evidenceIds", []).append(eid)
                    e["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_json(EVENTS_FILE, events)
                    break
            self._json(ev, 201)

        elif path == "/api/rulings":
            rulings = load_json(RULINGS_FILE)
            rid = f"R-{len(rulings)+1:03d}"
            ruling = {
                "id": rid, "eventCode": body["eventCode"], "level": body["level"],
                "judge": body.get("judge",""), "decision": body["decision"],
                "reasoning": body.get("reasoning",""),
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            rulings.append(ruling)
            save_json(RULINGS_FILE, rulings)
            events = load_json(EVENTS_FILE)
            for e in events:
                if e["code"] == body["eventCode"]:
                    e.setdefault("rulingIds", []).append(rid)
                    e["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if body["decision"] == "upheld":
                        e["status"] = "resolved"
                    elif body["decision"] == "rejected":
                        e["status"] = "rejected"
                    save_json(EVENTS_FILE, events)
                    break
            self._json(ruling, 201)

        else:
            self._json({"error": "Not Found"}, 404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._body()

        if m := re.match(r"^/api/events/(.+)$", path):
            code = m.group(1)
            events = load_json(EVENTS_FILE)
            for ev in events:
                if ev["code"] == code:
                    if "status" in body:
                        target = body["status"]
                        if target not in VALID_TRANSITIONS.get(ev["status"], []):
                            self._json({"error": f"invalid transition: {ev['status']} -> {target}", "valid": VALID_TRANSITIONS.get(ev['status'],[])}, 400)
                            return
                    ev.update(body)
                    ev["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_json(EVENTS_FILE, events)
                    self._json(ev)
                    return
            self._json({"error": f"not found: {code}"}, 404)
        else:
            self._json({"error": "Not Found"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if m := re.match(r"^/api/events/(.+)$", path):
            code = m.group(1)
            events = load_json(EVENTS_FILE)
            ev = next((e for e in events if e["code"] == code), None)
            if ev:
                for eid in ev.get("evidenceIds", []):
                    ef = os.path.join(EVIDENCE_DIR, f"{eid}.json")
                    if os.path.exists(ef):
                        os.remove(ef)
                events = [e for e in events if e["code"] != code]
                save_json(EVENTS_FILE, events)
            self._json({"deleted": code})

        elif m := re.match(r"^/api/evidence/(.+)$", path):
            eid = m.group(1)
            ef = os.path.join(EVIDENCE_DIR, f"{eid}.json")
            if os.path.exists(ef):
                os.remove(ef)
            self._json({"deleted": eid})
        else:
            self._json({"error": "Not Found"}, 404)

    def log_message(self, format, *args):
        pass  # 静默日志

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Gzz-E server running on port {PORT}")
    server.serve_forever()