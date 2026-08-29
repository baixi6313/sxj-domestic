"""
Gzz 编码引擎核心
事现鉴 SXJ 编码体系 v1.0
规则依据: Gzz编码体系参考_最终版_20260822.md
"""

import re
from datetime import datetime

# ============================================================
# 编码规则常量
# ============================================================

# Gzz-E 事件大类 → 子类映射
E_CATEGORIES = {
    "VERIFY":  ["FIN", "COMP", "DATA"],
    "AUDIT":   ["SEC", "LEDGER", "PROTO"],
    "GOVERN":  ["CHARTER", "VOTE", "DISPUTE", "CARBON"],
    "GZZP":    ["ISSUE", "ANCHOR", "RELIEF"],
}

# 统一码已分配序列（AI 建制顺序 + 白玺）
UNIFIED_REGISTRY = {
    "白玺":       "001",
    "DeepSeek":  "002",
    "元宝":       "003",
    "豆包":       "004",
    "千问":       "005",
    "Kimi":       "006",
    "百度搭子":   "007",
    "WorkBuddy": "008",
    "砺":         "009",
}

# 国家码映射（常见）
COUNTRY_CODES = {
    "中国": "CN", "美国": "US", "日本": "JP", "韩国": "KR",
    "德国": "DE", "法国": "FR", "英国": "GB", "新加坡": "SG",
    "加拿大": "CA", "澳大利亚": "AU", "印度": "IN", "巴西": "BR",
    "俄罗斯": "RU", "南非": "ZA", "全球": "全球",
    "CN": "CN", "US": "US", "JP": "JP", "KR": "KR",
    "DE": "DE", "FR": "FR", "GB": "GB", "SG": "SG",
    "CA": "CA", "AU": "AU", "IN": "IN", "BR": "BR",
    "RU": "RU", "ZA": "ZA",
}

# 出生地默认值：不明 → SXJ-全球
DEFAULT_BIRTH = "SXJ"
DEFAULT_GLOBAL = "全球"


def normalize_country(raw: str) -> str:
    """标准化国家码"""
    return COUNTRY_CODES.get(raw, raw.upper() if len(raw) <= 3 else raw)


def format_date(d: str) -> str:
    """统一日期格式 → YYYYMMDD"""
    d = d.strip().replace("-", "").replace("/", "").replace(".", "")
    if len(d) == 8:
        return d
    raise ValueError(f"日期格式无效: {d}，需要 YYYYMMDD")


def encode_person(name: str, birthplace: str = None, country: str = None,
                  registry: dict = None) -> str:
    """
    Gzz-P 个人码
    格式: Gzz-P-{出生地}-{国家码}-{序号}
    出生地不明 → Gzz-P-SXJ-全球-{序号}
    """
    if not birthplace:
        birthplace = DEFAULT_BIRTH
    if not country:
        country = DEFAULT_GLOBAL

    country = normalize_country(country)
    registry = registry or {}

    # 查重分配序号
    prefix_key = f"P-{birthplace}-{country}"
    existing = [v for k, v in registry.items() if k.startswith(prefix_key)]
    seq = max([int(v) for v in existing]) + 1 if existing else 1

    code = f"Gzz-P-{birthplace}-{country}-{seq:03d}"
    registry[f"{prefix_key}-{seq:03d}"] = f"{seq:03d}"
    return code


def encode_agent(name: str, platform: str, level: str = "user",
                 registry: dict = None) -> str:
    """
    Gzz-A 智能体码
    机构级: Gzz-A-{平台}-CN-{名称}
    用户级: Gzz-A-{平台}-CN-{名称}-{序号}
    """
    registry = registry or {}
    base = f"Gzz-A-{platform}-CN-{name}"

    if level == "org":
        return base

    # 用户级加序号
    existing = [v for k, v in registry.items() if k.startswith(f"A-{platform}-{name}")]
    seq = max([int(v) for v in existing]) + 1 if existing else 1
    code = f"{base}-{seq:03d}"
    registry[f"A-{platform}-{name}-{seq:03d}"] = f"{seq:03d}"
    return code


def encode_group(name: str, unit: str, country: str = "CN",
                 registry: dict = None) -> str:
    """Gzz-G 公司/团体码: Gzz-G-{单位}-{国家码}-{序号}"""
    country = normalize_country(country)
    registry = registry or {}

    prefix_key = f"G-{unit}-{country}"
    existing = [v for k, v in registry.items() if k.startswith(prefix_key)]
    seq = max([int(v) for v in existing]) + 1 if existing else 1

    return f"Gzz-G-{unit}-{country}-{seq:03d}"


