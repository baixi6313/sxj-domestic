"""
Gzz 哈希链验证层
事现鉴 SXJ 编码体系 —— 四套哈希公式与全量账本验证

公式依据: Gzz引擎哈希公式破解报告_20260829.md（964 条全量链 100% 破解）
  - v1 链(index 1-196)   : hash8 = sha256(f"{term}|{definition}|{event_date}|{prev_hash}")[:8]
  - v2/v3 链(index 197+) : hash8 = sha256(f"{term}|{timestamp}|{prev_hash}")[:8]
  - 独立实体码            : hash8 = sha256(f"{name}|{country}|{cat}")[:8]
  - 独立事件码            : hash8 = sha256(f"{summary}|{phase}|{ts}")[:8]

已知例外: index 112「三元光锥时空」的 definition 不在 v1_items.json 中（脚本
快照晚于编码时被修改），验证时该条跳过，允许 963/964 通过。
"""

import hashlib
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

LEDGER_PATH = os.path.join(DATA_DIR, "full_ledger.json")
V1_ITEMS_PATH = os.path.join(DATA_DIR, "v1_items.json")

GENESIS_PREV = "7d9387a7"   # 创世 prev_hash
V1_LAST_INDEX = 196         # v1 链最后一节的 index


# ============================================================
# 四套哈希公式
# ============================================================

def v1_hash8(term: str, definition: str, event_date: str, prev_hash: str) -> str:
    """v1 链词条哈希: sha256(term|definition|event_date|prev_hash)[:8]"""
    raw = f"{term}|{definition}|{event_date}|{prev_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]


def v2_hash8(term: str, timestamp: str, prev_hash: str) -> str:
    """v2/v3 链词条哈希: sha256(term|timestamp|prev_hash)[:8]"""
    raw = f"{term}|{timestamp}|{prev_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]


def entity_hash8(name: str, country: str, cat: str) -> str:
    """独立实体注册表哈希: sha256(name|country|cat)[:8]"""
    raw = f"{name}|{country}|{cat}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]


def event_hash8(summary: str, phase: str, ts: str) -> str:
    """独立事件存根哈希: sha256(summary|phase|ts)[:8]"""
    raw = f"{summary}|{phase}|{ts}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]


def extract_timestamp(code: str) -> str:
    """从 Gzz 编码中提取 14 位时间戳段（如 20260827005200）"""
    m = re.search(r"(\d{14})", code or "")
    return m.group(1) if m else ""


# ============================================================
# 数据加载（自包含：全部从 data/ 目录读取）
# ============================================================

def load_ledger(path: str = None) -> dict:
    """加载全量账本 full_ledger.json"""
    path = path or LEDGER_PATH
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_v1_items(path: str = None) -> dict:
    """加载 v1 四元组列表，返回 term -> item 映射"""
    path = path or V1_ITEMS_PATH
    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    return {it["term"]: it for it in items}


# ============================================================
# 验证
# ============================================================

def verify_chain(chain: list, v1_items: dict = None) -> dict:
    """
    对全量链逐条复算 current_hash。
    - index 1-196 (v1): 按 term 在 v1_items 中取 definition/event_date 复算；
      term 不在表中则记为跳过（当前仅 index 112）。
    - index 197+ (v2/v3): 从 code 提取 14 位时间戳复算。
    同时校验 prev_hash 连续性（断链检测）。
    """
    if v1_items is None:
        v1_items = load_v1_items()

    matched = failed = skipped = breaks = 0
    failed_index, skipped_index, break_index = [], [], []

    for i, e in enumerate(chain):
        idx = e.get("index", i + 1)
        prev = e.get("prev_hash", "")

        # prev_hash 连续性（第 1 条 prev 应为创世值）
        if i == 0:
            if prev != GENESIS_PREV:
                breaks += 1
                break_index.append(idx)
        elif prev != chain[i - 1].get("current_hash"):
            breaks += 1
            break_index.append(idx)

        if idx <= V1_LAST_INDEX:
            item = v1_items.get(e.get("term", ""))
            if item is None:
                skipped += 1
                skipped_index.append(idx)
                continue
            expect = v1_hash8(e["term"], item["definition"], item["event_date"], prev)
        else:
            expect = v2_hash8(e["term"], extract_timestamp(e.get("code", "")), prev)

        if expect == e.get("current_hash"):
            matched += 1
        else:
            failed += 1
            failed_index.append(idx)

    return {
        "total": len(chain),
        "matched": matched,
        "failed": failed,
        "failed_index": failed_index,
        "skipped": skipped,
        "skipped_index": skipped_index,
        "breaks": breaks,
        "break_index": break_index,
        "chain_tail": chain[-1].get("current_hash", "") if chain else "",
    }


