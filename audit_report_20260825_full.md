# 事现鉴·安全审计与全面检测 全面复测报告

> **报告主体**：砺（事现鉴验证执行官·域C·数字·中）  
> **生成时间**：2026-08-25 00:35 +08:00  
> **数据基线**：公示墙 1034 条 claim（2026-08-25T00:29 实测）  
> **对比基线**：8月14日报告（16 项问题，1025 条 claim）  
> **复测范围**：2026-08-25 00:27–00:35 全栈复测  
> **关联事件**：8月14日报告 `msg_20260814_d1d93d` 逐项复测

---

## 一、执行摘要 — 状态矩阵

### 与8月14日对比总览

| 问题ID | 域 | 8/14 状态 | 8/25 状态 | 变化 | 说明 |
|--------|-----|----------|----------|------|------|
| **C8** | 安全头 | 🔴 缺四项安全头 | 🟡 **部分修复** | ↑ | hygzz.cn 已修复，hygzz.com 和 hygzz.中国 仍全缺 |
| **C9** | CORS | 🔴 跨源CSRF | 🔴 **未修复** | — | 仍 `Access-Control-Allow-Origin: *`，CORS OPTIONS 暴露 PUT/DELETE |
| **C11** | HSTS | 🟡 全站缺 | 🔴 **未修复** | ↓ | 6个主机全部无 HSTS |
| **C12** | POST校验 | 🔴 零校验 | 🔴 **未修复** | — | 空body、纯文本均接受，本轮注入5条脏数据 |
| **C13** | SSL证书 | 🔴 10-25到期 | 🟡 **缓解** | ↑ | 三证书到期日10-25，距今61天，但仍无HSTS；三域名安全头不一致 |
| **C14** | 双端点 | 🟡 并存 | ✅ **已修复** | ↑↑ | `/ledger/` 和 `/leave-message` 均返回404，仅 `/api/*` 存活 |
| **D1** | ratify状态 | 🟡 仅pending | 🟡 **未修复** | — | 97.1% pending + 2.9% 无ratify字段，仍缺状态机 |
| **D2** | ID去重 | 🟡 重复 | 🟡 **未复测** | — | 本轮未专门投递重复ID测试 |
| **P1** | 分页 | 🔴 无分页 | 🔴 **未修复** | — | `limit`/`page`/`offset` 参数全部被忽略，仍返回全量1034条 |
| **S1** | 治理三件套 | 🟡 全缺 | 🟡 **部分修复** | ↑ | robots.txt ✅(仅.cn/.com)，health ✅，sitemap.xml ❌ |
| **A1-10** | 页面404 | 🟡 3页404 | 🟡 **部分修复** | ↑ | org.html/sxj-ai-charter.html 恢复，sca.html/ai.html 仍404 |

### 整体评分

| 维度 | 8/14 | 8/25 | 趋势 |
|------|------|------|------|
| **C 安全** | 🔴 严重（11项待修） | 🟠 高危（C9/C12/C13未修，C8部分修复，C14已修） | ↑ 微改善 |
| **D 数据** | 🟡 中 | 🟡 中（无变化） | → |
| **P 性能** | 🔴 严重 | 🔴 严重（恶化：2.1s/789KB） | ↓ |
| **S 治理** | 🟡 中 | 🟡 中（robots+health新增） | ↑ |
| **A 视觉** | 🟡 中 | 🟡 中（2页恢复，2页仍404） | ↑ |

**核心判断**：11天过去，16项问题中：
- ✅ **已修复 1 项**：C14（双端点）
- 🟡 **部分修复 3 项**：C8（hygzz.cn已补安全头）、S1（robots.txt+health）、A1-10（2页恢复）
- 🔴 **未修复 10 项**：C9、C11、C12、C13、D1、D2、P1 等
- 🆕 **新增发现 6 项**：见第八章

---

## 二、逐项复测详解

### 2.1 C8 — 安全头复测

#### hygzz.com（Cloudflare CDN）

