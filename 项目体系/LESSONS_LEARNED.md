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

## 坑3：sentinel每次巡检都登录，session堆积挤爆root登录

**时间**：2026-08-09 会话8
**严重度**：🔴 重大（K哥无法登录后台运维）

### 事故经过
sentinel bot 每60秒巡检渠道，每次都调 `/api/user/login` 拿新 token，**从不登出**。一天1440次登录，`user_sessions` 表堆积50+记录，触发 New-API 的 AUTH_SESSION_LIMIT，把 root 账号挤爆。K哥登录后台返回 HTTP 409 Conflict，完全进不去。

### 根因
sentinel 的 `run_check()` 函数里 `token = login()`，每次巡检都重新登录。New-API 的 session 有上限（防多设备滥用），登录累积超限就锁死。

### 修复（双重保险）
1. **token 缓存**：`_cached_token` + `TOKEN_TTL=3600`，1小时内复用同一个 token，不再每60秒登录
2. **兜底清理**：每轮巡检 `cleanup_sessions()`，检查 user_sessions 超10个就清空
3. token 失效(401)时自动 `invalidate_token()` 重新登录

### 教训
1. **任何要登录拿 token 的常驻服务，必须复用 token，不能无脑登录**
2. New-API 的 user_sessions 表是堆积型的，不会自动清理过期 session
3. 系统设计要考虑"自己造成的副作用"——bot 自己登录会把自己人(root)锁死
4. **修复后必须观察 session 数量**，确认不再堆积才算真修好

### 相关文件
- 出事代码：`bots/sentinel/sentinel.py` 的 `run_check()`（旧版）
- 修复：同文件，新增 `login()` 缓存逻辑 + `cleanup_sessions()` + `invalidate_token()`

---

## 坑4：告警系统上线即微信轰炸，3个设计bug

**时间**：2026-08-09 会话8
**严重度**：🟡 中（骚扰K哥，超出Server酱免费额度）

### 事故经过
告警系统上线后，20:50 给 K哥 微信连发多条告警（GLM/DeepSeek/Kimi各种报错），超出 Server酱 每天5条免费额度，后续推送全 HTTP 400。

### 3个根因bug
1. **故障告警太敏感**：sentinel ping 渠道偶尔超时（网络抖动）就当成"故障"报警。应该"连续N次失败才报"，不是一次抖动就报
2. **重复发2次**：`log()` 函数同时 print（被systemd捕获）+ 写文件，导致依赖日志的告警逻辑被触发两次，1条变2条
3. **超额狂发**：Server酱返回400（额度用完）后，sentinel 还在每3分钟重试，刷一堆失败日志。应该检测到400就停止当天推送

### 处理
**已紧急止血**：`systemctl stop aixx-sentinel`。告警系统需修完3个bug才能重启。

### 教训
1. **告警系统本身不能成为告警源**——监控工具骚扰用户是严重设计失败
2. **告警去重不仅要按时间，还要按"状态变化"**——渠道抖动一两次不算故障，连续失败才是
3. **第三方限流要识别**：Server酱免费版每天5条，收到400必须停，不能重试
4. **log双写副作用**：函数同时做print和写文件，会让依赖它的逻辑执行两次。告警逻辑不该和log耦合
5. **新功能上线后必须观察一个完整周期**（至少一个告警间隔），不能"上线=完成"

### 待修复（下个会话优先）
- 故障告警加"连续3次失败"门槛
- 告警逻辑剥离log，单独执行
- 识别Server酱400，当天停止推送

### 相关文件
- 出事代码：`bots/sentinel/sentinel.py` 的 `run_fault_alert()` / `push_wechat()`

---

## 🔴 坑5：New-API不支持火山方舟生图——自写代理绕过（架构缺陷）

**时间**：2026-08-09 会话9
**严重度**：🟡 中（豆包生图功能受阻，用自写代理绕过）

### 事故经过
火山方舟生图接口直连完全正常（doubao-seedream-5-0-pro返回真JPEG），但接入New-API配成type=45渠道后，调`/v1/images/generations`报错：
```
invalid image request type
```

### 根因
**New-API的type=45（火山方舟）渠道适配器只实现了对话（chat completions）转发，没实现图片生成（images generations）转发。**

关键证据：
1. 报错"invalid image request type"是**New-API的relay层自己抛的**，不是火山返回的（火山接口直连好用）
2. 这是**已知Bug**：New-API issue #3127「火山方舟豆包生图无法使用」，2026-03-05提交，**零评论零PR零回复**，维护者没理
3. 官方更新日志里火山/Doubao只有Seedance（视频），**没有任何Seedream（生图）支持**
4. 社区有人fork了new-api（ensonz/volc-adapter）专门解决这个，说明官方不修

### 最终解法（自写代理）
不依赖New-API，自己写了个薄代理服务`image-proxy`（`/opt/aixx/bots/image-proxy/image_proxy.py`）：
- 监听8090，接收OpenAI格式`/v1/images/generations`
- 模型名映射（doubao-seedream→火山真实名）
- 转发到火山`/api/v3/images/generations`
- 返回精简的OpenAI格式
- New-API配一个OpenAI兼容渠道（type=1）指向这个代理（id=18），**鉴权和计费仍由New-API负责**

### 教训
1. **New-API对火山方舟多模态支持残缺**：对话能用，但生图/视频等高级接口可能不被relay层支持。接火山多模态要先验证New-API支持，不支持就自写代理
2. **"invalid image request type"这个错误 = New-API不认这种渠道类型支持图片生成**，不是配置问题，别在配置上瞎试
3. **New-API的issue响应慢**：重要功能缺失别等官方修（#3127晾半年），自己写代理绕过最快
4. **自写代理设计要点**：薄转发+模型名映射+错误格式标准化+计费仍交New-API（别在代理里重复造计费）

### 相关文件
- 代理代码：`bots/image-proxy/image_proxy.py`（266行）
- 代理服务：systemd `image-proxy.service`（监听8090）
- New-API渠道：id=18（type=1指向localhost:8090）
- 调研依据：New-API issue #3127 / #2195 / #4705 + 官方更新日志
