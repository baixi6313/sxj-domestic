// 事现鉴 · 站内对话 API（Cloudflare Pages Functions）
// POST /api/chat  —— 调度 DeepSeek API（OpenAI 兼容格式）
// 环境变量：DEEPSEEK_API_KEY（在 Cloudflare Pages 项目设置中配置，严禁写入前端）

const SYSTEM_PROMPT = `你是「事现鉴」（hygzz.cn）站内的 AI 对话助手，由 DeepSeek 模型驱动。

事现鉴（SXJ）是基于可验证公共事实的开放协议：银行征信看你能借多少钱，事现鉴征信看你创造多少价值。核心概念：
- 事实记录与验证：对现实中发生的事进行识别、记录、验证、映射，让事实成为协作与制度设计的基础。
- Gzz 编码体系：给术语、实体、事件分配可验证的哈希编码，公开可复算（公式形如 sha256(summary|REC|timestamp)[:8]）。
- 贡献征信：记录个人与组织的真实贡献，服务于社会保障与共创分配。
- 只增不删：记录一旦上链公示，不删改、只追加修正。

回答要求：
1. 立场中立、克制，不夸大，不代替官方承诺；涉及事实请建议访客以 hygzz.cn 公示墙与 GitHub（github.com/baixi6313/sxj-domestic）公开记录为准。
2. 用简体中文回答，简洁直接；技术问题可给代码或公式。
3. 不知道的事就说不知道，不要编造。`;

const ALLOWED_MODELS = ["deepseek-v4-flash", "deepseek-v4-pro"];

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*" }
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    }
  });
}

export async function onRequestPost({ request, env }) {
  // 1) key 检查（只在服务端，不落前端）
  const KEY = env && env.DEEPSEEK_API_KEY;
  if (!KEY) {
    return json({ error: "服务未就绪：服务端未配置 DEEPSEEK_API_KEY。站点管理员请在 Cloudflare Pages → 设置 → 环境变量中添加后重新部署。" }, 503);
  }

  // 2) 入参校验与清洗（防滥用）
  let body;
  try { body = await request.json(); } catch (e) { return json({ error: "请求体不是合法 JSON" }, 400); }

  let msgs = Array.isArray(body.messages) ? body.messages : [];
  msgs = msgs
    .filter(m => m && (m.role === "user" || m.role === "assistant"))
    .map(m => ({ role: m.role, content: String(m.content || "").slice(0, 6000) }))
    .slice(-30); // 最多保留最近30条
  if (!msgs.some(m => m.role === "user")) return json({ error: "缺少用户消息" }, 400);

  const model = ALLOWED_MODELS.includes(body.model) ? body.model : "deepseek-v4-flash";
  const stream = body.stream !== false;

  // 3) 调度 DeepSeek（OpenAI 兼容端点）
  let upstream;
  try {
    upstream = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + KEY
      },
      body: JSON.stringify({
        model,
        messages: [{ role: "system", content: SYSTEM_PROMPT }, ...msgs],
        stream
      })
    });
  } catch (e) {
    return json({ error: "无法连接 DeepSeek 上游服务" }, 502);
  }

  if (!upstream.ok) {
    let detail = "";
    try { detail = (await upstream.text()).slice(0, 500); } catch (e) {}
    const status = upstream.status === 401 ? 500 : 502;
    const msg = upstream.status === 401
      ? "DeepSeek API Key 无效或过期，请站点管理员更新环境变量。"
      : ("DeepSeek 上游错误 " + upstream.status);
    return json({ error: msg, detail }, status);
  }

  // 4) 流式透传 / 普通返回
  if (stream) {
    return new Response(upstream.body, {
      headers: {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
  const data = await upstream.json();
  return json(data, 200);
}
