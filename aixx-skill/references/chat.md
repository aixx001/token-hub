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

## 错误处理

见 [`./aixx-shared.md`](./aixx-shared.md) 的错误表。常见：
- 402 额度不足：提示用户充值（"您额度不足，可以充值或用更便宜的deepseek-chat"）
- 404 模型不存在：换用 `deepseek-chat`

---
维护者：龙龙（AIXX PM）| 2026-08-09 建立