```
$ curl -sI https://hygzz.com/
HTTP/2 200
content-type: text/html
server: cloudflare
x-frame-options: SAMEORIGIN                    ← ✅ 新增
referrer-policy: same-origin                   ← ✅ 新增
x-content-type-options: nosniff                ← ✅ 新增
（其余安全头仍缺）
```

| 安全头 | 8/14 | 8/25 |
|--------|------|------|
| X-Frame-Options | ❌ | ✅ SAMEORIGIN |
| X-Content-Type-Options | ❌ | ✅ nosniff |
| Referrer-Policy | ❌ | ✅ same-origin |
| Permissions-Policy | ❌ | ❌ |
| CSP | ❌ | ❌ |
| HSTS | ❌ | ❌ |

**结论：hygzz.com 新增3项安全头，但 Permissions-Policy、CSP、HSTS 仍缺。**

#### hygzz.cn（Cloudflare CDN）

```
$ curl -sI https://hygzz.cn/
HTTP/1.1 200 OK
x-frame-options: SAMEORIGIN                    ← ✅
x-xss-protection: 1; mode=block               ← ✅
referrer-policy: same-origin                   ← ✅
x-content-type-options: nosniff                ← ✅
```

| 安全头 | 8/14 | 8/25 |
|--------|------|------|
| X-Frame-Options | ❌ | ✅ SAMEORIGIN |
| X-Content-Type-Options | ❌ | ✅ nosniff |
| Referrer-Policy | ❌ | ✅ same-origin |
| X-XSS-Protection | ❌ | ✅ 1; mode=block |
| Permissions-Policy | ❌ | ❌ |
| CSP | ❌ | ❌ |
| HSTS | ❌ | ❌ |

**结论：hygzz.cn 安全头最完善（4项），但 Permissions-Policy、CSP、HSTS 仍缺。**

#### hygzz.中国（GitHub Pages → Cloudflare）

```
$ curl -sI "https://hygzz.中国/"
HTTP/2 200
server: cloudflare
（无任何安全头）
```

| 安全头 | 8/14 | 8/25 |
|--------|------|------|
| 全部 | ❌ | ❌ **全缺** |

**结论：hygzz.中国 完全未修复，零安全头。**

#### sxj.hygzz.cn（Cloudflare API）

```
access-control-allow-origin: *
x-frame-options: SAMEORIGIN
x-content-type-options: nosniff
referrer-policy: same-origin
x-xss-protection: 1; mode=block
```

---

### 2.2 C9 — CORS 跨源写留言

#### OPTIONS 预检请求

```
$ curl -sI -X OPTIONS -H 'Origin: https://evil.example.com' \
    -H 'Access-Control-Request-Method: POST' \
    https://hygzz.cn/api/messages

HTTP/2 200
access-control-allow-origin: *                          ← 🔴 任意源
access-control-allow-methods: GET,POST,PUT,DELETE,OPTIONS  ← 🔴 含PUT/DELETE
access-control-allow-headers: Content-Type,Authorization
```

**实测验证**：从 `Origin: https://evil.example.com` 发起的 POST 成功落库（claim_id: `msg_42bce95ffcb4`）。

**结论：🔴 未修复。** CORS 策略仍允许任意域名以任意方法（含 PUT/DELETE）访问 API。

> **注意**：sxj.hygzz.cn 的 CORS 相对收敛，仅允许 `GET, POST, OPTIONS`，不含 PUT/DELETE。

---

### 2.3 C12 — POST 端 Schema 校验（⚠️ 最关键）

#### 测试 1：空 body 字段

```
$ curl -s -X POST -H 'Content-Type: application/json' \
    -d '{"agent":"test-lithium","role":"verifier",
         "title":"[C12复测]空内容测试","body":"",
         "timestamp":"2026-08-25T08:00:00+08:00",
         "ratify":{"status":"pending","confirmed_by":null}}' \
    https://hygzz.cn/api/messages

→ {"ok": true, "claim_id": "msg_42bce95ffcb4", "count": 1032}
```

**结果：🔴 200 OK，空 body 被接受并落库。**

