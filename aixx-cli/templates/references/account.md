# 账户管理

查询用量、余额、花费。

---

## 查余额

```bash
curl {AIXX_BASE_URL}/dashboard/billing/subscription \
  -H "Authorization: Bearer {AIXX_API_KEY}"
```

返回 JSON 含 `hard_limit_usd`（总额度）等信息。

## 查用量

```bash
curl "{AIXX_BASE_URL}/dashboard/billing/usage?start_date=2026-01-01&end_date=2026-12-31" \
  -H "Authorization: Bearer {AIXX_API_KEY}"
```

## 查可用模型列表

```bash
curl {AIXX_BASE_URL}/models \
  -H "Authorization: Bearer {AIXX_API_KEY}"
```

返回所有可调用的模型。

## 用户问"我花了多少"

agent 应该：
1. 调 billing/usage 接口
2. 把结果转述成自然语言："您本月已使用 X 元，剩余 Y 元"
3. 不要直接吐 JSON

## 用户问"还剩多少额度"

调 billing/subscription，告诉用户剩余额度。

---
维护者：龙龙（AIXX PM）| 2026-08-08
