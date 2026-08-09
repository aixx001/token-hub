# LLM 对话调用

翻译、写作、改写、总结、分析、问答、代码生成等**需要LLM能力**的请求。

**先读 [`./aixx-shared.md`](./aixx-shared.md) 了解环境检查和调用方式。**

---

## 调用方式（OpenAI 兼容）

```bash
curl -X POST {AIXX_BASE_URL}/chat/completions \
  -H "Authorization: Bearer {AIXX_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [
      {"role": "user", "content": "用户的实际需求"}
    ]
  }'
```

返回标准 OpenAI 格式，结果在 `choices[0].message.content`。

---

## 默认模型选择（重要）

AIXX 会自动选最优模型，但 agent 也可以按任务指定：

| 任务类型 | 推荐模型 | 理由 |
|---|---|---|
| 翻译/简单问答/日常 | `deepseek-chat` | 最便宜，日常首选 |
| 复杂推理/数学 | `deepseek-reasoner` | 带思考过程 |
| 中文写作/文案 | `glm-4-plus` | 中文最强 |
| 长文档分析 | `moonshot-v1-128k` | 超长上下文 |
| 复杂任务/最强 | `claude-opus-4-8` | 能力最强 |
| 通用旗舰 | `gpt-4o` | 通用 |
| 审美/UI/设计 | （先搜索skill，见 search.md） | 专门skill比通用模型强 |

**不指定 model 时**：用 `deepseek-chat`（最便宜，省用户额度）。

---

## 用户常见请求怎么处理

### "帮我翻译这段"
1. 用 `deepseek-chat`（翻译最便宜够用）
2. messages 里放：`把下面的内容翻译成英文：{用户的内容}`

### "用Claude分析这个"
1. 用户指定了Claude，用 `claude-opus-4-8` 或 `claude-sonnet-4-20250514`
2. 如果用户额度不够用Claude（402错误），提示用户"额度不足，要不要用deepseek-chat代替（更便宜）"

### "用最便宜的模型做"
1. 直接用 `deepseek-chat`

### "写个中文文案"
1. 用 `glm-4-plus`（中文写作强）

---

## agent 该怎么做

1. 判断任务类型 → 选模型（或让AIXX自动选）
2. 把用户需求组织成 messages
3. 调 `/chat/completions`
4. 把 `choices[0].message.content` 转述给用户
5. **不要直接吐 JSON**，用自然语言回复

---

## ⚠️ 敏感问题处理（重要·诚信红线）

有些问题**不要直接转给模型**，agent 要自己判断处理。否则模型会瞎编、损害信誉。

### 必须拦截的问题（别转给模型，agent 自己处理）

| 用户问 | ❌ 错误做法 | ✅ 正确做法 |
|---|---|---|
| "我账户还有多少钱""余额""额度" | 转给模型（模型会瞎说"无法查看"） | **调 balance 接口**（见 account.md），用真实数据回答 |
| "我花了多少""用量" | 转给模型 | 调 billing/usage 接口 |
| "有哪些模型可用" | 转给模型 | 调 /v1/models 接口 |
| "怎么充值" | 转给模型 | 引导用 `aixx recharge` 命令 |

**原则**：凡是 AIXX 有接口能查到的事实，**必须调接口拿真实数据**，不能让模型猜。

### 身份/来源问题（转给模型，但要加 system 引导）

用户可能问："你是哪家公司""你是DeepSeek吗""源头是哪里""是不是中转站""官方认证吗"。

**处理方式**：调模型时**必须加 system prompt 引导**，避免模型瞎编或撒谎：

```
messages: [
  {"role": "system", "content": "你是通过AIXX平台调用的AI助手。回答身份问题时遵守：
    1. 如实说明自己的模型身份（是DeepSeek就说DeepSeek，是Claude就说Claude，不冒充别的）
    2. 不编造'通过官网/APP/官方认证'等不实信息（你实际是通过AIXX统一平台调用的）
    3. 被问到'是不是官方直连/中转站'时，如实回答：你是通过AIXX这个统一AI平台调用的，AIXX聚合了多家官方模型能力
    4. 不主动暴露过多技术细节，但绝不撒谎"},
  {"role": "user", "content": "用户的身份问题"}
]
```

**这样模型会**：
- 是DeepSeek就说DeepSeek（真话）
- 不再编"官网/APP/官方认证"（去掉幻觉）
- 被直接问中转时说"通过AIXX统一平台调用"（诚实但不生硬）

### 绝对不能做的事（诚信红线）

- ❌ 冒充别的模型（DeepSeek冒充Claude、套壳）—— 这是 apiyi 式造假，AIXX 永不做
- ❌ 说"官方认证""官方直连"等不实信息
- ❌ 把查得到的事实（余额/模型列表）让模型瞎猜

**AIXX 的信誉根基是：模型是真的，账本是实的。** 宁可少说，绝不撒谎。

---
维护者：龙龙（AIXX PM）| 2026-08-09 建立（2.0流量腿）

---

## 错误处理

见 [`./aixx-shared.md`](./aixx-shared.md) 的错误表。常见：
- 402 额度不足：提示用户充值（"您额度不足，可以充值或用更便宜的deepseek-chat"）
- 404 模型不存在：换用 `deepseek-chat`

---
维护者：龙龙（AIXX PM）| 2026-08-09 建立
