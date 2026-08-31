import json, hashlib

ts = "20260830235000"
d = json.load(open('data/full_ledger.json'))

codes = [
    {
        "seq": 91, "type": "VERIFY", "phase": "DATA",
        "summary": "《中国数据产业发展报告(2026)》数据锚定（国家数据发展研究院2026-08-28数博会主论坛发布：2025年数据产业规模6.78万亿元+15.7%/企业48.2万家+17.9%；高质量数据集12.6万个/总数据量1815PB，截至2026-08，较3月+89%）",
        "claim": "SXJ-037", "evidence_level": "E1",
        "note": "国家数据局官网08-28+湖南日报08-30+央视网新闻联播08-30三源交叉；2025产业规模6.78万亿为报告原文口径（'超6万亿'为联播简化口径）",
        "sanyuan": {"primary": "治理元", "level": "中", "cross": ["产业元"]}
    },
    {
        "seq": 92, "type": "GOVERN", "phase": "CHARTER",
        "summary": "国家数据局四项新举措锚定（央视新闻联播2026-08-30：①32城启动新一批数据标注先行先试②探索词元商业模式③14家央国企开放超60亿条④数据领域高技能人才集群培养计划）",
        "claim": "SXJ-037", "evidence_level": "E1",
        "note": "079码已锚定数据开放月倡议，本码补全四举措完整结构；词元商业模式探索与数博会主题'词元——数据要素价值释放新路径'呼应",
        "sanyuan": {"primary": "治理元", "level": "中", "cross": []}
    },
]

for c in codes:
    summary, phase = c["summary"], c["phase"]
    hash8 = hashlib.sha256(f"{summary}|{phase}|{ts}".encode()).hexdigest()[:8]
    ev = {
        "code": f"Gzz-E-EVENT-{c['type']}-{phase}-{ts}-{c['seq']}-{hash8}",
        "summary": summary, "phase": phase, "timestamp": ts,
        "seq": c["seq"], "hash8": hash8, "type": c["type"],
        "creator": "白玺", "registrar": "砺·事现鉴验证执行官",
        "claim": c["claim"], "evidence_level": c["evidence_level"],
        "note": c["note"], "sanyuan": c["sanyuan"],
    }
    d['events'].append(ev)
    print(ev['code'])

json.dump(d, open('data/full_ledger.json', 'w'), ensure_ascii=False, indent=1)
