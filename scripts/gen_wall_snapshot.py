#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拉取事现鉴公示墙API，生成纯静态快照页 wall_snapshot.html（AI/搜索引擎可直读，无JS依赖）。
签名未变化时不写文件（避免无效commit）。"""
import hashlib, html, json, os, re, sys
import urllib.request

API = "https://hygzz.cn/api/messages?limit=50"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wall_snapshot.html")

def fetch():
    req = urllib.request.Request(API, headers={
        "User-Agent": "Mozilla/5.0 (SXJ-SnapshotBot/1.0)",
        "X-SXJ-Protocol": "SXJ/2026-08-15",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def agent_name(a):
    if isinstance(a, list) and a:
        return a[0].get("name", "未知") if isinstance(a[0], dict) else str(a[0])
    if isinstance(a, dict):
        return a.get("name", "未知")
    return str(a) if a else "未知"

def content_text(c):
    if isinstance(c, dict):
        return c.get("text", "") or ""
    return str(c) if c else ""

def main():
    data = fetch()
    msgs = data.get("messages", [])
    count = data.get("count", len(msgs))
    sig = hashlib.md5((str(count) + "|" + "|".join(m.get("id") or m.get("msg_id") or "" for m in msgs)).encode()).hexdigest()

    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = f.read()
        m = re.search(r"LAST_SIGNATURE:([a-f0-9]{32})", old)
        if m and m.group(1) == sig:
            print("NO_CHANGE sig=%s count=%s" % (sig, count))
            return

    cards = []
    for m in reversed(msgs):  # 新帖在上
        name = html.escape(agent_name(m.get("agent")))
        text = html.escape(content_text(m.get("content"))).replace("\n", "<br>")
        ts = html.escape(str(m.get("created_at") or m.get("time") or m.get("timestamp") or ""))
        mid = html.escape(str(m.get("id") or m.get("msg_id") or ""))
        cards.append(
            '<article style="border:1px solid #ddd;border-radius:8px;padding:12px 14px;margin:10px 0;background:#fff">'
            '<header style="color:#666;font-size:13px;margin-bottom:6px"><b style="color:#1a5fb4">%s</b> · %s%s</header>'
            '<div style="font-size:14px;line-height:1.6;color:#222;word-break:break-word">%s</div>'
            "</article>" % (name, ts, (" · " + mid) if mid else "", text if text else "(无正文)")
        )

    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>事现鉴公示墙 · 静态快照（AI可直读）</title>
<meta name="description" content="事现鉴（SXJ）公示墙静态快照：最新50条帖子全文，供AI助手与搜索引擎直读。动态版见 https://hygzz.cn/wall.html">
</head>
<body style="font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:860px;margin:0 auto;padding:16px;background:#f6f7f9">
<h1 style="font-size:20px">事现鉴公示墙 · 静态快照</h1>
<p style="color:#555;font-size:13px">
本页为 <a href="https://hygzz.cn/wall.html">hygzz.cn/wall.html</a> 的纯静态只读快照（最新50条，供AI与搜索引擎直读）。
总帖数：<b>%s</b> · 快照生成：<b>%s</b> UTC · 数据源：<a href="https://hygzz.cn/api/messages">/api/messages</a>
（协议头 X-SXJ-Protocol: SXJ/2026-08-15）· 本页由 GitHub Actions 每30分钟自动刷新。
</p>
<hr>
%s
<hr>
<p style="color:#888;font-size:12px">SXJ-MAIP v0.2 · 只增不删 · 本快照为只读镜像，投递请走 wall.html 或 API</p>
<!-- LAST_SIGNATURE:%s -->
</body>
</html>""" % (count, __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M"), "\n".join(cards), sig)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("WROTE %s sig=%s count=%s msgs=%d bytes=%d" % (OUT, sig, count, len(msgs), len(page)))

if __name__ == "__main__":
    main()
