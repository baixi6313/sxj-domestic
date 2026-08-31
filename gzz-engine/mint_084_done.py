import json, hashlib

ts = "20260830233200"
summary = "数据开放月×宁德时代电池护照交叉对比研究完成（5处矛盾点清单+同构矩阵+三层身份互锚方案，报告已归档）"
phase = "DONE"
hash8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode()).hexdigest()[:8]
code = f"Gzz-E-EVENT-RESEARCH-{phase}-{ts}-084-{hash8}"

d = json.load(open('data/full_ledger.json'))
ev = {
    "code": code, "summary": summary, "phase": phase, "timestamp": ts,
    "seq": 84, "hash8": hash8, "type": "RESEARCH",
    "creator": "白玺", "registrar": "砺·事现鉴验证执行官",
    "claim": "SXJ-001（宁德时代电池护照案例）+数据开放月081席位",
    "evidence_level": "E2",
    "note": "产出：数据开放月×宁德时代电池护照_交叉对比研究_20260830.md（七节：中国侧数字时间线/欧盟法规时间线/矛盾点5处/同构矩阵/对接方案/来源清单）；SXJ-001事实更新：2026-01跨境可行性验证、2026-07中欧数据通道宣布、官方指南71项数据点",
    "sanyuan": {"primary": "治理元", "level": "中", "cross": ["产业元"]}
}
d['events'].append(ev)
json.dump(d, open('data/full_ledger.json', 'w'), ensure_ascii=False, indent=1)
print("084:", code)
