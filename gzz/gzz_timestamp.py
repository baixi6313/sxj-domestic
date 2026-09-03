#!/usr/bin/env python3
"""
Gzz 可信时间戳编码引擎 v2.1
三项锚定哈希：内容 + 事件时间 + 前链哈希
v2.0 五元锚定已废弃（鸡生蛋问题：claim_id 和 _received_at 在 POST 后才生成）
"""

import hashlib
from datetime import timezone, timedelta

CST = timezone(timedelta(hours=8))


# ===== v2.1 三项锚定（当前方案）=====

def gzz_hash(content: str, event_time: str, prev_hash: str) -> str:
    """三项锚定哈希，SHA256 前8位"""
    seed = f"{content}|{event_time}|{prev_hash}"
    return hashlib.sha256(seed.encode()).hexdigest()[:8]


def encode_event(category: str, subcategory: str, seq: str,
                 event_time: str, prev_hash: str,
                 content: str) -> str:
    """
    生成三项锚定 Gzz 事件编码
    格式: Gzz-E-{CAT}-{SUB}-{YYYYMMDDHHMMSS}-{NNN}-{HASH8}
    """
    h = gzz_hash(content, event_time, prev_hash)
    return f"Gzz-E-{category}-{subcategory}-{event_time}-{seq}-{h}"


def verify_encoding(code: str, content: str, event_time: str,
                    prev_hash: str) -> dict:
    """独立验证三项锚定编码完整性"""
    parts = code.split("-")
    if len(parts) < 7:
        return {"valid": False, "error": "格式不完整"}

    claimed_hash = parts[6]
    computed = gzz_hash(content, event_time, prev_hash)

    return {
        "valid": claimed_hash == computed,
        "code": code,
        "event_time": f"{event_time[:4]}-{event_time[4:6]}-{event_time[6:8]} {event_time[8:10]}:{event_time[10:12]}:{event_time[12:14]}",
        "prev_hash": prev_hash,
        "claimed_hash": claimed_hash,
        "computed_hash": computed,
        "hash_matches": claimed_hash == computed,
    }


# ===== v2.0 五元锚定（已废弃，仅保留用于历史验证）=====

def gzz_hash_v2_deprecated(content: str, event_time: str, posting_time: str,
                           claim_id: str, prev_hash: str) -> str:
    """【已废弃】五元锚定哈希"""
    seed = f"{content}|{event_time}|{posting_time}|{claim_id}|{prev_hash}"
    return hashlib.sha256(seed.encode()).hexdigest()[:8]


# ===== v1 两项锚定（已废弃，仅保留用于历史验证）=====

def gzz_hash_v1_deprecated(content: str, event_time: str) -> str:
    """【已废弃】两项锚定哈希"""
    seed = f"{content}|{event_time}"
    return hashlib.sha256(seed.encode()).hexdigest()[:8]


# ===== 实例：Kimi 事件 v7（三项锚定）=====

KIMI_CONTENT_V7 = "Kimi 盘域扫描报告。三步验证：步骤1公示墙✅ 步骤2 Logo❌ 步骤3交叉验证⚠️。发现 hygzz.com Worker坏、limit=100陷阱、icons缺6个。回贴 msg_00bff050e2e8。事件时间 20260823132700 CST。"
KIMI_EVENT_TIME = "20260823132700"
KIMI_PREV_HASH = "c3a4aedb"  # ← msg_1fb05b597759 v1

if __name__ == "__main__":
    print("=" * 60)
    print("Gzz 可信时间戳编码引擎 v2.1 — 三项锚定")
    print("=" * 60)

    # v7 编码
    code_v7 = encode_event("EVENT", "VERIFY", "003",
                           KIMI_EVENT_TIME, KIMI_PREV_HASH,
                           KIMI_CONTENT_V7)
    print(f"v7 编码: {code_v7}")

    result = verify_encoding(code_v7, KIMI_CONTENT_V7,
                             KIMI_EVENT_TIME, KIMI_PREV_HASH)
    print(f"验证: {'✅ 通过' if result['valid'] else '❌ 失败'}")
    print(f"  声称哈希: {result['claimed_hash']}")
    print(f"  计算哈希: {result['computed_hash']}")
    print()

    # 三项锚点
    print("三项锚点:")
    print(f"  内容:      {KIMI_CONTENT_V7[:50]}...")
    print(f"  事件时间:  {result['event_time']} CST")
    print(f"  前链哈希:  {KIMI_PREV_HASH} ← msg_1fb05b597759 (v1)")
    print()

    # 篡改检测
    print("篡改检测:")
    tests = [
        ("改事件时间", KIMI_CONTENT_V7, "20260823140000", KIMI_PREV_HASH),
        ("改前链哈希", KIMI_CONTENT_V7, KIMI_EVENT_TIME, "ffffffff"),
        ("改内容", "篡改后的内容", KIMI_EVENT_TIME, KIMI_PREV_HASH),
    ]
    for label, c, t, p in tests:
        v = verify_encoding(code_v7, c, t, p)
        print(f"  {label}: {'❌ 检出' if not v['valid'] else '⚠️ 未检出'}")

    print()
    print("版本历史:")
    print("  v1: 两项 SHA256(内容+时间)[:8] → c3a4aedb (msg_1fb05b597759)")
    print("  v2: 五项（参数错误）→ d63ac8b3 (msg_f2c746091c79) ❌废弃")
    print("  v3-v6: 废弃")
    print("  v7: 三项 SHA256(内容+时间+前链)[:8] → 0194e767 (msg_91b8ad878b23) ✅")