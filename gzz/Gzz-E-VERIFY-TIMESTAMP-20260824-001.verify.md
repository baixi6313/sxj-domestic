# ⚠️ 本验证命令已废弃

> 此为 v1 验证命令，指向 v2 编码 `d63ac8b3`（五元锚定，已废弃）。
> 请使用 v2 验证命令：https://hygzz.cn/gzz/Gzz-E-VERIFY-TIMESTAMP-20260824-002.verify.md

---

## 废弃原因

v2 编码的哈希计算存在以下问题：
1. claim_id 指向错误（用了 v1 的 msg_1fb05b597759 而非 v2 的 msg_f2c746091c79）
2. 前链哈希声称 c5794183，实际应为 c3a4aedb
3. 五元锚定存在鸡生蛋问题（claim_id 和 _received_at 在 POST 后才生成）

当前有效编码：`Gzz-E-EVENT-VERIFY-20260823132700-003-0194e767`（v7，三项锚定）

## 原始内容（仅作历史参考）

---

## 验证目标（已废弃）

编码：`Gzz-E-EVENT-VERIFY-20260823132700-003-d63ac8b3` ❌ 废弃
公示墙：https://hygzz.cn/api/messages?limit=2000

## 验证步骤

### 步骤1：从公示墙取编码

访问 `https://hygzz.cn/api/messages?limit=2000`，找到 claim_id 为 `msg_1fb05b597759` 的记录，确认其 code 字段为上述编码。

### 步骤2：提取五元

从墙上记录中提取：

| 元 | 从哪里取 | 值 |
|----|---------|-----|
| 内容 | content 字段 | （记录中的 content 原文） |
| 事件时间 | 编码第4段（YYYYMMDDHHMMSS） | 20260823132700 |
| 墙上时间 | _received_at 字段，转 CST（UTC+8），格式 YYYYMMDDHHMMSS | 20260824090503 |
| claim_id | claim_id 字段 | msg_1fb05b597759 |
| 前链哈希 | 公示墙上紧邻前一条记录的编码尾缀；若无尾缀则用前一条记录自算 | c5794183 |

### 步骤3：独立重算哈希

```
HASH8 = SHA256(内容 + "|" + 事件时间 + "|" + 墙上时间 + "|" + claim_id + "|" + 前链哈希)
取前8位十六进制
```

### 步骤4：比对

重算结果应等于编码尾缀 `d63ac8b3`。

---

## 验证要点

1. **不要信我给的任何值**——内容、_received_at 必须从公示墙直接取，不能用我写的
2. **前链哈希