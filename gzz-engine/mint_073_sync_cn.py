# -*- coding: utf-8 -*-
# 073: hygzz.cn源站同步启动（2026-08-30）
import json, hashlib, shutil, sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "data", "full_ledger.json")
BACKUP = os.path.join(BASE, "data", "full_ledger.backup_before_073_20260830.json")

shutil.copy2(LEDGER, BACKUP)
ledger = json.load(open(LEDGER))
events = ledger["events"]

summary = "hygzz.cn源站同步启动（主人授权'同步.cn'；补齐wall/timeline/relay缺失页，API不动，主页保留sxj-chat）"
phase = "OPS"
ts = "20260830221500"
h8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode("utf-8")).hexdigest()[:8]
seq = 73
code = f"Gzz-E-EVENT-SYNC-{phase}-{ts}-{seq:03d}-{h8}"

ev = {
    "code": code,
    "summary": summary,
    "phase": phase,
    "timestamp": ts,
    "seq": seq,
    "hash8": h8,
    "doc_type": "站点运维",
    "source_ref": "hygzz.cn(Lighthouse VM-0-15 43.131.35.57); 授权:主人202608302208",
    "sanyuan": {"primary": "技术元", "level": "中", "cross": []},
}
events.append(ev)

ledger["meta"]["total"] = len(ledger["chain"]) + len(ledger["entities"]) + len(events)
ledger["meta"]["counts"]["events"] = len(events)
ledger["meta"]["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")

json.dump(ledger, open(LEDGER, "w"), ensure_ascii=False)
print(f"[铸码] {code}")
print(f"[写入] events 总数 {len(events)}, 账本总计 {ledger['meta']['total']}")

from hash_chain import verify_all, format_report
print(format_report(verify_all(ledger)))
