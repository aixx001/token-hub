# AIXX 重构待办（REFACTOR_BACKLOG）

> 每次开工扫一眼，收尾时更新。
> 维护者：龙龙 | 2026-08-08 建立 | 2026-08-09 会话8更新

---

| 状态 | 问题 | 优先级 | 备注 |
|---|---|---|---|
| 🔴 待修 | 告警系统3bug：①故障告警太敏感(偶尔超时就报,应连续3次)②log双写导致告警发2次③超额后收到Server酱400还狂重试 | 高 | sentinel已停,修完才重启。见坑4 |
| 🔴 待修 | Grok官方渠道(id=7)一直HTTP500挂掉,需禁用+接ithinkai grok-4.5 | 高 | 待办 |
| 🟡 待做 | 接入豆包全家桶：对话(必成)/生图(需验证New-API支持)/视频(异步任务可能不支持) | 高 | 火山方舟key已测通 |
| 🟡 待做 | 接入ithinkai的grok-4.5/MiniMax-M2.7(比现有版本新) | 中 | 升级机会 |
| 🟡 待做 | 优化skill"代调"模式(install后引导用户手动选AIXX供应商) | 中 | 零配置体验闭环 |
| 🟡 优化 | sentinel日志双写：print(被systemd捕获)+写文件,导致每条日志重复2次 | 中 | 不影响功能,但告警逻辑受影响(坑4) |
| 🟡 优化 | systemd unit里明文密码(AIXX_ADMIN_PASS),建议改EnvironmentFile指向600权限文件 | 低 | 安全优化 |
| 🟢 已知 | .env.aixx不进git,跨设备(PC/Mac)交接需手动传凭证文件 | 低 | 安全vs便利的权衡 |
| 🟢 已知 | ZCode残留备份文件 ~/.zcode/v2/setting.json.bak.aixx* | 低 | 坑1事故遗留,可选清理 |

---
