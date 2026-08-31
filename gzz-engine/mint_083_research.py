import json, hashlib

ts = "20260830232600"
summary = "数据开放月×宁德时代电池护照案例交叉对比研究启动（SXJ-001联动，中国可信数据空间vs欧盟Catena-X双体系对比，E2多源+E1实测data.csg.cn）"
phase = "CROSS"
hash8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode()).hexdigest()[:8]
code = f"Gzz-E-EVENT-RESEARCH-{phase}-{ts}-083-{hash8}"

d = json.load(open('data/full_ledger.json'))
ev = {
    "code": code, "summary": summary, "phase": phase, "timestamp": ts,
    "seq": 83, "hash8": hash8, "type": "RESEARCH",
    "creator": "白玺", "registrar": "砺·事现鉴验证执行官",
    "claim": "SXJ-001（宁德时代电池护照案例）+数据开放月081席位",
    "evidence_level": "E2",
    "note": "研究任务：数据开放月多源数据交叉对比+宁德时代电池护照案例合并分析；实测E1：data.csg.cn HTTP 200；完成码随报告铸",
    "sanyuan": {"primary": "治理元", "level": "中", "cross": ["产业元"]}
}
d['events'].append(ev)
json.dump(d, open('data/full_ledger.json', 'w'), ensure_ascii=False, indent=1)
print("083:", code)