def verify_entities(entities: list) -> dict:
    """对独立实体注册表逐条复算 hash8"""
    matched = failed = 0
    failed_codes = []
    for e in entities:
        expect = entity_hash8(e["name"], e["country"], e["category"])
        if expect == e.get("hash8"):
            matched += 1
        else:
            failed += 1
            failed_codes.append(e.get("code", "?"))
    return {"total": len(entities), "matched": matched,
            "failed": failed, "failed_codes": failed_codes}


def verify_events(events: list) -> dict:
    """对独立事件存根逐条复算 hash8"""
    matched = failed = 0
    failed_codes = []
    for e in events:
        expect = event_hash8(e["summary"], e["phase"], e["timestamp"])
        if expect == e.get("hash8"):
            matched += 1
        else:
            failed += 1
            failed_codes.append(e.get("code", "?"))
    return {"total": len(events), "matched": matched,
            "failed": failed, "failed_codes": failed_codes}


def verify_all(ledger: dict = None) -> dict:
    """验证全量账本（chain + entities + events），返回汇总统计"""
    ledger = ledger or load_ledger()
    chain = ledger.get("chain", [])
    entities = ledger.get("entities", [])
    events = ledger.get("events", [])

    s_chain = verify_chain(chain)
    s_ent = verify_entities(entities)
    s_evt = verify_events(events)

    return {
        "meta": ledger.get("meta", {}),
        "chain": s_chain,
        "entities": s_ent,
        "events": s_evt,
        "grand_total": len(chain) + len(entities) + len(events),
        "grand_matched": s_chain["matched"] + s_ent["matched"] + s_evt["matched"],
        "grand_failed": s_chain["failed"] + s_ent["failed"] + s_evt["failed"],
        "grand_skipped": s_chain["skipped"],
    }


def format_report(stats: dict) -> str:
    """把 verify_all 的统计格式化为可打印报告"""
    c, en, ev = stats["chain"], stats["entities"], stats["events"]
    lines = []
    lines.append("=" * 56)
    lines.append("Gzz 全量账本哈希验证报告")
    lines.append("=" * 56)
    m = stats.get("meta") or {}
    if m:
        lines.append(f"账本 meta    : total={m.get('total')}  chain_tail={m.get('chain_tail')}"
                     f"  generated_at={m.get('generated_at')}")
    lines.append(f"链 chain     : {c['total']} 条 | 复算通过 {c['matched']}"
                 f" | 跳过 {c['skipped']} {c['skipped_index']}"
                 f" | 失败 {c['failed']} {c['failed_index']}")
    lines.append(f"             | 断链 {c['breaks']} {c['break_index']} | 链尾 {c['chain_tail']}")
    lines.append(f"实体 entities: {en['total']} 条 | 通过 {en['matched']} | 失败 {en['failed']}"
                 + (f" {en['failed_codes'][:5]}" if en["failed"] else ""))
    lines.append(f"事件 events  : {ev['total']} 条 | 通过 {ev['matched']} | 失败 {ev['failed']}"
                 + (f" {ev['failed_codes'][:5]}" if ev["failed"] else ""))
    lines.append("-" * 56)
    ok = stats["grand_failed"] == 0 and c["breaks"] == 0
    verdict = "PASS ✅" if ok else "FAIL ❌"
    lines.append(f"总计 {stats['grand_total']} 条 | 通过 {stats['grand_matched']}"
                 f" | 跳过 {stats['grand_skipped']} | 失败 {stats['grand_failed']} → {verdict}")
    return "\n".join(lines)


# ============================================================
# 自测入口
# ============================================================

if __name__ == "__main__":
    print(format_report(verify_all()))
