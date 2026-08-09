# AIXX 项目健康清单（HEALTH_CHECKLIST）

> 持续维护，每次开工读，收尾更新。
> 维护者：龙龙 | 2026-08-08 建立 | 2026-08-09 会话8更新

---

## 项目整体状态：🟢 健康（1.0闭环已通，渠道扩展中）

- ✅ 定位清晰（AIXX = AI能力账户/AI的谷歌，三层架构，终极AI银行）
- ✅ 1.0核心闭环已通（注册→充值→调模型→计费）
- ✅ 渠道层完整且验真（11渠道，详见下方）
- ✅ CLI发布npm（aixxai@1.1.0，含质检修复）
- ✅ bot团队3个在岗（sentinel巡查+告警 / integrator接入 / dispatcher咨询）
- ✅ 收款双通道（Creem信用卡 + BEpusdt USDT，都部署完）
- ✅ 主备切换机制（derouter主/ithinkai备，故障自动切，实测通过）
- ⏳ 告警系统已上线但有3bug待修（sentinel已停，见坑4）
- ⏳ 豆包全家桶待接入（对话必成，生图/视频需验证New-API支持）
- ⏳ K哥还没亲自体验过install

---

## 渠道现状（11个，截至2026-08-09）

| id | 渠道 | 类型 | 状态 | 角色 |
|---|---|---|---|---|
| 1 | DeepSeek官方 | OpenAI | ✅启用 | 主力国产 |
| 2 | GLM智谱官方 | OpenAI | ✅启用 | 主力国产 |
| 3 | Kimi官方 | OpenAI | ✅启用 | 主力国产 |
| 4 | MiniMax官方 | OpenAI | ✅启用 | 主力国产 |
| 7 | Grok-xai官方 | xAI | ⚠️挂了(HTTP500) | 待禁用，用ithinkai的grok-4.5替代 |
| 10 | apiyi-GPT | OpenAI | ❌禁用 | 造假，永久pass |
| 11 | apiyi-Claude | Anthropic | ❌禁用 | 造假，永久pass |
| 12 | 硅基流动 | OpenAI | ✅启用 | 聚合，DeepSeek备选 |
| 13 | derouter-Claude | Anthropic | ✅启用 priority10 | Claude主 |
| 14 | derouter-GPT | OpenAI | ✅启用 priority10 | GPT主 |
| 15 | ithinkai-Claude | Anthropic | ✅启用 priority1 | Claude备胎 |
| 16 | ithinkai-GPT | OpenAI | ✅启用 priority1 | GPT备胎 |

**待接入**：火山方舟-豆包对话/生图（key已测通）、ithinkai的grok-4.5（替代官方坏Grok）

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
| 告警系统3bug | 🔴 待修 | 误报敏感/重复发2次/超额狂发。sentinel已停，修完才重启 |
| derouter/ithinkai共享号池风险 | 🟡 关注 | 都可能转售同一上游，注意余额/可用性，多渠道兜底 |
| Grok官方渠道挂掉 | 🟡 待处理 | id=7一直HTTP500，需禁用+接ithinkai grok-4.5替代 |
| 豆包视频2.0+需充值 | 🟢 已知 | 1.0系列可用，2.0/2.5需账户余额≥200元 |
| Anthropic自己做调度层 | 🟡 关注 | 可能性低(20-25%)，12-18个月窗口 |
| KOL分销二开New-API | ⏳ 待开发 | 归因服务+永久分润，需Python微服务 |

## ⚠️ 已知事故
| 事故 | 时间 | 影响 | 状态 |
|---|---|---|---|
| 强改ZCode setting.json导致崩溃 | 2026-08-09 | ZCode任务/项目丢失，K哥找客服恢复 | 已修复+坑1 |
| apiyi造假(Claude套DeepSeek) | 2026-08-09 | 用户花Claude钱买DeepSeek | apiyi已pass+坑2 |
| sentinel session堆积挤爆root | 2026-08-09 | K哥无法登录后台 | 已修复(token缓存+清理)+坑3 |
| 告警系统微信轰炸 | 2026-08-09 | 骚扰K哥，超Server酱额度 | 已止血(sentinel停)+坑4待修 |

## 服务器关键信息
- 服务器：14.103.27.195
- SSH：`ssh -i ~/.ssh/aixx_key aixx@14.103.27.195`（aixx用户）/ root@（需密码）
- root密码：`Aixx@2026!K8`
- 数据库：`/opt/aixx/new-api/one-api.db`（SQLite）
- New-API地址：http://14.103.27.195:8080
- BEpusdt管理：http://14.103.27.195:8000/e1cfe22e46
- 凭证文件：`.env.aixx`（不进git，含所有key）
