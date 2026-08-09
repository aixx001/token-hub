# AIXX 重构待办（REFACTOR_BACKLOG）

> 每次开工扫一眼，收尾时更新。
> 维护者：龙龙 | 2026-08-08 建立 | 2026-08-09 会话8更新

---

| 状态 | 问题 | 优先级 | 备注 |
|---|---|---|---|
| ✅ 已完成 | 告警系统3bug：①故障告警加连续失败计数器②log单出口③Server酱400停推 | 高 | 会话9修完,sentinel已重启,待24h观察 |
| ✅ 已完成 | Grok官方渠道(id=7)禁用+ithinkai grok-4.5接入(id=16,3个友好名) | 高 | 会话9完成,官方连不上x.ai |
| ✅ 已完成 | 豆包生图：自写image-proxy代理绕过New-API缺陷 | 高 | 会话9完成,坑5 |
| 🟡 待做 | 接入豆包视频(seedance)：异步任务,需调研New-API/代理支持方式 | 高 | 生图已通,视频另开任务 |
| 🟡 待做 | 接入ithinkai宝库：MiniMax-M2.7/gemini-3.5/gpt-5.6/veo3.1视频 | 中 | 升级机会,验真后接 |
| 🟡 待做 | 优化skill"代调"模式(install后引导用户手动选AIXX供应商) | 中 | 零配置体验闭环 |
| 🟡 待做 | 阿里中转站key(K哥会给,验真后接入) | 中 | 等K哥 |
| 🟡 优化 | systemd unit里明文密码(AIXX_ADMIN_PASS/image-proxy用EnvironmentFile已示范),建议sentinel也改EnvironmentFile | 低 | 安全优化 |
| 🟡 优化 | image-proxy质检建议3项：③兜底item透传破坏格式④空格prompt绕过⑤火山返回空data时静默 | 低 | 边界情况,触发概率低 |
| 🟢 已知 | .env.aixx不进git,跨设备(PC/Mac)交接需手动传凭证文件 | 低 | 安全vs便利的权衡 |
| 🟢 已知 | ZCode残留备份文件 ~/.zcode/v2/setting.json.bak.aixx* | 低 | 坑1事故遗留,可选清理 |

---
