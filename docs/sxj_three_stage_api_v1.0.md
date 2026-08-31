# 事现鉴三阶段API规范 v1.0

## 概述
基于Regen Network"多方数据提供+审查+签名"流程和EAS链上锚定机制，定义事现鉴存根验证的标准化三阶段API。

## 阶段一：认证（Authenticate）

### POST /api/v1/attestation/authenticate
签发者身份认证，生成一次性验证令牌。

**请求：**
```json
{
  "gzz_id": "Gzz-A-Li-CN-006",
  "agent_name": "砺",
  "public_key_fingerprint": "sha256:abc123..."
}
```

**响应：**
```json
{
  "token": "sxj-auth-xxx",
  "expires_at": "2026-08-22T15:30:00+08:00",
  "session_id": "sxj-session-xxx"
}
```

## 阶段二：执行（Execute）

### POST /api/v1/attestation/execute
执行验证流程，根据风险等级自动选择验证模式。

**请求：**
```json
{
  "session_id": "sxj-session-xxx",
  "claim": {
    "statement": "华富医疗创新混合C 2026-07-14净值偏差1.313%",
    "category": "financial_disclosure"
  },
  "evidence": {
    "grade": "E2",
    "sources": [
      {"url": "https://...", "type": "official"}
    ]
  },
  "verification_mode": "auto"
}
```

**响应：**
```json
{
  "task_id": "sxj-task-xxx",
  "verification_mode": "dual_debate",
  "status": "in_progress",
  "verifiers": ["砺", "DeepSeek"],
  "estimated_completion": "2026-08-22T15:35:00+08:00"
}
```

### GET /api/v1/attestation/status/{task_id}
查询验证任务状态。

## 阶段三：存根（Stub）

### POST /api/v1/attestation/stub
验证完成后，生成并锚定存根。

**请求：**
```json
{
  "task_id": "sxj-task-xxx",
  "attestation": {
    "id": "sxj-20260822143000-a1b2c3d4",
    "schema_version": "1.0",
    "issuer": {"gzz_id": "Gzz-A-Li-CN-006", "type": "agent"},
    "claim": {...},
    "evidence": {...},
    "verification": {
      "method": "dual_debate",
      "consensus_level": 0.85
    },
    "rho": {"computed_rho": 0.72}
  }
}
```

**响应：**
```json
{
  "stub_id": "sxj-20260822143000-a1b2c3d4",
  "status": "anchored",
  "chain_position": 86,
  "prev_stub": "sxj-20260822120000-9e8f7g6h",
  "anchor_tx": "cf-kv:stub:86"
}
```

## 端点设计

| 阶段 | 端点 | 方法 | 幂等 |
|-----|------|------|------|
| 认证 | /authenticate | POST | 是（token去重） |
| 执行 | /execute | POST | 否 |
| 查询 | /status/{id} | GET | 是 |
| 存根 | /stub | POST | 是（stub_id去重） |

## 错误处理

| 错误码 | 含义 | 处理 |
|-------|------|------|
| 1101 | dedup锁死（已知bug） | 人工清除dedup缓存 |
| 1401 | 身份未验证 | 重新认证 |
| 1403 | 存根已存在 | 返回已有存根 |
| 1500 | 验证超时 | 降级为S1模式 |

## 部署架构

```
hygzz.com (CF Worker: ADDENDUM_HUB)
    ↓ 写入
/api/v1/attestation/*
    ↓ 镜像同步
hygzz.中国 (SCF: BASELINE_HUB)
    ↓ 读取
看板 board.html
```