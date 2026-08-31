"""
Gzz 编码引擎 — 命令行入口
事现鉴 SXJ 编码体系 v1.1
用法:
  python gzz_cli.py              # 交互式编码菜单
  python gzz_cli.py verify       # 验证全量账本（chain 964 + entities 653 + events 52）
  python gzz_cli.py lookup <关键词>   # 在全量账本中查询（编码/术语/名称/哈希）
"""

import sys
import os

# 确保能找到同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gzz_encoder import (
    encode_person, encode_agent, encode_group, encode_nation,
    encode_event, encode_contribution, encode_negative,
    get_unified_code, parse_gzz, E_CATEGORIES
)
from gzz_registry import register, get_next_seq, lookup, list_all, count_by_prefix, export_all


def print_banner():
    print("""
╔══════════════════════════════════════╗
║      Gzz 编码引擎 v1.1               ║
║      事现鉴 SXJ 编码体系             ║
╚══════════════════════════════════════╝
""")


def print_usage():
    print("""
用法:
  python gzz_cli.py               # 交互式编码菜单
  python gzz_cli.py verify        # 验证全量账本哈希（chain+entities+events）
  python gzz_cli.py lookup <关键词>   # 在全量账本中查询
""")


def cmd_verify():
    """验证全量账本：调用 hash_chain 对 1669 条逐条复算"""
    from hash_chain import verify_all, format_report
    print(format_report(verify_all()))


def cmd_lookup(keyword: str):
    """在全量账本（chain/entities/events）中按关键词查询"""
    from hash_chain import load_ledger

    ledger = load_ledger()
    kw = keyword.strip()
    if not kw:
        print("  ❌ 关键词为空")
        return

    hits = []
    for e in ledger.get("chain", []):
        if any(kw in str(e.get(k, "")) for k in ("code", "term", "current_hash", "prev_hash")):
            hits.append(("链", e))
    for e in ledger.get("entities", []):
        if any(kw in str(e.get(k, "")) for k in ("code", "name", "name_en", "hash8")):
            hits.append(("实体", e))
    for e in ledger.get("events", []):
        if any(kw in str(e.get(k, "")) for k in ("code", "summary", "hash8")):
            hits.append(("事件", e))

    if not hits:
        print(f"  ❌ 全量账本中未找到: {kw}")
        return

    print(f"  🔍 '{kw}' 命中 {len(hits)} 条:\n")
    for kind, e in hits[:20]:
        if kind == "链":
            print(f"  [链] #{e['index']} {e['code']}  term={e['term']}  hash={e['current_hash']}")
        elif kind == "实体":
            print(f"  [实体] {e['code']}  {e['name']}  ({e['country']}/{e['category']})  hash={e['hash8']}")
        else:
            print(f"  [事件] {e['code']}  {e['summary']}  ({e['phase']}@{e['timestamp']})  hash={e['hash8']}")
    if len(hits) > 20:
        print(f"  ... 其余 {len(hits) - 20} 条略")


def print_menu():
    print("""
[1] 编码个人     Gzz-P    [5] 编码国家     Gzz-N
[2] 编码智能体   Gzz-A    [6] 编码贡献值   Gzz-B
[3] 编码公司     Gzz-G    [7] 编码负贡献   Gzz-C
[4] 编码事件     Gzz-E    [8] 查询统一码
                           [9] 查看注册表
                           [0] 导出全量清单
                           [Q] 退出
""")


def do_encode_person():
    name = input("姓名: ").strip()
    birthplace = input("出生地 (不明直接回车=SXJ): ").strip() or None
    country = input("国家 (如 中国): ").strip() or "中国"

    prefix_key = f"P-{birthplace or 'SXJ'}-{country}"
    seq = get_next_seq(prefix_key)
    code = f"Gzz-P-{birthplace or 'SXJ'}-{country}-{seq:03d}"

    desc = input("备注 (可选): ").strip()
    ok = register(code, name, desc)
    if ok:
        print(f"\n  ✅ 编码成功: {code}")
    else:
        print(f"\n  ⚠️ 编码已存在: {code}")


def do_encode_agent():
    name = input("智能体名称: ").strip()
    platform = input("平台 (如 Coze/DeepSeek): ").strip()
    level = input("级别 (org=机构级 / user=用户级，默认user): ").strip() or "user"

    if level == "org":
        code = f"Gzz-A-{platform}-CN-{name}"
    else:
        prefix_key = f"A-{platform}-{name}"
        seq = get_next_seq(prefix_key)
        code = f"Gzz-A-{platform}-CN-{name}-{seq:03d}"

    desc = input("备注 (可选): ").strip()
    ok = register(code, name, desc)
    if ok:
        print(f"\n  ✅ 编码成功: {code}")
    else:
        print(f"\n  ⚠️ 编码已存在: {code}")


