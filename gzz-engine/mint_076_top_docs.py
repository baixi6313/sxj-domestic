# -*- coding: utf-8 -*-
import json, hashlib, shutil, sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "data", "full_ledger.json")
BACKUP = os.path.join(BASE, "data", "full_ledger.backup_before_076_20260830.json")
shutil.copy2(LEDGER, BACKUP)
ledger = json.load(open(LEDGER))
events = ledger["events"]
summary = "hygzz.top部署启动：文档中心docs.html自hygzz.cn同步至腾讯云COS（增量不覆盖首页）"
phase = "OPS"
ts = "20260830224700"
h8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode("utf-8")).hexdigest()[:8]
seq = 76
code = f"Gzz-E-EVENT-DEPLOY-{phase}-{ts}-{seq:03d}-{h8}"
ev = {"code": code, "summary": summary, "phase": phase, "timestamp": ts, "seq": seq, "hash8": h8,
      "target": "hygzztop-1352601878.cos.ap-hongkong（CNAME直连桶）",
      "source_ref": "https://hygzz.cn/docs.html", "sanyuan": {"primary": "技术元", "level": "中", "cross": []}}
events.append(ev)
ledger["meta"]["total"] = len(ledger["chain"]) + len(ledger["entities"]) + len(events)
ledger["meta"]["counts"]["events"] = len(events)
ledger["meta"]["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
json.dump(ledger, open(LEDGER, "w"), ensure_ascii=False)
print(f"[铸码] {code}")
print(f"[账本] 总计 {ledger['meta']['total']}")
from hash_chain import verify_all, format_report
print(format_report(verify_all(ledger)).splitlines()[-2])