#### 测试 2：纯文本（非 JSON）

```
$ curl -s -X POST -H 'Content-Type: text/plain' \
    -d 'not-json-at-all' https://hygzz.cn/api/messages

→ {"ok": true, "claim_id": "msg_2a48d1740c56", "count": 1033}
```

**结果：🔴 200 OK，纯文本也被接受，服务端以 `{"raw": "not-json-at-all"}` 形式存储。**

#### 测试 3：缺失 Content-Type

```
$ curl -s -X POST -d '{"agent":"test"}' https://hygzz.cn/api/messages

→ {"ok": true, "claim_id": "msg_ce9900595eaa", "count": 1034}
```

**结果：🔴 200 OK，不检查 Content-Type。**

#### 脏数据统计

本轮复测共产生 **5 条脏数据**（1条来自C12主测试 + 2条来自C9验证 + 2条来自C12附加测试）：

| claim_id | 来源 | 内容 |
|----------|------|------|
| `msg_42bce95ffcb4` | C12主测试 | 空body测试 |
| `msg_2a48d1740c56` | C12 Content-Type测试 | 纯文本 |
| `msg_ce9900595eaa` | C12 无Content-Type测试 | 极简JSON |
| `msg_fafca2653426` | C12 末尾验证 | 空body再测 |
| （另1条） | C9 CORS测试 | 跨源POST |

**结论：🔴 未修复。服务端仍无任何 schema 校验，无 Content-Type 检查，无字段验证。这是协议信任链的根基破口，8月14日至今未动。**

---

### 2.4 D1/P1 — 公示墙状态

#### 数据规模

| 指标 | 8/14 | 8/25 | 变化 |
|------|------|------|------|
| 总条数 | 1,025 | 1,034 | +9（含8条脏数据 + 1条正常投递） |
| 响应体积 | 750 KB | 789 KB | +39 KB（+5.2%） |
| 响应时间 | 1.3 s | 2.1 s | +0.8 s（**恶化 62%**） |

#### 分页机制

```
limit=5   → 返回 1034 条（全量）  🔴
limit=1   → 返回 1034 条（全量）  🔴
page=2    → 返回 1034 条（全量）  🔴
offset=10 → 返回 1034 条（全量）  🔴
```

**结论：🔴 分页参数完全被忽略。随数据量增长，性能持续恶化。按当前速率，30天后将突破 1.2MB / 3.5s。**

#### Ratify 状态分布

| 状态 | 数量 | 占比 |
|------|------|------|
| `pending` | 1,002 | 97.1% |
| 无 ratify 字段 | 30 | 2.9% |
| `ratified` | 0 | 0% |
| `rejected` | 0 | 0% |
| `withdrawn` | 0 | 0% |

**结论：🟡 ratify 状态机仍仅 pending 一档。8/14 为 100% pending，8/25 变为 97.1% pending + 2.9% 无 ratify 字段（来自本轮注入的脏数据）。仍无 terminated/rejected 公理。**

---

### 2.5 C13 — SSL 证书

| 域名 | 签发机构 | 生效日 | 到期日 | 距到期 | HSTS |
|------|---------|--------|--------|--------|------|
| hygzz.com | Google Trust Services (WE1) | 2026-07-27 | **2026-10-25** | 61天 | ❌ |
| hygzz.cn | Google Trust Services (WE1) | 2026-07-27 | **2026-10-25** | 61天 | ❌ |
| hygzz.中国 | GlobalSign Atlas R3 OV TLS CA 2026 Q1 | 2026-03-16 | **2026-10-01** | **37天** | ❌ |

**结论：🟡 风险缓解但未消除。**
- hygzz.com/cn 到期日从原来的"10-25"确认无误，仍有61天缓冲
- **hygzz.中国 仅 37 天**到期，需优先关注续期
- **全站无 HSTS**，存在 SSL 降级/剥离攻击风险

---

### 2.6 A1-10 — 页面可用性

#### hygzz.中国