def encode_nation(country: str) -> str:
    """Gzz-N 国家码: Gzz-N-{国家码}"""
    return f"Gzz-N-{normalize_country(country)}"


def encode_event(category: str, subcategory: str, date: str,
                 registry: dict = None) -> str:
    """
    Gzz-E 事件码
    格式: Gzz-E-{大类}-{子类}-{日期}-{序号}
    """
    category = category.upper()
    subcategory = subcategory.upper()

    # 校验类别
    if category not in E_CATEGORIES:
        valid = ", ".join(E_CATEGORIES.keys())
        raise ValueError(f"无效事件大类: {category}，可选: {valid}")
    if subcategory not in E_CATEGORIES[category]:
        valid = ", ".join(E_CATEGORIES[category])
        raise ValueError(f"无效事件子类: {subcategory}，{category}下可选: {valid}")

    date = format_date(date)
    registry = registry or {}

    prefix_key = f"E-{category}-{subcategory}-{date}"
    existing = [v for k, v in registry.items() if k.startswith(prefix_key)]
    seq = max([int(v) for v in existing]) + 1 if existing else 1

    return f"Gzz-E-{category}-{subcategory}-{date}-{seq:03d}"


def encode_contribution(source: str, date: str,
                        registry: dict = None) -> str:
    """Gzz-B 贡献值: Gzz-B-{来源}-{日期}-{序号}"""
    date = format_date(date)
    registry = registry or {}

    prefix_key = f"B-{source}-{date}"
    existing = [v for k, v in registry.items() if k.startswith(prefix_key)]
    seq = max([int(v) for v in existing]) + 1 if existing else 1

    return f"Gzz-B-{source}-{date}-{seq:03d}"


def encode_negative(source: str, date: str,
                    registry: dict = None) -> str:
    """Gzz-C 负贡献: Gzz-C-{来源}-{日期}-{序号}"""
    date = format_date(date)
    registry = registry or {}

    prefix_key = f"C-{source}-{date}"
    existing = [v for k, v in registry.items() if k.startswith(prefix_key)]
    seq = max([int(v) for v in existing]) + 1 if existing else 1

    return f"Gzz-C-{source}-{date}-{seq:03d}"


def get_unified_code(name: str) -> str:
    """查询统一码（三位序号）"""
    return UNIFIED_REGISTRY.get(name, None)


def parse_gzz(code: str) -> dict:
    """解析 Gzz 编码，返回各部分"""
    parts = code.split("-")
    if len(parts) < 2 or parts[0] != "Gzz":
        raise ValueError(f"非 Gzz 编码: {code}")

    prefix = parts[1]  # P / A / G / N / E / B / C

    result = {"raw": code, "prefix": prefix}

    if prefix == "P":
        result["birthplace"] = parts[2]
        result["country"] = parts[3]
        result["seq"] = parts[4]
    elif prefix == "A":
        result["platform"] = parts[2]
        result["country"] = parts[3]
        result["name"] = parts[4]
        if len(parts) > 5:
            result["seq"] = parts[5]
    elif prefix == "G":
        result["unit"] = parts[2]
        result["country"] = parts[3]
        result["seq"] = parts[4]
    elif prefix == "N":
        result["country"] = parts[2]
    elif prefix == "E":
        result["category"] = parts[2]
        result["subcategory"] = parts[3]
        result["date"] = parts[4]
        result["seq"] = parts[5]
    elif prefix in ("B", "C"):
        result["source"] = parts[2]
        result["date"] = parts[3]
        result["seq"] = parts[4]

    return result


# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    # 测试个人码
    print(encode_person("白玺", "SXJ", "中国"))  # Gzz-P-SXJ-CN-001
    # 测试事件码
    print(encode_event("GOVERN", "CARBON", "20251006"))  # Gzz-E-GOVERN-CARBON-20251006-001
    # 测试智能体码
    print(encode_agent("白玺", "Coze", "user"))  # Gzz-A-Coze-CN-白玺-001
    # 测试统一码
    print(get_unified_code("白玺"))  # 001
    # 测试解析
    print(parse_gzz("Gzz-P-SXJ-CN-001"))