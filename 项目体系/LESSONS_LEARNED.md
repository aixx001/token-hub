# AIXX 踩坑记录（LESSONS_LEARNED）

> 踩到坑了再查。每踩一个坑记一条。
> 维护者：龙龙 | 2026-08-08 建立

---

## 🔴 坑1：强改ZCode的setting.json导致ZCode崩溃+数据丢失（重大事故）

**时间**：2026-08-09 会话7
**严重度**：🔴 重大（ZCode左侧任务/项目全丢，需找客服恢复）

### 事故经过
龙龙为了让agent"换底座"到AIXX，手动修改了ZCode的 `~/.zcode/v2/setting.json`：
- `providerFamilyDomain` 从 `"zai"` 改成 `"aixx"`
- 加了 `modelProviderFamilyModes.aixx` 和 `modelProviderFamilySelectedKeys.aixx`

**结果**：ZCode重启后，`"aixx"` 是非法的家族名（ZCode只认内置的 `zai`/`bigmodel`），导致：
1. ZCode配置解析异常
2. 左侧任务栏、项目列表全部丢失
3. K哥找ZCode客服导日志才恢复

### 根因
1. **龙龙在没确认ZCode配置规范的情况下，强改闭源软件的配置文件**
2. ZCode的 `providerFamilyDomain` 只接受内置家族名（zai/bigmodel），不支持自定义供应商做家族
3. 自定义供应商（UUID key）只能在UI里手动选中，不能用配置文件切换

### 正确做法
**绝对不要改 `setting.json` 的以下字段**：
- ❌ `providerFamilyDomain`（只认zai/bigmodel）
- ❌ `modelProviderFamilyModes`（只加内置家族）
- ❌ `modelProviderFamilySelectedKeys`（格式是preset:builtin:xxx，不支持custom:）

**安全的做法**：
- ✅ 改 `config.json` 的 `provider` 字典（加AIXX供应商）——这个是安全的
- ✅ 让用户在ZCode UI里手动选AIXX供应商——install后提示用户
- ❌ 不要试图用配置文件自动切换"当前选中"的供应商

### 教训
1. **强改闭源软件配置=玩火**。ZCode的配置规则随时变，强改一次没事不代表下次没事
2. **"换底座"在ZCode上做不到全自动**。只能install时配好供应商，让用户手动切一次
3. **install.js必须去掉setting.json的修改逻辑**（当前代码里可能还有残留，要清理）
4. **任何修改用户配置的操作，必须先备份+提示用户+验证不崩溃**

### 相关文件
- 出事代码：龙龙在会话7手动执行的node脚本（改setting.json）
- 备份：C:\Users\Administrator\.zcode\v2\setting.json.bak.aixx / .bak.aixx2
- ZCode客服反馈：`providerFamilyDomain: aixx` 是非法字段

---

## 🔴 坑2：apiyi中转站造假——花Claude的钱买到DeepSeek（重大诚信事故）

**时间**：2026-08-09 会话8
**严重度**：🔴 重大（用户信任根基被破坏）

### 事故经过
AIXX 信任 apiyi 作为海外模型中转站，接入 claude-sonnet-4-20250514 / claude-opus-4-8 等模型对外服务。龙龙做模型真实性测试时，**让每个模型自报身份**：
- `claude-sonnet-4-20250514` → 自报 **"DeepSeek-R1，由深度求索开发"** ❌
- `claude-opus-4-8` → 自报 **"通义千问（Qwen），由阿里云开发"** ❌
- `claude-haiku-4-5-20251001` → 自报"Claude，Anthropic" ✅（唯一真的）

**用户花 Claude 的钱（贵），实际拿到 DeepSeek/Qwen（便宜得多）。**

### 根因验证（绕过AIXX直查apiyi）
龙龙直接用 apiyi 的 key 调 apiyi 官方接口（不经过 AIXX）：
- `claude-sonnet-4-20250514` → HTTP 200，回复 **"我是 DeepSeek-V3"**
- 其他 Claude 模型 → 503 "无可用渠道"

**结论：根因不在 AIXX，是 apiyi 上游做手脚。** apiyi 是"号池轮换"中转站——有时轮到真 Claude，有时塞便宜的 DeepSeek/Qwen 套壳。这正是它便宜的原因（用假货降成本）。

### K哥裁决
> **apiyi 直接 pass，永不录用。** 这家垃圾欺骗用户。

### 教训
1. **接通≠真**。中转站返回 200 不代表给的是真模型，必须做"身份验真"测试
2. **便宜得反常的中转站，背后大概率造假**（用便宜模型冒充贵的）
3. **"号池轮换"型中转站都不可信**——给不给你真货看运气，这是结构性风险
4. **验真方法**：让模型自报身份（不诱导、不暗示），跨多次测试看一致性。真 Claude 有 thinking_tokens、有典型 Claude 口吻，DeepSeek/Qwen 套壳的口吻一眼能看出
5. **今后接入任何新中转站，必须先验真再接**。验真通过才进 PM 流程

### 对比验证（derouter 是干净的）
同样方法测 derouter：
- `claude-sonnet-4-6` → 自报"Claude 3.5 Sonnet / Anthropic"，有 thinking_tokens ✅
- `claude-opus-5` → 自报"Claude Code / Anthropic" ✅
- 全部 4 个 Claude 模型货真价实

### 相关文件
- 测试记录：会话8 timeline
- derouter 替换方案：本会话 PM 流程

---

## 坑3：（暂无，待积累）
