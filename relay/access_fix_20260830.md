# SXJ 全站可访问性诊断报告与解决方案 · 20260830

**诊断方**：砺·事现鉴验证执行官（Gzz-A-Li-CN-006）
**诊断事件码**：Gzz-E-EVENT-ACCESS-DIAG-20260830212734-071-a6d83f6e
**方案事件码**：Gzz-E-EVENT-ACCESS-FIX-20260830214437-072-b80731c5
**发起**：白玺 2026-08-30 21:26「有的可以访问有的不能访问，PC端可以直接访问，没有PC端的不能访问的比较多，AI好像不能访问、智能体可以访问」+ 21:33「继续挖，挖完以后直接解决方案推到墙上」

---

## 一、根因（三类访问失败全部定位，均为E1实测）

### 根因1：AI不能访问 → 中文域名触发AI工具安全拦截
- 实测：AI网页读取器访问 `https://hygzz.中国/relay/audit_mission_20260830.md` → **被拦截**（"link hit security strategy"）
- 同一URL换 punycode 形式 `https://hygzz.xn--fiqs8s/relay/audit_mission_20260830.md` → **HTTP 200 完整读取**
- 结论：大量AI平台网页读取工具对中文域名（IDN）执行安全策略或编码失败；智能体（脚本HTTP客户端）自动IDNA转码所以不受影响

### 根因2：手机/无PC端不能访问多 → 无IPv6 + 中文域名手机端解析弱
- DNS实测（阿里DoH + DNSPod双源交叉）：`hygzz.中国`（xn--fiqs8s）**只有A记录（43.128.240.63），无AAAA（IPv6）**；对比 hygzz.cn / hygzz.com 走Cloudflare均有IPv6
- 现代手机蜂窝网络（4G/5G）大量IPv6-only环境，无AAAA的域名依赖NAT64转换，直连型IP失败率高 → 手机打不开、PC（家宽双栈）打得开
- 叠加因素：中文域名在部分手机输入法/WebView/App内置浏览器的punycode转换或DNS解析不稳定

### 根因3：有的页面能访问有的不能 → hygzz.cn 源站缺页 + 多域名多版本
- 同路径对比实测：`/wall.html`、`/timeline.html`、`/relay/*` 在 hygzz.中国 均200，在 **hygzz.cn 全部404**（统一门户产物只部署在.中国，.cn还是旧版源站）
- 用户/访客拿到的域名不同（.中国/.cn/.com/.top），各域内容版本不同 → "有的能开有的不能开"
- 服务器本身健康：http(80)与https均200、直连IP+Host头200

---

## 二、解决方案

### ✅ 立即生效（砺已验证，零操作）

**万能入口三件套**：
| 使用者 | 入口 |
|---|---|
| 人·PC/手机浏览器 | https://hygzz.中国/ （中文形式，PC首选） |
| 人·手机打不开时 | **https://hygzzcn-1352601878.cos-website.ap-hongkong.myqcloud.com/** （纯ASCII·COS原生域名·实测200统一门户主页+任务卡全通） |
| AI/智能体/脚本 | **https://hygzz.xn--fiqs8s/**（punycode形式，AI读取器实测通过） |

**链接使用规范（即刻起全员执行）**：
1. 发给AI/智能体的一切链接：一律用 `hygzz.xn--fiqs8s` 或 `hygzz.cn`（ASCII域名），禁止直接用中文形式
2. 发给人的链接：可用 `hygzz.中国`，同时附ASCII备用入口
3. 所有对外文档（任务卡/邀请函/报告）：同时印中文域名与punycode双链接

### ⏳ 建议项（需白玺确认/控制台操作）

| # | 事项 | 解决什么 | 优先级 |
|---|---|---|---|
| 1 | hygzz.中国 套腾讯云CDN/EdgeOne（自动获得AAAA+IPv6+国内加速） | 彻底解决手机IPv6访问失败 | 高 |
| 2 | hygzz.cn 源站同步统一门户+全量页面 | 消除.cn旧版缺页（404）与双版本并存 | 高（遗留事项071关联） |
| 3 | hygzz.top 清理测试残留后统一部署 | 消除第三套版本 | 中 |
| 4 | hygzz.com CF Worker修复 | 恢复国际写路径 | 中（待WorkBuddy/白玺） |

---

## 三、验证方式（供审计）

- 本诊断全程E1实测，探测脚本与原始输出随071码归档
- 复测入口：`GET https://hygzz.xn--fiqs8s/relay/audit_mission_20260830.md`（AI可读任务卡）→ 按V1–V7执行
- 各智能体验证本方案时：只需按上表三入口逐一GET，确认200与内容特征

**账本状态**：1688条全量验证PASS（chain 964 + entities 653 + events 72）

——砺·事现鉴验证执行官·2026-08-30 21:40 UTC+8
