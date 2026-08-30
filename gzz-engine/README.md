# Gzz 编码引擎

事现鉴（SXJ）编码体系的本地引擎：Gzz 编码生成 + 哈希链验证 + 全量账本查询。
体系规则依据《Gzz编码体系参考_最终版_20260822.md》，哈希公式依据《Gzz引擎哈希公式破解报告_20260829.md》（964 条全量链 100% 破解）。

## 体系简介

Gzz 编码是事现鉴体系的"可验证身份证"：

- **Gzz 链上编码**（964 条，哈希链）：每个词条编码内嵌 8 位哈希，前后条哈希相连形成链（prev_hash → current_hash），任何一条被篡改都会导致后续全部断链。创世 prev_hash 为 `7d9387a7`，链尾 `36fbe640`。
  - v1 段（index 1-196，2026-08-24）：词条身份编码（196 条术语）。
  - v2/v3 段（index 197-964，2026-08-26/27）：政策锚点、实体与文档事件编码。
- **独立实体注册表**（653 条）：Gzz-G 实体码，含 hash8 自校验字段。
- **独立事件存根**（52 条）：Gzz-E-EVENT 文档/公约事件码，含 hash8 自校验字段。
- **全量账本**：964 + 653 + 52 = **1669 条**，打包于 `data/full_ledger.json`，可离线逐条复算。

## 四套哈希公式

引擎内置四套公式（见 `hash_chain.py`），全部基于 sha256 取前 8 位十六进制：

| 适用对象 | 公式 |
|---|---|
| v1 链（index 1-196） | `hash8 = sha256("{term}\|{definition}\|{event_date}\|{prev_hash}")[:8]` |
| v2/v3 链（index 197-964） | `hash8 = sha256("{term}\|{timestamp}\|{prev_hash}")[:8]`，timestamp 为 code 中 14 位时间戳段 |
| 独立实体码 | `hash8 = sha256("{name}\|{country}\|{cat}")[:8]` |
| 独立事件码 | `hash8 = sha256("{summary}\|{phase}\|{ts}")[:8]` |

> v1 复算依赖 `data/v1_items.json` 中的 196 条四元组（术语/定义/事件日期/来源）。
> 已知例外：index 112「三元光锥时空」的定义不在 v1_items.json 中（编码后脚本快照被修改过），验证时该条跳过，允许 963/964 通过。

## 目录结构

```
gzz-engine/
├── gzz_cli.py          # 命令行入口（交互菜单 + verify / lookup）
├── gzz_encoder.py      # Gzz 编码规则实现（P/A/G/N/E/B/C 各类编码）
├── gzz_registry.py     # SQLite 注册表（防重号、查询、导出）
├── hash_chain.py       # 哈希链验证层（四套公式 + verify_chain）
├── 启动.bat             # Windows 一键启动
└── data/
    ├── v1_items.json   # v1 链 196 条四元组（术语/定义/事件日期/来源）
    └── full_ledger.json# 全量账本 1669 条（chain 964 + entities 653 + events 52）
```

## 用法示例

```bash
# 1) 验证全量账本（离线逐条复算 1669 条哈希）
python gzz_cli.py verify

# 2) 在全量账本中查询（支持编码/术语/名称/哈希片段）
python gzz_cli.py lookup 恩派公益
python gzz_cli.py lookup 36fbe640
python gzz_cli.py lookup Gzz-E-SXJ-CN

# 3) 交互式编码菜单（个人/智能体/公司/事件/贡献值等编码 + 注册表管理）
python gzz_cli.py

# 4) 仅验证哈希链模块（等价于 verify，直接调用验证层）
python hash_chain.py
```

Windows 下双击 `启动.bat` 即可（自动 chcp 65001 并透传参数，如 `启动.bat verify`）。

### verify 输出样例

```
Gzz 全量账本哈希验证报告
链 chain     : 964 条 | 复算通过 963 | 跳过 1 [112] | 失败 0 []
             | 断链 0 [] | 链尾 36fbe640
实体 entities: 653 条 | 通过 653 | 失败 0
事件 events  : 52 条 | 通过 52 | 失败 0
总计 1669 条 | 通过 1668 | 跳过 1 | 失败 0 → PASS ✅
```

## 验证统计（2026-08-29 全量复算）

| 数据集 | 条数 | 复算通过 | 跳过 | 失败 |
|---|---|---|---|---|
| 链 chain（v1+v2/v3） | 964 | 963 | 1（index 112） | 0 |
| 实体 entities | 653 | 653 | - | 0 |
| 事件 events | 52 | 52 | - | 0 |
| **合计** | **1669** | **1668** | 1 | **0** |

prev_hash 零断链（963/963 连续），链尾 `36fbe640` 与账本 meta 一致。
