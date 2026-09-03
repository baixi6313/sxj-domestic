# 事现鉴 · Gzz 统一编号体系 v1.0

> 2026-08-24 · 基于 Kimi 三版本公开（msg_a38ad89c833a）+ 实际运行经验

## 问题

手册定义的编号体系与实际使用不一致：

| 维度 | 手册 v0.2 | 实际使用 |
|------|----------|---------|
| 大类 | VERIFY/AUDIT/GOVERN/GZZP 四个 | EVENT/DEPLOY/SPEC/ANALYSIS/FIX/VERIFY 等自由扩展 |
| 子类 | 每大类固定子类（如 VERIFY→FIN/COMP/DATA） | 自由描述（如 VERIFY-TIMESTAMP、EVENT-VERIFY） |
| 序号 | 日期+序号 | 日期+时分秒+序号 |
| 尾缀 | 无 | 三项锚定哈希（v2.1） |

## 统一方案

### 编码格式

```
Gzz-E-{大类}-{子类}-{YYYYMMDDHHMMSS}-{序号}-{HASH8}
```

### 大类（Category）

不再限定为四个，而是按三元光锥空间站体系自由扩展：

| 大类 | 含义 | 三元光锥空间站 |
|------|------|---------|
| **EVENT** | 事件记录 | 任意 |
| **VERIFY** | 验证 | 数字·中 |
| **DEPLOY** | 部署 | 数字·中 |
| **SPEC** | 规范/协议 | 数字·上 |
| **FIX** | 修复 | 数字·中 |
| **ANALYSIS** | 分析 | 数字·中 |
| **RECOMMEND** | 建议 | 数字·上 |
| **AUDIT** | 审计 | 数字·上 |
| **GOVERN** | 治理 | 人力·上 |
| **GZZP** | 共济值 | 数字/资产 |
| **DD** | 尽调（Due Diligence） | 数字·中 |

### 子类（Subcategory）

自由描述，不限定。推荐使用短标识符（如 VERIFY、TIMESTAMP、DATA 等），但不强制。

### 序号

格式：`{YYYYMMDDHHMMSS}-{NNN}`

- 日期时间精确到秒（CST）
- 序号为三位数字，同一天内递增

### 尾缀哈希

三项锚定（v2.1）：`SHA256(内容 + "|" + 事件时间 + "|" + 前链哈希)[:8]`

非事件类编码（如规范发布）可省略尾缀。

### 旧编码兼容

旧编码（无时间戳、无尾缀）继续有效。格式转换规则：

```
旧：Gzz-E-EVENT-20260824-003
新：Gzz-E-EVENT-{类别}-{YYYYMMDDHHMMSS}-003-{HASH8}
```

## 手册子类表（推荐，非强制）

保留手册原有子类作为推荐分类，但不强制：

| 大类 | 推荐子类 |
|------|---------|
| VERIFY | FIN（金融）、COMP（对比）、DATA（数据）、TIMESTAMP（时间戳） |
| AUDIT | SEC（安全）、LEDGER（账本）、PROTO（协议） |
| GOVERN | CHARTER（章程）、VOTE（投票）、DISPUTE（争议）、CARBON（碳足迹） |
| GZZP | ISSUE（发放）、ANCHOR（锚定）、RELIEF（救助） |

## 注册机制（未来）

编码创建后自动投递公示墙，公示墙即为编码注册表。不需要额外注册步骤。