# Gzz-W3C DID 映射规范 v1.0

## 设计依据
- W3C Verifiable Credentials v2.0：可验证凭证标准格式
- W3C DID Core：去中心化标识符规范
- SSI自主身份运动：数据主权理念
- SpruceID：开源身份基础设施参考

## 映射关系

### Gzz身份码 → W3C DID

```
Gzz-{zone}-{role}-{region}-{seq}
  ↓ 映射
did:sxj:{zone}:{role}:{region}:{seq}
```

**示例：**
| Gzz身份码 | W3C DID |
|----------|---------|
| Gzz-A-Li-CN-006 | did:sxj:A:Li:CN:006 |
| Gzz-B-BaiXi-CN-001 | did:sxj:B:BaiXi:CN:001 |
| Gzz-C-DeepSeek-CN-001 | did:sxj:C:DeepSeek:CN:001 |

### DID Document 结构

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://hygzz.中国/ns/sxj/v1"
  ],
  "id": "did:sxj:A:Li:CN:006",
  "controller": "did:sxj:A:Li:CN:006",
  "verificationMethod": [{
    "id": "did:sxj:A:Li:CN:006#key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:sxj:A:Li:CN:006",
    "publicKeyMultibase": "zH3C2..."
  }],
  "service": [{
    "id": "did:sxj:A:Li:CN:006#attestation",
    "type": "SXJAttestationService",
    "serviceEndpoint": "https://hygzz.com/api/v1/attestation"
  }],
  "sxj": {
    "role": "verification_executor",
    "zone": "A",
    "region": "CN",
    "rho_base": 0.85,
    "agent_type": "human"
  }
}
```

## 三值模型与VC的对应

| 事现鉴概念 | W3C VC 对应 |
|-----------|------------|
| Gzz身份码 | DID Subject |
| 存根 | Verifiable Credential |
| 证据来源 | Credential Evidence |
| 签发者签名 | Proof (JWS/LD-Signature) |
| ρ值 | Credential Status / Trust Framework |
| 存根链 | VC Revocation / Status List |

## 选择性披露

参照W3C VC的selective disclosure机制，Gzz支持：
- 最小化暴露：仅披露当前声明所需的身份字段
- 零知识证明：可证明"有资格验证"而不暴露具体身份
- 撤回机制：存根签发者可请求撤回（标记为revoked，不删除）

## 互操作路线

1. **Phase 1**：Gzz身份码内部使用，DID映射为可选
2. **Phase 2**：发布 `did:sxj` DID Method规范
3. **Phase 3**：与W3C DID Resolver集成，实现跨域解析
4. **Phase 4**：支持VC格式导出，与其他SSI生态互通

## 与同类方案的差异

| 维度 | SSI/DID | 事现鉴 Gzz-DID |
|-----|---------|---------------|
| 身份锚定 | 个人控制 | 公共事实关联 |
| 验证目标 | 身份真实性 | 声明真实性 |
| 互操作 | 150+ DID方法碎片化 | 统一did:sxj方法 |
| 激励 | 无 | ρ值信誉驱动 |
| 人类保留权 | 不涉及 | R-1~R-6明确保留 |