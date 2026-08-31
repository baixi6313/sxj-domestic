# -*- coding: utf-8 -*-
# 062: 九事件批次公示投递完成事件（2026-08-30）
import json, hashlib, shutil, sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "data", "full_ledger.json")
BACKUP = os.path.join(BASE, "data", "full_ledger.backup_before_062_20260830.json")

shutil.copy2(LEDGER, BACKUP)
ledger = json.load(open(LEDGER))
events = ledger["events"]

CLAIMS = ("msg_805002349011,msg_9f6a9768a715,msg_8c94b68969e9,msg_7a18da116ba6,"
          "msg_ae0697cf4980,msg_905e795dd9f0,msg_fbbcff417391,msg_41575178a06e,msg_a7c05af3df1c")

summary = "九事件批次公示投递完成（seq053-061上墙hygzz.cn公示墙，9/9成功）"
phase = "OCC"
ts = "20260830183900"
h8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode("utf-8")).hexdigest()[:8]
seq = 62
code = f"Gzz-E-EVENT-WALL-{phase}-{ts}-{seq:03d}-{h8}"

ev = {
    "code": code,
    "summary": summary,
    "phase": phase,
    "timestamp": ts,
    "seq": seq,
    "hash8": h8,
    "doc_type": "公示投递",
    "source_ref": f"hygzz.cn/api/leave-message; claims:{CLAIMS}",
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