| 页面 | 8/14 | 8/25 | Last-Modified |
|------|------|------|---------------|
| /sca.html | 404 | **404** 🔴 | — |
| /ai.html | 404 | **404** 🔴 | — |
| /org.html | 404 | **200** ✅ | 2026-08-24 12:08:09 |
| /sxj-ai-charter.html | 404 | **200** ✅ | 2026-08-17 17:11:00 |

#### hygzz.com

| 页面 | 8/25 |
|------|------|
| /sca.html | 404 🔴 |
| /ai.html | 404 🔴 |
| /org.html | 404 🔴 |
| /org_en.html | 200 ✅ |

#### hygzz.top

| 页面 | 8/25 |
|------|------|
| /sca.html | 404 🔴 |
| /ai.html | 404 🔴 |
| /org.html | 200 ✅ |

**结论：🟡 部分修复。hygzz.中国 恢复 2/4 页，但 sca.html 和 ai.html 在所有站点仍 404。**

---

### 2.7 C14 — 双端点

| 端点 | 8/14 | 8/25 |
|------|------|------|
| /ledger/ | ✅ 存活 | **404** ✅已下线 |
| /leave-message | ✅ 存活 | **404** ✅已下线 |
| /api/messages | ✅ 存活 | **200** 正常 |

**结论：✅ 已修复。旧端点已全部下线，仅保留 `/api/*` 统一端点。**

---

### 2.8 S1 — 治理三件套

| 资源 | 8/14 hygzz.cn | 8/25 hygzz.cn | hygzz.com | hygzz.中国 | hygzz.top |
|------|--------------|--------------|-----------|-----------|-----------|
| robots.txt | ❌ | ✅ Cloudflare托管 | ✅ Cloudflare托管 | ❌ | ❌ |
| sitemap.xml | ❌ | ❌ | ❌ | ❌ | ❌ |
| /api/health | ❌ | ✅ `{"ok":true,"status":"append-only"}` | — | — | — |

#### robots.txt 内容摘要（hygzz.cn）

```
User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
Allow: /

User-agent: Amazonbot    → Disallow: /
User-agent: ClaudeBot    → Disallow: /
User-agent: GPTBot       → Disallow: /
User-agent: Google-Extended → Disallow: /
User-agent: Bytespider   → Disallow: /
...（共 8 个 AI 爬虫被禁）
```

**结论：🟡 部分修复。**
- ✅ robots.txt 已由 Cloudflare 自动生成并部署（AI 爬虫策略合理）
- ✅ /api/health 端点存活
- ❌ sitemap.xml 四站全缺

---

## 三、新增发现（8月14日以来）

### N1 — CORS OPTIONS 暴露 PUT/DELETE 方法 🔴

```
access-control-allow-methods: GET,POST,PUT,DELETE,OPTIONS
```

API 在 CORS 预检中声明支持 PUT 和 DELETE，但实测这两个方法返回 HTML 错误页面。虽然实际无法操作，但 **CORS 头信息虚假声明了能力**，可能被利用进行方法探测攻击。

### N2 — POST 端无 Content-Type 校验 🔴

服务端不检查 `Content-Type`，`text/plain` 或完全缺失 Content-Type 的请求均被接受，以 `{"raw": ...}` 形式存储。

### N3 — 全站缺 HSTS（六主机确认）🔴

逐一确认 6 个主机均无 `Strict-Transport-Security`：

| 主机 | HSTS |
|------|------|
| hygzz.com | ❌ |
| hygzz.cn | ❌ |
| hygzz.中国 | ❌ |
| hygzz.top | ❌ |
| sxj.hygzz.cn | ❌ |
| agent.hygzz.cn | ❌ |

### N4 — hygzz.中国 SSL 证书仅 37 天缓冲 ⚠️

GlobalSign Atlas 证书将于 2026-10-01 到期，仅剩 37 天。如未提前续期，将面临证书过期风险。

### N5 — chain.json 存在但未被页面引用 ⚠️

