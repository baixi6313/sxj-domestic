# -*- coding: utf-8 -*-
# 074: hygzz.cn源站同步完成（2026-08-30）
import json, hashlib, shutil, sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "data", "full_ledger.json")
BACKUP = os.path.join(BASE, "data", "full_ledger.backup_before_074_20260830.json")
shutil.copy2(LEDGER, BACKUP)
ledger = json.load(open(LEDGER))
events = ledger["events"]

summary = "hygzz.cn源站同步完成（7/7文件上线：wall.html1071条快照/timeline/portal统一门户/relay×4；E1外部实测全200；主页sxj-chat与API未动）"
phase = "OPS"
ts = "20260830223800"
h8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode("utf-8")).hexdigest()[:8]
seq = 74
code = f"Gzz-E-EVENT-SYNC-{phase}-{ts}-{seq:03d}-{h8}"
ev = {
    "code": code, "summary": summary, "phase": phase, "timestamp": ts, "seq": seq, "hash8": h8,
    "doc_type": "站点运维",
    "source_ref": "hygzz.cn(Lighthouse lhins-oc9amaq1); 方案C·OrcaTerm单命令; COS镜像源hygzzcn-1352601878",
    "sanyuan": {"primary": "技术元", "level": "中", "cross": []},
}
events.append(ev)
ledger["meta"]["total"] = len(ledger["chain"]) + len(ledger["entities"]) + len(events)
ledger["meta"]["counts"]["events"] = len(events)
ledger["meta"]["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
json.dump(ledger, open(LEDGER, "w"), ensure_ascii=False)
print(f"[铸码] {code}")
print(f"[写入] events {len(events)}, 账本总计 {ledger['meta']['total']}")
from hash_chain import verify_all, format_report
print(format_report(verify_all(ledger)))
