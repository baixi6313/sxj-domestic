import json, hashlib

ts = "20260830234500"
d = json.load(open('data/full_ledger.json'))

codes = [
    {
        "seq": 85, "type": "VERIFY", "phase": "DATA",
        "summary": "南方能源行业可信数据空间运行状态锚定（E1实测data.csg.cn HTTP200+E2多源：上架数据产品342个/累计调用220万+次/生态主体581家/4大业务专区，南网数字301638运营，国家首批可信数据空间试点）",
        "claim": "SXJ-038", "evidence_level": "E1",
        "note": "互动易08-29官方回复+cepca 05-07（328款）+云南电协 08-07（340余款）同一增长曲线；注册通道data.guangzhou.csg.cn:2233/energy（广州数交所审核约3工作日）",
        "sanyuan": {"primary": "产业元", "level": "高", "cross": ["治理元"]}
    },
    {
        "seq": 86, "type": "GZZP", "phase": "ISSUE",
        "summary": "南网第一批数据开放目录=081席位实体池锚定（149项电网数据+8类AI高质量数据集：全社会用电量/分产业用电量/发用电负荷等；禤亮试用机制100+项对应此目录）",
        "claim": "SXJ-038", "evidence_level": "E1",
        "note": "首批升码原料：可从149项目录逐项映射生成VERIFY-DATA子码；60亿条为14家合计预计值，南网可点名实体仅此目录（60亿预计非已开放纪律持续生效）",
        "sanyuan": {"primary": "产业元", "level": "高", "cross": ["治理元"]}
    },
    {
        "seq": 87, "type": "GOVERN", "phase": "POLICY",
        "summary": "欧盟数字电池护照法规锚定（EU 2023/1542第77(1)条：2027-02-18 EV/LMT/>2kWh工业电池强制，QR码+唯一标识无但书；DPP Registry 2026-07-20上线；实施条例2026/1778于08-06生效；官方指南v1.0=71项数据点）",
        "claim": "SXJ-001", "evidence_level": "E1",
        "note": "引用纪律：护照数据点以欧盟委员会2026-07-28指南v1.0=71项为准，媒体通稿90项系早期估算不采信；碳足迹标签生效日存在07-01/08-18两说暂记不确定；2028-02-18碳足迹阈值禁售",
        "sanyuan": {"primary": "治理元", "level": "高", "cross": ["产业元"]}
    },
    {
        "seq": 88, "type": "VERIFY", "phase": "DATA",
        "summary": "中欧可信汽车数据通道锚定（Catena-X×中汽协CAAM×VDA China×众链科技Zhonglian：2026-01电池护照跨境可行性验证→2026-07-29宣布世界首条中欧汽车数据通道→计划2026-11中旬运营；临港全国首例电池护照跨境试点=合规通道样本）",
        "claim": "SXJ-001", "evidence_level": "E1",
        "note": "Zhonglian=Catena-X欧洲外首个运营伙伴；通道使护照一次生成两侧互认（中国数据出境规则+欧盟法规同时满足）；2026-11运营为计划节点，到达时需复核",
        "sanyuan": {"primary": "产业元", "level": "高", "cross": ["治理元", "技术元"]}
    },
    {
        "seq": 89, "type": "DOC", "phase": "CASE",
        "summary": "SXJ-001宁德时代电池护照案例事实更新（宝马MOU 2025-02首签+2026-02深化；GBA两轮试点：神行超充/CTP集成电池独立溯源档案+第三方核验；储能产品获全国锂电池类首张国家级碳足迹标识认证；中国动力电池溯源新规2026-04-01施行：每块电池唯一编码入全国统一溯源平台）",
        "claim": "SXJ-001", "evidence_level": "E1",
        "note": "五源交叉：中国汽车报07-27/OFweek 06-29/上观新闻06-17/新浪财经IIGF 07-21/马拉车市08-14；旧记忆'90项'表述据此更新为官方71项口径",
        "sanyuan": {"primary": "产业元", "level": "高", "cross": ["治理元"]}
    },
    {
        "seq": 90, "type": "GOVERN", "phase": "CHARTER",
        "summary": "三层身份互锚架构确立（中国动力电池溯源平台唯一编码=监管层强制/欧盟DPP Registry护照标识=市场层2027强制/Gzz码=记录层自愿跨主权；护照验证事件铸VERIFY-DATA码，claim对应护照QR标识哈希）",
        "claim": "SXJ-001", "evidence_level": "E2",
        "note": "白玺决策锚：SXJ-001升维路径=事现鉴作为第三方验证记录层嵌入两大体系；近期动作：149项目录首批10项试点升码+13家央企名单巡查升码",
        "sanyuan": {"primary": "治理元", "level": "高", "cross": ["产业元", "技术元"]}
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