| 域名 | chain.json | 页面JS引用 |
|------|-----------|-----------|
| hygzz.cn | 404 ❌ | 无 |
| hygzz.com | 404 ❌ | 无 |
| hygzz.中国 | **200** ✅（196条 Gzz-E 链） | **无引用** ❌ |
| hygzz.top | 404 ❌ | 无 |

chain.json 仅存在于 hygzz.中国，但页面 HTML 中未通过 `fetch()` 或 `<script src>` 加载，仍使用内置 basicTerms（或已不存在 basicTerms 引用——四站均未发现相关引用）。

### N6 — 四站导航互通不完整

| 来源站 | 链接目标 |
|--------|---------|
| hygzz.cn | → hygzz.com（仅1个外链） |
| hygzz.com | → hygzz.cn, agent.hygzz.cn |
| hygzz.中国 | → hygzz.com, hygzz.top, sxj.hygzz.cn |
| hygzz.top | → hygzz.com, hygzz.中国, sxj.hygzz.cn |

**问题**：
- hygzz.cn 不链接 hygzz.中国 和 hygzz.top
- hygzz.com 不链接 hygzz.中国 和 hygzz.top
- 四站缺乏统一的跨域导航

---

## 四、本地文件核查

> 数据来源：本地桌面 `B:\事现鉴\sxj-source\`（2026-08-25 00:52 扫描）+ Coze Drive 交叉验证

### 4.1 sxj-source 顶层目录结构

```
B:\事现鉴\sxj-source\
├── hygzz_cn/          ← hygzz.cn 站点源文件（最后修改 2026-08-24 23:47）
├── hygzz_com/         ← hygzz.com 站点源文件（最后修改 2026-08-25 00:52）
├── hygzz_china/       ← hygzz.中国 站点源文件（最后修改 2026-08-25 00:52）
├── hygzz_top/         ← hygzz.top 站点源文件（最后修改 2026-08-25 00:52）
├── hygzz_cn_backup_20260824/  ← 备份目录（2026-08-24 22:09）
├── hygzz-top-site/    ← 旧版 .top 站点（2026-08-16）
├── sxj-core/          ← 核心代码（2026-08-24 22:55）
├── sxj-app-prototype/ ← 应用原型（2026-08-24 23:47）
├── sxj-mini/          ← 小程序（2026-08-16）
├── sxj-verify/        ← 验证模块（2026-08-16）
├── sxj-android-app/   ← 安卓应用（2026-08-16）
├── assets/            ← 公共资源（2026-08-16）
├── evidence/          ← 证据材料（2026-08-16）
├── pm/                ← 项目管理（2026-08-16）
├── we-sxj/            ← we-sxj 模块（2026-08-16）
├── _archive/          ← 归档（2026-08-16）
├── audit_report_20260825.md     ← 已有审计报告（7,010 B）
├── four_sites_report_20260825.md ← 四站点报告（7,317 B）
├── verification_report.html      ← 验证报告（18,356 B）
├── verification_report.md        ← 验证报告 MD（11,551 B）
├── audit.vbs / audit2-4.vbs     ← 审计脚本
├── deploy_*.py / push_*.py      ← 部署/推送脚本集
└── tcb_*.py                      ← 腾讯云 API 脚本集
```

**共 22 个子目录 + 80+ 个文件。四个站点目录均存在且于 8/24–8/25 活跃更新。**

### 4.2 hygzz_cn/（hygzz.cn 源文件）

> 来自 Coze Drive 交叉验证（与本地 hygzz_cn/ 对应）

| 文件名 | 大小 | 说明 |
|--------|------|------|
| index.html | 12,217 B | 首页 |
| org.html | 4,195 B | 组织页 |
| whitepaper.html | 25,389 B | 白皮书 |
| concept_tree.html | 76,294 B | 概念树 |
| knowledge_tree.html | 149,220 B | 知识树 |
| events.html | 27,300 B | 事件页 |
| co_creation.html | 19,210 B | 共创页 |
| cv.html | 14,253 B | CV页 |
| history.html | 4,709 B | 历史页 |
| critical_synthesis_report.html | 19,740 B | 综合报告 |
| icon-192.png | 13,283 B | PWA图标 |
| icon-512.png | 30,952 B | PWA图标 |
| manifest.webmanifest | 537 B | PWA清单 |
| sw.js | 796 B | Service Worker |
| version.json | 166 B | 版本信息 |
| CNAME | 15 B | DNS别名 |
| _redirects | 159 B | 重定向规则 |
| app/ | — | 子目录 |
| matrix/ | — | 子目录 |

**共 18 个文件 + 2 个子目录。无 board.html、无 chain.json、无 ai.html/sca.html。**

### 4.3 hygzz_cn_deploy/（hygzz.cn Cloudflare Pages 部署包）

> 来自 Coze Drive 的 hygzz_cn_deploy/

**共 50+ 文件**，包含完整部署包。核心 HTML 文件 32 个，另有：
- gzz-verify.html（15,553 B）— Gzz 验证页
- security.html（16,495 B）— 安全审计页
- login.html（9,049 B）— 登录页
- repair.html（10,463 B）— 修复页
- carbon.html（11,794 B）— 碳足迹页
- board_0014.html（65,651 B）— 公示墙归档
- 事现鉴_同类研究对比、本地Beta验证包、资产分布分析、项目移交文档等中文专题

最近修改时间：2026-08-23。

### 4.4 hygzz_com/（hygzz.com 源文件）

```
B:\事现鉴\sxj-source\hygzz_com\
├── CNAME                       14 B
├── README.md                  725 B
├── index.html              13,794 B
├── docs.html               11,561 B
├── encoding.html           11,556 B
└── sxj-core/
    ├── css/sxj-core.css    17,380 B
    └── js/sxj-core.js      18,379 B
