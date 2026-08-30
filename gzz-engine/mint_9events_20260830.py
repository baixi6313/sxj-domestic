# -*- coding: utf-8 -*-
"""
Gzz 事件存根批量铸码 — 2026-08-30 九事件
公式: hash8 = sha256(f"{summary}|{phase}|{ts}")[:8]  (与 hash_chain.py event_hash8 一致)
账本: data/full_ledger.json events 数据集, seq 从 053 接续
写前自动备份, 写后跑全量验证
"""
import json, hashlib, shutil, os, sys
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "data", "full_ledger.json")
BACKUP = os.path.join(BASE, "data", "full_ledger.backup_before_9events_20260830.json")

# 1. 备份（只增不删）
shutil.copy2(LEDGER, BACKUP)
print(f"[备份] {BACKUP}")

# 2. 九条事件定义 (summary, phase, timestamp, subtype, doc_type, source_ref, sanyuan_primary, sanyuan_level)
EV = [
    ("SXJ模型v2四模型上线（快速/深度/均衡/强力+对话留存+公示墙投递+站内RAG）", "OCC", "20260830095700", "DEPLOY", "部署", "sxj_v2_deploy_20260830", "技术元", "上"),
    ("hygzz.cn站内AI对话上线（chat.html+Nginx反代+sxj-chat服务+DeepSeek）", "OCC", "20260830030000", "DEPLOY", "部署", "hygzz_chat_online_20260830", "技术元", "上"),
    ("邮箱验证码登录系统上线（SMTP+nginx四路由+auth_server 8813全链路公网验证通过）", "OCC", "20260830130300", "DEPLOY", "部署", "auth_deploy_20260830", "技术元", "中"),
    ("OrcaRouter商务邮件查证完成（Continuum AI平台真实但群发推广，决议暂不接入生产）", "VER", "20260830132300", "COMP", "查证报告", "orcarouter_verify_20260830", "人文元", "中"),
    ("腾讯云全账户成本盘点完成（25项1261.69元，识别DDoS/SCF/南京CVM三大漏损）", "VER", "20260830133500", "AUDIT", "盘点报告", "tencent_cloud_audit_20260830", "金融元", "中"),
    ("砺8月工作日记归档（四主线+运维教训+9月交接，B盘+云端双份）", "REC", "20260830132300", "ARCHIVE", "日记", "li_work_diary_202608", "人文元", "中"),
    ("事现鉴安全审查报告归档（豆包MAIP验证Agent产线，P0四项整改清单确立）", "REC", "20260830182000", "SEC", "审查报告", "sxj_sec_review_20260830", "技术元", "上"),
    ("统一门户基础盘点确认（WorkBuddy unified-site地基+196条术语哈希链核验，待部署四站）", "VER", "20260830181800", "UNIFIED", "盘点报告", "unified_site_stage", "技术元", "中"),
    ("事现鉴定位与双段部署文档归档（免税区框架+四域两段架构+G-9断点记录）", "REC", "20260830181900", "ARCHIVE", "架构文档", "sxj_positioning_20260813", "技术元", "中"),
]

def event_hash8(summary, phase, ts):
    return hashlib.sha256(f"{summary}|{phase}|{ts}".encode("utf-8")).hexdigest()[:8]

# 3. 读账本
ledger = json.load(open(LEDGER, encoding="utf-8"))
events = ledger["events"]
start_seq = max(e["seq"] for e in events) + 1  # 53
print(f"[接续] 现有 events {len(events)} 条, 新码从 seq {start_seq:03d} 开始")

# 4. 铸码
new_items = []
for i, (summary, phase, ts, sub, doc_type, ref, sy_p, sy_l) in enumerate(EV):
    seq = start_seq + i
    h8 = event_hash8(summary, phase, ts)
    code = f"Gzz-E-EVENT-{sub}-{phase}-{ts}-{seq:03d}-{h8}"
    item = {
        "code": code, "summary": summary, "phase": phase, "timestamp": ts,
        "seq": seq, "hash8": h8, "doc_type": doc_type, "source_ref": ref,
        "sanyuan": {"primary": sy_p, "level": sy_l, "cross": []}
    }
    new_items.append(item)
    print(f"  {code}")

# 5. 幂等保护: 已存在则跳过
exist = {e["code"] for e in events}
add = [x for x in new_items if x["code"] not in exist]
events.extend(add)

# 6. meta 更新
ledger["meta"]["total"] = len(ledger["chain"]) + len(ledger["entities"]) + len(events)
ledger["meta"]["counts"]["events"] = len(events)
ledger["meta"]["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")

json.dump(ledger, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"[写入] 新增 {len(add)} 条, events 总数 {len(events)}, 账本总计 {ledger['meta']['total']}")

# 7. 全量验证（复用 hash_chain）
sys.path.insert(0, BASE)
from hash_chain import verify_all, format_report
print()
print(format_report(verify_all(ledger)))