def do_encode_group():
    name = input("公司/团体名称: ").strip()
    unit = input("单位简称: ").strip()
    country = input("国家 (默认中国): ").strip() or "中国"

    prefix_key = f"G-{unit}-{country}"
    seq = get_next_seq(prefix_key)
    code = f"Gzz-G-{unit}-{country}-{seq:03d}"

    desc = input("备注 (可选): ").strip()
    ok = register(code, name, desc)
    if ok:
        print(f"\n  ✅ 编码成功: {code}")
    else:
        print(f"\n  ⚠️ 编码已存在: {code}")


def do_encode_nation():
    country = input("国家 (如 中国): ").strip()
    code = f"Gzz-N-{country}"
    ok = register(code, country)
    if ok:
        print(f"\n  ✅ 编码成功: {code}")
    else:
        print(f"\n  ⚠️ 编码已存在: {code}")


def do_encode_event():
    print("\n事件大类:")
    for cat, subs in E_CATEGORIES.items():
        print(f"  {cat}: {', '.join(subs)}")

    category = input("\n大类: ").strip().upper()
    subcategory = input("子类: ").strip().upper()
    date = input("日期 (YYYYMMDD): ").strip()
    name = input("事件名称: ").strip()

    try:
        code = encode_event(category, subcategory, date, None)
    except ValueError as e:
        print(f"\n  ❌ {e}")
        return

    desc = input("备注 (可选): ").strip()
    ok = register(code, name, desc)
    if ok:
        print(f"\n  ✅ 编码成功: {code}")
    else:
        print(f"\n  ⚠️ 编码已存在: {code}")


def do_encode_contribution():
    source = input("来源: ").strip()
    date = input("日期 (YYYYMMDD): ").strip()
    name = input("描述: ").strip()

    try:
        code = encode_contribution(source, date, None)
    except ValueError as e:
        print(f"\n  ❌ {e}")
        return

    desc = input("备注 (可选): ").strip()
    ok = register(code, name, desc)
    if ok:
        print(f"\n  ✅ 编码成功: {code}")
    else:
        print(f"\n  ⚠️ 编码已存在: {code}")


def do_encode_negative():
    source = input("来源: ").strip()
    date = input("日期 (YYYYMMDD): ").strip()
    name = input("描述: ").strip()

    try:
        code = encode_negative(source, date, None)
    except ValueError as e:
        print(f"\n  ❌ {e}")
        return

    desc = input("备注 (可选): ").strip()
    ok = register(code, name, desc)
    if ok:
        print(f"\n  ✅ 编码成功: {code}")
    else:
        print(f"\n  ⚠️ 编码已存在: {code}")


def do_query_unified():
    name = input("名称: ").strip()
    code = get_unified_code(name)
    if code:
        print(f"\n  🔍 统一码: {code}")
    else:
        print(f"\n  ❌ 未找到 '{name}' 的统一码")


def do_view_registry():
    stats = count_by_prefix()
    if not stats:
        print("\n  📭 注册表为空")
        return

    print(f"\n  📊 注册表统计 ({sum(stats.values())} 条)")
    for prefix, count in sorted(stats.items()):
        print(f"     Gzz-{prefix}: {count} 条")

    show = input("\n查看全部? (y/n): ").strip().lower()
    if show == "y":
        all_codes = list_all()
        for c in all_codes:
            print(f"  {c['code']:50s} | {c['name'] or '-'}")


def do_export():
    text = export_all()
    export_path = os.path.join(os.path.dirname(__file__), "gzz_export.txt")
    with open(export_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n  ✅ 已导出到: {export_path}")
    print(f"\n{text[:500]}")


def main():
    # 命令行模式: verify / lookup / help
    argv = sys.argv[1:]
    if argv:
        cmd = argv[0].lower()
        if cmd == "verify":
            cmd_verify()
            return
        if cmd == "lookup":
            if len(argv) < 2:
                print("用法: python gzz_cli.py lookup <编码/术语/名称/哈希>")
                sys.exit(1)
            cmd_lookup(argv[1])
            return
        if cmd in ("-h", "--help", "help"):
            print_banner()
            print_usage()
            return
        print(f"  ❌ 未知命令: {cmd}")
        print_usage()
        sys.exit(1)

    # 交互模式
    print_banner()

    while True:
        print_menu()
        choice = input("选择: ").strip().upper()

        if choice == "1":
            do_encode_person()
        elif choice == "2":
            do_encode_agent()
        elif choice == "3":
            do_encode_group()
        elif choice == "4":
            do_encode_event()
        elif choice == "5":
            do_encode_nation()
        elif choice == "6":
            do_encode_contribution()
        elif choice == "7":
            do_encode_negative()
        elif choice == "8":
            do_query_unified()
        elif choice == "9":
            do_view_registry()
        elif choice == "0":
            do_export()
        elif choice == "Q":
            print("\n  再见。\n")
            break
        else:
            print("\n  ❌ 无效选项")

        input("\n按回车继续...")


if __name__ == "__main__":
    main()