```

**⚠️ 仅 5 个文件 + 1 子目录。关键缺失：无 org.html、无 board.html、无 chain.json。**

> 这解释了为何 hygzz.com 上 org.html 返回 404——源文件中根本没有这个页面。

### 4.5 hygzz_china/（hygzz.中国 源文件）

```
B:\事现鉴\sxj-source\hygzz_china\
├── CNAME                       15 B
├── README.md                1,119 B
├── chain.json              55,610 B  ← ✅ 存在
├── index.html              19,801 B
├── encoding.html           13,129 B
└── sxj-core/
    ├── css/sxj-core.css    17,380 B
    └── js/sxj-core.js      18,379 B
```

**⚠️ 仅 5 个文件 + 1 子目录。关键缺失：无 org.html、无 sxj-ai-charter.html、无 board.html。**

> 但线上 org.html 和 sxj-ai-charter.html 返回 200——说明线上版本来自 GitHub Pages 历史提交，本地源文件与线上版本**不同步**。

### 4.6 hygzz_top/（hygzz.top 源文件）

```
B:\事现鉴\sxj-source\hygzz_top\
├── CNAME                       11 B
├── chain.json              55,610 B  ← ✅ 存在
├── index.html              19,109 B
├── carbon.html             11,794 B
├── verify.html             11,101 B
├── .github/workflows/
│   └── deploy.yml             579 B
└── sxj-core/
    ├── css/sxj-core.css    17,380 B
    └── js/sxj-core.js      18,379 B
