# AIXX 快速开始

**30秒完成配置，立刻用AI调用万物。**

---

## 前置条件

你需要一个 AIXX API Key。如果还没有：
1. 访问 AIXX 平台注册
2. 充值后获取 API Key（格式：`sk-xxxxx`）

## 配置方式（三选一）

### 方式1：环境变量（推荐，最干净）

> ⚠️ **安全警告**：当前后端用 HTTP 明文传输，存在凭据被嗅探风险。
> TODO（安全）：后端配置好 HTTPS 证书后，请把下方 URL 改为 `https://14.103.27.195:8080/v1`。

在你的 agent 配置中设置两个环境变量：

```bash
export AIXX_API_KEY="sk-你的key"
export AIXX_BASE_URL="http://14.103.27.195:8080/v1"
```

Windows (PowerShell)：
```powershell
$env:AIXX_API_KEY="sk-你的key"
$env:AIXX_BASE_URL="http://14.103.27.195:8080/v1"
```

### 方式2：OpenAI兼容配置

AIXX 兼容 OpenAI 接口。在支持 OpenAI 格式的工具中：

```
API Base URL: http://14.103.27.195:8080/v1
API Key: sk-你的key
Model: deepseek-chat（或其他模型名）
```

### 方式3：直接在代码里用

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-你的key",
    base_url="http://14.103.27.195:8080/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: "sk-你的key",
  baseURL: "http://14.103.27.195:8080/v1",
});

const response = await client.chat.completions.create({
  model: "deepseek-chat",
  messages: [{ role: "user", content: "你好" }],
});
console.log(response.choices[0].message.content);
```

## 验证配置

配置完后，让你的 agent 说一句：
> "帮我用 deepseek-chat 翻译：Hello World"

如果返回中文翻译，说明配置成功。

## 下一步

- 查看 [`./SKILL.md`](./SKILL.md) 了解完整能力
- 查看 [`./references/chat.md`](./references/chat.md) 了解调用细节
- 查看 [`./references/account.md`](./references/account.md) 查询用量

## 常见问题

**Q: 报错 "Unauthorized"**
A: API Key 不对，检查是否完整复制（含 `sk-` 前缀）。

**Q: 报错 "insufficient quota"**
A: 额度不足，需要充值。

**Q: 报错 "model price not configured"**
A: 该模型未配置价格，联系管理员或换用 deepseek-chat。

---
维护者：龙龙（AIXX PM）| 2026-08-08
