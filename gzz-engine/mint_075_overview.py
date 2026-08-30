# -*- coding: utf-8 -*-
# 075: 事现鉴部署总览文档（2026-08-30）
import json, hashlib, shutil, sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "data", "full_ledger.json")
BACKUP = os.path.join(BASE, "data", "full_ledger.backup_before_075_20260830.json")
shutil.copy2(LEDGER, BACKUP)
ledger = json.load(open(LEDGER))
events = ledger["events"]
summary = "事现鉴部署总览文档生成（定位:公共免责可验证区域；四域E1实测数据；今日工作062-074全记录）"
phase = "DOC"
ts = "20260830224300"
h8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode("utf-8")).hexdigest()[:8]
seq = 75
code = f"Gzz-E-EVENT-DOC-{phase}-{ts}-{seq:03d}-{h8}"
ev = {"code": code, "summary": summary, "phase": phase, "timestamp": ts, "seq": seq, "hash8": h8,
      "doc_type": "总览文档", "source_ref": "事现鉴部署总览_20260830.md; 数据源:E1实测+账本1691条",
      "sanyuan": {"primary": "技术元", "level": "中", "cross": []}}
events.append(ev)
ledger["meta"]["total"] = len(ledger["chain"]) + len(ledger["entities"]) + len(events)
ledger["meta"]["counts"]["events"] = len(events)
ledger["meta"]["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
json.dump(ledger, open(LEDGER, "w"), ensure_ascii=False)
print(f"[铸码] {code}")
print(f"[写入] events {len(events)}, 账本总计 {ledger['meta']['total']}")
from hash_chain import verify_all, format_report
print(format_report(verify_all(ledger)))
