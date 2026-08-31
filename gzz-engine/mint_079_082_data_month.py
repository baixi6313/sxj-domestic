# -*- coding: utf-8 -*-
import json, hashlib, shutil, sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "data", "full_ledger.json")
BACKUP = os.path.join(BASE, "data", "full_ledger.backup_before_079_20260830.json")
shutil.copy2(LEDGER, BACKUP)
ledger = json.load(open(LEDGER))
events = ledger["events"]

def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()

c37 = "国家数据局'数据开放月'倡议E1锚定：14家央国企发起国内首个数据开放月，超500项数据资源，预计超60亿条，覆盖电力、油气管网、物流、汽车、农机等十余个行业；可信数据空间提供安全可控流通环境（2026-08-29，贵阳数博会；央视网新闻联播08-30/央视财经08-29交叉核验）"
c38 = "南方电网'数据试用'机制执行E1锚定：首次推出数据试用机制，开放电网运行、新能源消纳、设备运行等100多项数据，让发电企业、科研院所等需求方零门槛试用、验证数据的价值、用得好再谈合作（禤亮，南方电网数字化部副总经理，2026-08-29，央视逐字引用）"
c39 = "白玺观测者宣言：我在上面，我站得高，看得远，我一观察底下（2026-08-30，录音转写，L0真相源归档）"
c33 = "14家央国企数据开放月责任席位派单：逐一映射各家开放数据资源清单生成VERIFY-DATA子事件码（当前仅南网100+项已公布清单，其余13家待细则后升E1）"

specs = [
    (79, "GOVERN", "CHARTER", "20260830231000", "国家数据局'数据开放月'倡议锚定（2026数博会，E1）",
     {"claim": "SXJ-037", "claim_sha256": sha(c37), "evidence_level": "E1",
      "sources": ["央视网新闻联播 https://news.cctv.com/2026/08/30/ARTICjakAuYbdNykcxb4BqSy260830.shtml",
                  "央视财经 https://m.toutiao.com/group/7679431618066383423/"],
      "discipline": "60亿条为预计目标非已开放量；只锚定已发生事实"}),
    (80, "VERIFY", "DATA", "20260830231000", "南方电网'数据试用'机制执行锚定（E1）",
     {"claim": "SXJ-038", "claim_sha256": sha(c38), "evidence_level": "E1",
      "sources": ["央视视频逐字引用 https://content-static.cctvnews.cctv.com/snow-book/index.html?item_id=1355063001841650897"],
      "parent": "079"}),
    (81, "GZZP", "ISSUE", "20260830231000", "14家央国企'数据开放月'责任席位派单（E2待细则）",
     {"claim": "SXJ-034映射", "claim_sha256": sha(c33), "evidence_level": "E2",
      "note": "仅南网清单已公布；其余13家待国家数据局细则后逐家生成VERIFY-DATA子码并升E1",
      "parent": "079"}),
    (82, "GOVERN", "CHARTER", "20260830231000", "白玺观测者宣言（E1，观测者层级锚定）",
     {"claim": "SXJ-039", "claim_sha256": sha(c39), "evidence_level": "E1",
      "note": "录音转写已归档L0真相源；终裁权白玺R-5"}),
]

ts_base = "20260830231000"
for seq, typ, ph, ts, summ, extra in specs:
    h8 = hashlib.sha256(f"{summ}|{ph}|{ts}".encode("utf-8")).hexdigest()[:8]
    code = f"Gzz-E-EVENT-{typ}-{ph}-{ts}-{seq:03d}-{h8}"
    ev = {"code": code, "summary": summ, "phase": ph, "timestamp": ts, "seq": seq, "hash8": h8,
          "type": typ, "creator": "白玺", "registrar": "砺·事现鉴验证执行官", **extra,
          "sanyuan": {"primary": "治理元" if typ == "GOVERN" else "数据元", "level": "高", "cross": []}}
    events.append(ev)
    print(f"[{seq:03d}] {code}")

ledger["meta"]["total"] = len(ledger["chain"]) + len(ledger["entities"]) + len(events)
ledger["meta"]["counts"]["events"] = len(events)
ledger["meta"]["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
json.dump(ledger, open(LEDGER, "w"), ensure_ascii=False)
print(f"[账本] 总计 {ledger['meta']['total']}")
from hash_chain import verify_all, format_report
print(format_report(verify_all(ledger)).splitlines()[-2])
