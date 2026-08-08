# LLM 对话调用

翻译、写作、分析、问答、代码等所有需要 LLM 能力的请求。

---

## 调用示例

### 基础调用（用默认模型 deepseek-chat）

```bash
curl -X POST {AIXX_BASE_URL}/chat/completions \
  -H "Authorization: Bearer {AIXX_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "用户的需求"}]
  }'
```

### 指定模型

用户说"用Kimi" → model 用 `moonshot-v1-8k`
用户说"用GLM" → model 用 `glm-4-flash` 或 `glm-4-plus`
用户说"用最便宜的" → model 用 `deepseek-chat`
用户说"用推理强的" → model 用 `deepseek-reasoner`

### 流式输出

```json
{
  "model": "deepseek-chat",
  "messages": [...],
  "stream": true
}
```

## 模型选择建议（agent自动决策）

| 场景 | 推荐模型 | 理由 |
|---|---|---|
| 简短翻译/问答 | deepseek-chat | 最便宜，足够用 |
| 长文档分析 | moonshot-v1-128k | Kimi长文本强 |
| 复杂推理 | deepseek-reasoner | 专门的推理模型 |
| 中文写作 | glm-4-plus | GLM中文表现好 |
| 代码生成 | deepseek-chat | DeepSeek代码能力强 |

## 意图识别

agent 接收到用户消息后，先判断：
1. **是否需要调LLM？** 简单确认/闲聊不用
2. **用哪个模型？** 用户指定就用指定的，没指定就用 deepseek-chat
3. **怎么调？** 标准 OpenAI 格式，AIXX base_url + key

---
维护者：龙龙（AIXX PM）| 2026-08-08
