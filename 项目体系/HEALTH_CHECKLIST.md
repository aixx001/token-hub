# AIXX 项目健康清单（HEALTH_CHECKLIST）

> 持续维护，每次开工读，收尾更新。
> 维护者：龙龙 | 2026-08-08 建立 | 2026-08-09 会话8更新

---

## 项目整体状态：🟢 健康（1.0闭环已通，渠道扩展中）

- ✅ 定位清晰（AIXX = AI能力账户/AI的谷歌，三层架构，终极AI银行）
- ✅ 1.0核心闭环已通（注册→充值→调模型→计费）
- ✅ 渠道层完整且验真（15渠道，11个健康，详见下方）
- ✅ CLI发布npm（aixxai@1.1.0，含质检修复）
- ✅ bot团队3个在岗 + 1个代理（sentinel巡查+告警 / integrator接入 / dispatcher咨询 / image-proxy生图代理）
- ✅ 收款双通道（Creem信用卡 + BEpusdt USDT，都部署完）
- ✅ 主备切换机制（derouter主/ithinkai备，故障自动切，实测通过）
- ✅ 告警系统3bug已修（sentinel已重启运行，待24小时观察稳定性）
- ✅ 豆包生图代理上线（image-proxy服务，绕过New-API缺陷，计费打通）
- ⏳ 豆包视频待接（生图已通，视频异步任务需另调研）
- ⏳ K哥还没亲自体验过install

---

## 渠道现状（15个，截至2026-08-09会话9）

| id | 渠道 | 类型 | 状态 | 角色 |
|---|---|---|---|---|
| 1 | DeepSeek官方 | OpenAI | ✅启用 | 主力国产 |
| 2 | GLM智谱官方 | OpenAI | ✅启用 | 主力国产 |
| 3 | Kimi官方 | OpenAI | ✅启用 | 主力国产 |
| 4 | MiniMax官方 | OpenAI | ✅启用 | 主力国产 |
| 7 | Grok-xai官方 | xAI | ❌禁用(连不上x.ai) | 服务器网络访问不了x.ai，用ithinkai替代 |
| 10 | apiyi-GPT | OpenAI | ❌禁用 | 造假，永久pass |
| 11 | apiyi-Claude | Anthropic | ❌禁用 | 造假，永久pass |
| 12 | 硅基流动 | OpenAI | ✅启用 | 聚合，DeepSeek备选 |
| 13 | derouter-Claude | Anthropic | ✅启用 priority10 | Claude主 |
| 14 | derouter-GPT | OpenAI | ✅启用 priority10 | GPT主 |
| 15 | ithinkai-Claude | Anthropic | ✅启用 priority1 | Claude备胎 |
| 16 | ithinkai-GPT | OpenAI | ✅启用 priority1 | GPT备胎 + **grok主力**(grok-4.5等) |
| 17 | 火山方舟-对话 | OpenAI(type45) | ✅启用 | 豆包对话(doubao-seed系列) |
| 18 | 火山方舟-生图 | OpenAI(type1→代理) | ✅启用 | 豆包生图(指向image-proxy:8090) |

**健康渠道11个**，禁用4个（官方Grok + apiyi×2造假 + 豆包生图旧配置已改造）

**ithinkai待挖掘**：MiniMax-M2.7 / gemini-3.5 / gpt-5.6 / veo3.1视频（验真后可接，见REFACTOR_BACKLOG）

---

## 代码冗余
- ZCode残留备份文件：`~/.zcode/v2/setting.json.bak.aixx*`（坑1事故遗留，可选清理）

## skill问题
（AIXX skill待优化"代调"模式，install后引导用户手动选AIXX供应商）

## 废弃文件
- apiyi渠道(10,11)：status=2禁用，保留作记录和回滚（不删）

## 待办风险/关注点

| 项 | 状态 | 说明 |
|---|---|---|
| sentinel告警稳定性 | 🟡 观察 | 3bug已修复重启，需观察24小时确认不轰炸不漏报。Server酱8-10日0点恢复额度 |
| 豆包视频待接 | 🟡 待做 | 生图已通(代理)，视频是异步任务需另调研New-API/代理支持方式 |
| derouter/ithinkai共享号池风险 | 🟡 关注 | 都可能转售同一上游，注意余额/可用性，多渠道兜底 |
| ithinkai宝库待挖 | 🟢 机会 | MiniMax-M2.7/gemini-3.5/gpt-5.6/veo3.1视频 验真后可接 |
| 豆包视频2.0+需充值 | 🟢 已知 | 1.0系列可用，2.0/2.5需账户余额≥200元 |
| Anthropic自己做调度层 | 🟡 关注 | 可能性低(20-25%)，12-18个月窗口 |
| KOL分销二开New-API | ⏳ 待开发 | 归因服务+永久分润，需Python微服务 |

## ⚠️ 已知事故
| 事故 | 时间 | 影响 | 状态 |
|---|---|---|---|
| 强改ZCode setting.json导致崩溃 | 2026-08-09 | ZCode任务/项目丢失，K哥找客服恢复 | 已修复+坑1 |
| apiyi造假(Claude套DeepSeek) | 2026-08-09 | 用户花Claude钱买DeepSeek | apiyi已pass+坑2 |
| sentinel session堆积挤爆root | 2026-08-09 | K哥无法登录后台 | 已修复(token缓存+清理)+坑3 |
| 告警系统微信轰炸 | 2026-08-09 | 骚扰K哥，超Server酱额度 | 已修复(3bug全修+sentinel重启)+坑4 |
| New-API不支持火山生图 | 2026-08-09 | 豆包生图功能受阻 | 已绕过(自写image-proxy代理)+坑5 |

## 服务器关键信息
- 服务器：14.103.27.195
- SSH：`ssh -i ~/.ssh/aixx_key aixx@14.103.27.195`（aixx用户）/ root@（需密码）
- root密码：`Aixx@2026!K8`
- 数据库：`/opt/aixx/new-api/one-api.db`（SQLite）
- New-API地址：http://14.103.27.195:8080
- BEpusdt管理：http://14.103.27.195:8000/e1cfe22e46
- 凭证文件：`.env.aixx`（不进git，含所有key）