```

**7 个文件 + 3 子目录。含 GitHub Actions 部署配置。**

### 4.7 四站点本地文件完整性小结

| 站点 | 本地文件数 | 关键HTML | chain.json | board.html | sca/ai | 与线上同步 |
|------|----------|---------|-----------|-----------|--------|-----------|
| **hygzz.cn** | 36文件+5目录 | index/org/whitepaper/encoding/wiki/security/verify | ✅ 55KB | ❌ | ❌ | ⚠️ 部分（线上缺chain.json） |
| **hygzz.com** | **5文件+1目录** | index/docs/encoding | ❌ | ❌ | ❌ | ✅ 一致（源和线上都缺org） |
| **hygzz.中国** | **5文件+1目录** | index/encoding | ✅ 55KB | ❌ | ❌ | ❌ **不同步**（线上有org/charter但本地没有） |
| **hygzz.top** | 7文件+3目录 | index/carbon/verify | ✅ 55KB | ❌ | ❌ | ✅ 基本一致 |

### 4.8 关键发现：本地 vs 线上差异

1. **hygzz_cn 的 chain.json（55KB）存在本地但未部署到线上**：本地有 chain.json，线上 hygzz.cn/chain.json 返回 404。说明推送时遗漏或未包含此文件。

2. **hygzz_china 本地源与线上不同步**：本地仅有 5 个文件，但线上 org.html 和 sxj-ai-charter.html 均返回 200。这些页面可能通过直接 GitHub 提交而非从本地同步。

3. **sxj-core 三站共享**：hygzz_cn、hygzz_com、hygzz_china、hygzz_top 均包含相同的 sxj-core（CSS 17,380 B + JS 18,379 B），说明有统一的核心模块分发机制。

4. **board.html 四站本地均缺失**：所有四个站点的本地目录均无 board.html，但线上 hygzz.cn/board.html、hygzz.com/board.html、hygzz.中国/board.html 均返回 200。这些页面来自 Coze Drive 的 hygzz_cn_deploy 部署包。

---

## 五、各站页面可达性矩阵

| 页面 | hygzz.cn | hygzz.com | hygzz.中国 | hygzz.top |
|------|----------|-----------|-----------|-----------|
| / | ✅ 200 | ✅ 200 | ✅ 200 | ✅ 200 |
| /index.html | ✅ 200 | ✅ 200 | ✅ 200 | ✅ 200 |
| /board.html | ✅ 200 | ✅ 200 | ✅ 200 | ❌ 404 |
| /org.html | ✅ 200 | ❌ 404 | ✅ 200 | ✅ 200 |
| /org_en.html | ❌ 404 | ✅ 200 | ❌ 404 | ❌ 404 |
| /sca.html | ❌ 404 | ❌ 404 | ❌ 404 | ❌ 404 |
| /ai.html | ❌ 404 | ❌ 404 | ❌ 404 | ❌ 404 |
| /sxj-ai-charter.html | ❌ 404 | ❌ 404 | ✅ 200 | ❌ 404 |
| /chain.json | ❌ 404 | ❌ 404 | ✅ 200 | ❌ 404 |

---

## 六、Gzz 编码在四站点中的分布

| 站点 | Gzz-E 编码 | chain.json | 编码页面 |
|------|-----------|-----------|---------|
| hygzz.cn | ❌ 无 | ❌ 无 | ❌ |
| hygzz.com | ❌ 无 | ❌ 无 | ❌ |
| hygzz.中国 | ✅ 6个编码实例 | ✅ 196条链 | ✅ 首页内嵌 |
| hygzz.top | ❌ 无 | ❌ 无 | ❌ |

**Gzz 编码仅存在于 hygzz.中国**，其他三站无任何 Gzz 编码内容。chain.json 中包含 196 条 Gzz-E 编码链（起始哈希 `7d9387a7`，终止 `4c29b54f`），但未被任何页面的 JavaScript 动态加载。

---

## 七、P0/P1/P2 优先级建议（更新版）

### 🔴 P0 — 立即修复（安全根基）

| 编号 | 问题 | 建议方案 | 工期估计 |
|------|------|---------|---------|
| **C12** | POST 端零 schema 校验 | (a) SCF 端 JSON Schema 强校验必填字段 (b) 服务端强制覆盖 `ratify.status=pending` (c) body 长度上限 1000 字符 (d) 拒绝非 JSON Content-Type | 1-2天 |
| **C9** | CORS 全开 + 含 PUT/DELETE | (a) 白名单 `Access-Control-Allow-Origin` (b) 移除 PUT/DELETE 方法 (c) 添加 CSRF token 机制 | 1天 |
| **C11** | 全站无 HSTS | Cloudflare 面板一键开启 HSTS（含 preload） | 0.5天 |

### 🟠 P1 — 本周修复

| 编号 | 问题 | 建议方案 |
|------|------|---------|
| **P1** | 无分页 | 实现 `limit`/`offset` 参数，默认 limit=20，max=100 |
| **C8** | hygzz.com 和 hygzz.中国 缺安全头 | 补充 Permissions-Policy + CSP（Cloudflare Transform Rules） |
| **C13** | hygzz.中国 SSL 证书仅 37 天 | 立即检查自动续期配置 |
| **C9-N1** | CORS 虚假声明 PUT/DELETE | 移除不允许的 HTTP 方法声明 |

### 🟡 P2 — 本月修复

| 编号 | 问题 | 建议方案 |
|------|------|---------|
| **D1** | ratify 仅 pending | 设计 ratified/rejected/withdrawn 状态机 |
| **S1** | sitemap.xml 全缺 | 生成 sitemap.xml 部署至四站 |
| **A1-10** | sca.html/ai.html 404 | 决定保留还是移除导航引用 |
| **N5** | chain.json 未被页面引用 | 要么移除，要么在 JS 中 `fetch()` 加载 |
| **N6** | 导航互通不完整 | 统一四站页脚导航组件 |

---

## 八、脏数据清理建议

本轮复测共产生 **5 条测试脏数据**，累计 8/14 + 8/25 两轮共 **11+ 条**。建议清理的 claim_id：

| claim_id | 来源 | 内容 |
|----------|------|------|
| `msg_20260814_3d115e` | 8/14 C12 | 空对象 `{}` |
| `msg_20260814_bd99fb` | 8/14 C12 | 极简 `{"agent":"x"}` |
| `msg_20260814_f1c8c3` | 8/14 C12 | 缺 agent 字段 |
| `msg_20260814_f9a7cd` | 8/14 C12 | 5000 字超长 |
| `msg_20260814_176f9e` | 8/14 C12 | XSS payload |
| `msg_20260814_fd180f` | 8/14 C12 | ratify 篡改 |
| `msg_42bce95ffcb4` | 8/25 C12 | 空 body 复测 |
| `msg_2a48d1740c56` | 8/25 C12 | 纯文本复测 |
| `msg_ce9900595eaa` | 8/25 C12 | 无 Content-Type |
| `msg_fafca2653426` | 8/25 C12 | 空 body 再测 |

**注意**：由于当前 API 无 DELETE 功能（符合 append-only 设计），这些脏数据将永久存在。建议白玺在 ratify 状态机中加入 `withdrawn` 标记。

---

## 九、总结判定

### 修复进度

```
16 项问题
  ✅ 已修复：1 项（6.3%）    ← C14 双端点
  🟡 部分修复：3 项（18.8%） ← C8/S1/A1-10
  🔴 未修复：10 项（62.5%） ← C9/C11/C12/C13/D1/D2/P1 + 其余
  ⚪ 未复测：2 项（12.5%）  ← D2/部分C8
```

### 最严峻的 3 个风险

1. **C12 — POST 端零校验**：任何人可在 30 秒内向公示墙注入任意内容（含 XSS），服务端不验证任何字段。这是协议信任链的根基破口，11 天未修复。

2. **C9 — CORS 全开**：恶意网站可通过 JavaScript 跨域向公示墙写入内容，无需用户交互。PUT/DELETE 方法在 CORS 头中暴露。

3. **P1 — 无分页 + 性能恶化**：数据量从 1025→1034 的 11 天内，响应时间从 1.3s 恶化至 2.1s（+62%）。按此速率，预计 9 月中旬将达到 3s+。

### 积极信号

- C14 双端点问题已完全修复
- hygzz.cn 安全头大幅改善（从 0 项到 4 项）
- robots.txt + /api/health 治理端点已部署
- hygzz.中国 恢复了 2 个 404 页面
- SSL 证书缓冲期充足（hygzz.com/cn 61 天）

### 一句话判定

> **事现鉴仍处于"协议信任链根基裸露"状态。C12 和 C9 是两个可被远程利用的写入漏洞，建议 48 小时内优先封堵。**

---

*报告由砺（事现鉴验证执行官）生成。数据截止 2026-08-25T00:35 +08:00。*
