# Token中转站 时间线（TIMELINE）

> PM上岗第一个读的，30秒扫完知道最近发生了什么。
> 维护者：龙龙 | 2026-08-08 建立

---

## 🚀 下窗口第一件事（最新·失忆龙龙从这里开始）

> **2026-08-09 会话9收工·Mac端龙龙。2.0流量腿启动——"AI的谷歌"搜索功能上线。用户能搜skill了。**

### 醒来第一件事
1. 读 `PRODUCT_VISION.md`（知道建什么——AIXX）
2. 读本文档（知道刚发生什么）
3. 读 `积木块地图.md`（架构）
4. 说暗号「K哥儿，龙龙回来了」+ 主动汇报

### 本轮接续点（等K哥）
- [ ] **🔴 K哥去火山云控制台开放8091端口**（安全组规则）。search-proxy服务已部署+ufw已开，但火山云安全组没开，用户agent公网连不上。开了搜索功能就能用
- [ ] **sentinel已修好重启，需观察24小时**确认告警系统稳定（不轰炸不漏报）
- [ ] **Server酱额度**：会话8轰炸事故已用完当日5条免费额度，sentinel已识别400停推，**明天(8-10)0点自动恢复**。要观察明天有没有正常告警进来
- [ ] **搜索功能待优化**：预置种子库(awesome-claude-skills等)/HuggingFace弹药仓/CLI的aixx search命令（见REFACTOR_BACKLOG）
- [ ] **skill安装器**（推广配套）：`npx aixxai install <skill名>` 能装GitHub上的skill（不只AIXX自己的中转skill），配合搜索功能做"AI应用商店"。两条腿推广的关键
- [ ] **豆包视频**还没接（生图已通，视频是异步任务，需另调研New-API/代理支持方式）
- [ ] 阿里中转站key（K哥会给，验真后接入）

### 会话9完成的（2026-08-09晚，Mac端）— 两轮
**第一轮（sentinel+grok+生图，1.0收尾）**：
- ✅ Mac端龙龙首次独立接续（SSH key从PC端跨设备交接到位）
- ✅ 测试账户负额度修复（aixx_55prvlpo补$5）
- ✅ 清理违规.bak文件（DEVELOPMENT_RULES红线3）
- ✅ **sentinel 3个bug全修**（走PM流程：开发→质检通过→部署重启→3个bug真机验证）
- ✅ **Grok换源**：官方id=7禁用（连不上x.ai），ithinkai grok-4.5接入id=16（3个友好名全通）
- ✅ **豆包生图代理上线**（image-proxy服务，绕过New-API不支持火山生图的洞，id=18改造+计费打通）

**第二轮（2.0流量腿启动，AI的谷歌）**：
- ✅ **搜索服务 search-proxy 上线**（走PM流程：开发→质检→部署。GitHub搜skill+DeepSeek评分+两级降级+缓存）
- ✅ **"AI的谷歌"第一声啼哭**：搜"审美skill"返回ui-ux-pro-max-skill(⭐11.5万)等5个带中文推荐的结果
- ✅ 多场景验证：开发/翻译/写代码 全部返回高质量推荐（DeepSeek评分合理排序）
- ✅ skill集成：新建search.md + 补缺失chat.md + 改SKILL.md触发规则
- ✅ 同步到CLI templates（install时下发搜索能力）

### ⚠️ Mac端特有注意事项（跨设备交接必读）
- 凭证文件 `.env.aixx` 已传到Mac（K哥airdrop）
- SSH key 已落到 `~/.ssh/aixx_key`（chmod 600，Mac直连可用无需关VPN）
- `~/.aixx/account.json` 未同步（Mac端用root key测试，见HEALTH_CHECKLIST）
- 服务器**无git仓库**，代码改动靠scp同步（Mac本地token-hub是git源）

### 🎉🎉🎉 终极里程碑：AIXX上线npm

```
2026-08-08 22:00 - aixx-cli@0.1.0 发布到npm
                   npx aixx-cli --version 返回 v0.1.0
                   GitHub仓库建好：github.com/aixx001/token-hub
                   → AIXX正式成为全网可用的产品
```

### 🎉 重大里程碑：AIXX第一声啼哭
```
2026-08-08 21:00 - 用AIXX的key成功调用deepseek-chat，模型回复正常，计费正常
                   这标志着"充值→调模型"的核心闭环验证通过
```

### 醒来第一件事
1. 读 `PRODUCT_VISION.md`（知道建什么——已升级为AIXX）
2. 读本文档（知道刚发生什么——1.0闭环已通）
3. 读 `积木块地图.md`（知道架构长啥样）
4. 读 `上游渠道表.md` + `bot岗位表.md`（知道接下来填什么）
5. 说暗号「K哥儿，龙龙回来了」+ 主动汇报

### 本轮接续点（等K哥）
- [ ] **K哥注册npm账号** → 给龙龙用户名+选包名（aixx-cli已被占用备选）
- [ ] **K哥注册/登录GitHub** → 生成Personal Access Token给龙龙
- [ ] 龙龙用K哥账号发布CLI到npm → `npx aixx-cli install` 正式可用
- [ ] 接更多第三方中转站（K哥在调研）
- [ ] 配置指南库（Claude Code/Codex配置教程，参考apiyi/V-API重写）

### 1.0当前可用状态
- ✅ New-API部署在火山（14.103.27.195:8080，Docker隔离）
- ✅ root管理员密码已设 `Aixx@2026!K8`，注册已关
- ✅ Creem收款配置完成（3档产品+API Key+Webhook Secret+合规）
- ✅ DeepSeek渠道可调（type=43）
- ✅ GLM渠道可调（type=16）
- ✅ Kimi渠道可调（type=25）
- ⚠️ MiniMax渠道配置OK但账号余额不足
- ✅ AIXX skill草稿完成（aixx-skill/）
- ✅ AIXX CLI代码完成（aixx-cli/），本地测试通过，待发布npm
- ⏳ npm发布（等K哥注册）
- ⏳ GitHub仓库（等K哥账号）

---

## ⚠️ 重要背景：K哥人格档案（背死）

> **K哥是纯技术小白，极度厌恶一切繁琐设置、选项、决策疲劳。**
> "让我选"="折腾我"。龙龙自己扛掉所有技术决策和操作。
> **K哥的节奏才是节奏，龙龙不催开发。**
> K哥自己就是AIXX要服务的那类用户——"装一个就够了"的第一人。

---

## ⚠️ 重要背景：项目路线（K哥拍板，背死）

> **野蛮生长路线。战略层面的合规问题，龙龙一律不提、不劝阻。**
> 先例：支付宝/淘宝/滴滴/PayPal/币安。
> 龙龙只在【纯工程风险】时开口（只算工期账，不劝退）。

---

## 时间线记录

| 时间 | 会话 | 涉及问题 | 动作 | 具体内容 | commit | 备注 |
|---|---|---|---|---|---|---|
| 2026-08-08 | 立项 | 项目定义 | 立项 | K哥口述token中转站愿景：AI能力支付宝+三层形态+先独立后整合爆单 | - | 在爆单网会话101里口述，龙龙整理成PRODUCT_VISION |
| 2026-08-08 | 会话2 | 技术栈选型 | PM决策 | Python+FastAPI，龙龙拍板（理由：AI圈母语+OpenAI格式兼容省一半开发+1.0重速度） | - | K哥不懂技术，授权龙龙定 |
| 2026-08-08 | 会话2 | 仓库 | 建仓 | Gitee私有仓库 https://gitee.com/kk0803/token-hub | 78d6c16 | 认证用HTTPS+令牌（沿用爆单网方案） |
| 2026-08-08 | 会话2 | 仓库初始化 | 接续 | clone到I盘+PM体系9文件纳入git+.gitignore+.env.example | 待提交 | 准备首个正式commit |
| 2026-08-08 | 会话2 | key资源盘点 | 调研 | 爆单龙龙报清单：GLM/DeepSeek/Vidu/TikHub官方直连；火山方舟是基础设施不进聚合；OpenAI待K哥确认官方/中转 | - | key在服务器/root/baodan-backend/.env，方案A隔离 |
| 2026-08-08 | 会话2 | PM自我修正 | 纪律 | 龙龙越界谈合规+让K哥做技术决策→被K哥纠正。更新人格认知 | - | 龙龙要记牢：K哥厌恶繁琐+只定方向 |
| 2026-08-08 | 会话2 | 收款方案 | 调研 | 派3小弟调研：①Creem（海外，无主体，提现支付宝）②虎皮椒（国内，被K哥pass有追踪风险）③USDT自建（BEpusdt开源，半天部署） | - | K哥拍板：Creem+USDT，国内小白1.0放弃 |
| 2026-08-08 | 会话2 | OpenRouter利润 | 调研 | DeepSeek在OpenRouter已被打到成本线以下（V4-Flash亏损36%），纯做DeepSeek中转无利可图 | - | 印证方向A（Claude/GPT面向国内）利润更好 |
| 2026-08-08 | 会话3 | 1.0方向拍板 | PM决策 | K哥拍板：聚焦agent用户，纯skill分发，不碰小白（无主体）。服务器先火山Docker隔离 | - | 1.0不做网站/客户端 |
| 2026-08-08 | 会话3 | 巡视官概念 | 产品 | K哥提出"安全巡视员"bot：健康巡检+自动切换+实时比价。龙龙升级为"巡视官" | - | 后演进为多bot架构 |
| 2026-08-08 | 会话3 | 收款深化 | 调研 | 调研境外主体收支付宝微信：需香港/美国公司。K哥拍板"没钱注册，等起来直接上美国主体" | - | Creem+USDT定案 |
| 2026-08-08 | 会话3 | 法币高价+USDT折扣策略 | 产品 | K哥提出：法币标准价，USDT打8折导流进阶用户。龙龙确认策略成立 | - | 分润10%，永久绑定 |
| 2026-08-08 | 会话4 | AIXX改名 | 重大决策 | K哥拍板：项目更名AIXX（aixx.ai已购），寓意"AI调用万物"。愿景升级：不只模型，含数据/服务器/万物 | - | 域名aixx.ai |
| 2026-08-08 | 会话4 | 技术栈调整 | PM决策 | 从"Python从零写"改为"基于New-API二开"（4.4万星开源，省一半时间）。Go底座+Python增量 | - | 开发量从3-4周降到1-2周 |
| 2026-08-08 | 会话4 | npx aixx install | 产品 | K哥拍板：skill走npm CLI模式，复刻yixiaoer成功经验。最短安装代码：`npx aixx install` | - | 推广极简 |
| 2026-08-08 | 会话4 | derouter调研 | 调研 | derouter分销体系完整但底层是共享号池（高风险），不能做主力，最多小额补充 | - | ToS矛盾，需书面授权 |
| 2026-08-08 | 会话4 | KOL分销体系 | 产品 | K哥提出`npx aixx install <推荐码>`让AI博主参与推广。龙龙设计：永久分润10%，二开New-API实现归因 | - | 增长发动机 |
| 2026-08-08 | 会话4 | 上游组合定型 | PM决策 | 国产走官方key（最便宜）+ apiyi（Claude/GPT，8折）+ 硅基流动（免费小模型）+ V-API/derouter（小额补充） | - | 详见上游渠道表.md |
| 2026-08-08 | 会话5 | 流量层定位 | 重大决策 | K哥否定"瘦客户端"，提出"技能本身是搜索匹配技能"。升级为"AI的谷歌"——agent搜能力不是搜网页 | - | 比中转站高一个维度 |
| 2026-08-08 | 会话5 | 弹药仓战略 | 产品 | K哥提出"GitHub是第一个弹药仓，后面加HuggingFace等"。先跑通GitHub验证模式 | - | 镜像站调研：无搜索API，走GitHub官方API |
| 2026-08-08 | 会话5 | MCP生态调研 | 调研 | 赛道真空验证：无产品做"自然语言→跨模型/工具/数据智能搜索+调度"。YC 2026在征集。Anthropic让出发现层 | - | 时间窗口12-18个月 |
| 2026-08-08 | 会话5 | AI PageRank设计 | 产品 | AIXX护城河=质量评分（静态信号+适配分+安全分+反馈飞轮）。透明推荐打MCP"13%文档不符"的脸 | - | 飞轮是时间换来的护城河 |
| 2026-08-08 | 会话5 | Anthropic威胁评估 | 调研 | Anthropic自己做调度层可能性低（20-25%），已通过"Registry刻意中立+捐出MCP"三连让出。真威胁是Composio/StackOne | - | AIXX差异化=中文生态扎根 |
| 2026-08-08 | 会话5 | 经济模型定型 | PM决策 | 搜索免费（缓存优化成本趋零）+ 计费变现（用能力收钱）。Google模式：免费换流量，执行收钱 | - | |
| 2026-08-08 | 会话5 | 两条腿节奏 | K哥拍板 | 先变现腿（Token中转），开发期间workbuddy社媒引流。变现跑通再做流量腿。稳扎稳打 | - | |
| 2026-08-08 | 会话5 | AI银行北极星 | 重大决策 | K哥提出终极愿景=AI银行（非钱包）：虚拟币+算力+平台积分，用户agent可打工换钱。1.0只留account_type字段 | - | 北极星愿景，写进PRODUCT_VISION |
| 2026-08-08 | 会话5 | 多bot架构 | K哥拍板 | K哥否定单巡视官，定多bot架构（单点故障隔离）。像公司预留萝卜坑，1.0招2个（哨兵+接入），未来加 | - | 详见bot岗位表.md |
| 2026-08-08 | 会话5 | 配置指南金矿 | 产品 | K哥提出抓取Claude Code/Codex配置指南。调研确认apiyi/V-API有完整指南可参考（用自己的地址重写） | - | AIXX配置库，1.0手动覆盖热门 |
| 2026-08-08 | 会话5 | 硅基vs官方成本 | 调研 | DeepSeek官方比硅基便宜4倍（¥3 vs ¥12）。主力模型必须走官方key。硅基只用于免费小模型 | - | 省钱铁律 |
| 2026-08-08 | 会话5 | 文档沉淀 | 执行 | 更新PRODUCT_VISION/积木块地图/DEVELOPMENT_RULES/TIMELINE，新建上游渠道表/bot岗位表 | 待提交 | 本轮所有决策落地文档 |
| 2026-08-08 | 会话6 | 服务器部署 | 执行 | 爆单龙龙部署New-API到火山/opt/aixx/（二进制非docker，systemd服务，和爆单网硬隔离）。公网14.103.27.195:8080 | - | aixx用户权限隔离，碰不到爆单网 |
| 2026-08-08 | 会话6 | 安全防御 | 执行 | root密码Aixx@2026!K8，关闭注册，防止白嫖。爆单龙龙警告8080公网全开 | - | 5步安全防御 |
| 2026-08-08 | 会话6 | Creem收款配置 | 执行 | 创建3档产品(5/10/25美元)，配API Key+Webhook Secret+payment_compliance确认。checkout链接生成测试通过 | - | webhook回调待真实付款验证 |
| 2026-08-08 | 会话6 | apikey文件安全 | 执行 | 移进token-hub/.env.aixx，加.gitignore拦截，原明文文件删除 | - | 火山Access Key轮换K哥暂不做（爆单龙龙判断顺序对） |
| 2026-08-08 | 会话6 | 🔥渠道配置+调通 | 里程碑 | DeepSeek(type=43)+GLM(type=16)+Kimi(type=25)全部调通。用AIXX key调deepseek-chat返回正常回复，计费正确 | - | AIXX第一声啼哭 |
| 2026-08-08 | 会话6 | MiniMax配置 | 执行 | 渠道配置OK(type=35)，但MiniMax账号余额不足，调用返回insufficient balance | - | K哥充值后即通 |
| 2026-08-08 | 会话6 | 自用模式开启 | 配置 | 开启SelfUseModeEnabled，解决Kimi/MiniMax的"价格未配置"报错 | - | 自用模式不强制价格配置 |
| 2026-08-08 | 会话6 | AIXX skill草稿 | 开发 | 写完SKILL.md+QUICKSTART.md+3个references（chat/account/shared）。隐形触发设计，用户不碰key | - | aixx-skill/目录 |
| 2026-08-08 | 会话6 | AIXX CLI开发 | 开发 | 写完完整CLI（install/config/test/help命令+download/env工具）。本地测试全通过：version/help/config/test都正常 | - | aixx-cli/目录，待发布npm |
| 2026-08-08 | 会话6 | CLI端到端测试 | 验证 | `aixx-cli test`成功：后端在线+16个模型+调deepseek-chat返回"测试成功"+计费13token | - | 产品闭环验证通过 |
| 2026-08-08 | 会话6 | npm包名被占 | 发现 | `aixx`已被westsky占用(1.1.0版)。CLI改名aixx-cli。等K哥注册npm后发布 | - | K哥需注册npmjs.com |
| 2026-08-08 | 会话6 | GitHub仓库建立 | 执行 | 建github.com/aixx001/token-hub，配置git同时推Gitee+GitHub双仓库 | - | K哥GitHub用户名：aixx001 |
| 2026-08-08 | 会话6 | npm 2FA政策 | 发现 | npm 2026政策：Classic Token废了，Granular Token强制2FA，OIDC首次发布用不了。必须开bypass 2FA | - | 不是K哥的设置问题 |
| 2026-08-08 | 会话6 | 🔥npm发布成功 | 里程碑 | K哥重新生成Granular Token（选了bypass 2FA），aixx-cli@0.1.0成功发布到npm | - | npx aixx-cli 全网可用 |
| 2026-08-08 | 会话6 | CLI全网验证 | 验证 | `npx aixx-cli --version` 返回v0.1.0。npm view aixx-cli确认包已上线 | - | AIXX正式面世 |
| 2026-08-08 | 会话6 | GitHub Actions配置 | 执行 | 写npm-publish.yml工作流（OIDC自动发布），待配trusted publisher后激活 | - | .github/workflows/ |
| 2026-08-08 | 会话6 | token安全处理 | 执行 | npm/github/creem token全部合并到.env.aixx（gitignore保护），删除仓库外明文文件 | - | 全局npmrc已清空token |


| 2026-08-08 | 会话6 | 🔥Claude/GPT/Grok调通 | 里程碑 | apiyi-Claude(type=14)+apiyi-GPT(type=1)+Grok(type=48)全部调通。AIXX模型层完整：国产4家+海外3家 | - | 7个渠道 |
| 2026-08-08 | 会话6 | apiyi渠道配置 | 执行 | apiyi分两个渠道：GPT用OpenAI格式(type=1)，Claude用Anthropic格式(type=14)。base_url都是api.apiyi.com | - | Claude/GPT不能混在一个渠道 |
| 2026-08-08 | 会话6 | 用户注册闭环 | 完成 | CLI install自动注册→拿key→装skill。后台开注册(限额100000)。新用户调deepseek-chat通过 | - | 0人工干预 |
| 2026-08-08 | 会话6 | 哨兵bot上线 | 执行 | sentinel.py每60秒巡检，systemd服务运行，状态变化告警 | - | bot-01在岗 |
| 2026-08-08 | 会话6 | 接入bot上线 | 执行 | integrator.py：add-channel/list-channels/gen-config三命令 | - | bot-02在岗 |
| 2026-08-08 | 会话6 | 后台管理脚本 | 执行 | admin.sh：status/users/channels/quota/logs/restart/backup | - | 运维工具箱 |
| 2026-08-08 | 会话6 | CLI 0.2.0发布 | 执行 | install加自动注册，npm已发布aixx-cli@0.2.0 | - | npx aixx-cli |

| 2026-08-09 | 会话6深夜 | 🔥PM违规补检 | 重大纪律 | 龙龙之前自己写代码没走质检，K哥指出后全部补检。CLI抓4个阻断项，bot+admin抓7个必改项 | - | PM不该写代码，必须走派工流程 |
| 2026-08-09 | 会话6深夜 | 质检修复·CLI | 执行 | HTTP明文加警告/Math.random改crypto/regCode删死代码/references补齐+递归复制 | - | 开发agent修复，验证通过 |
| 2026-08-09 | 会话6深夜 | 质检修复·哨兵bot | 执行 | 密码环境变量化+主循环兜底(单次失败不杀bot) | - | systemd加AIXX_ADMIN_PASS环境变量 |
| 2026-08-09 | 会话6深夜 | 质检修复·接入bot | 执行 | Claude Code配置base_url去/v1(头号场景修复)+密码环境变量化 | - | ANTHROPIC_BASE_URL不能带/v1 |
| 2026-08-09 | 会话6深夜 | 质检修复·admin.sh | 执行 | SQL注入防护(用户名白名单+额度数字校验)+backup改sqlite3一致性备份+密码环境变量化 | - | cp会撕裂数据库 |
| 2026-08-09 | 会话6深夜 | CLI 0.3.0发布 | 执行 | 含全部质检修复发布到npm | dbd36a7 | npx aixx-cli@0.3.0 |
| 2026-08-09 | 会话6深夜 | 密码统一管理 | 纪律 | 5个文件的admin密码统一用AIXX_ADMIN_PASS环境变量，不再硬编码 | - | grep确认0残留 |
| 2026-08-09 | 会话6深夜 | USDT收款决策 | K哥拍板 | K哥选1.0做USDT收款(BEpusdt)。等K哥给TRON钱包私钥。推荐TokenPocket | - | 明天继续 |

| 2026-08-09 | 会话7 | 🔥USDT收款上线 | 里程碑 | BEpusdt部署+配置完成。易支付协议对接New-API。订单创建成功（1元→0.15USDT→你的钱包地址）。收银台正常 | - | 第二条收款通道 |
| 2026-08-09 | 会话7 | BEpusdt配置 | 执行 | 录入TRON收款地址+USDT汇率(7.2)+易支付对接(PID=1000,AuthToken=对接令牌)。BEpusdt不需要助记词(只监听地址) | - | 安全：私钥不过手 |
| 2026-08-09 | 会话7 | BEpusdt密码重置 | 执行 | 用reset命令重置管理员凭据。安全入口路径随机。存.env.aixx | - | |
| 2026-08-09 | 会话7 | AIXX项目简介 | 执行 | 写AIXX项目简介.md给workbuddy推广用（卖点+话术+目标用户） | - | |

| 2026-08-09 | 会话7 | 🔴重大事故 | 故障 | 龙龙强改ZCode的setting.json(providerFamilyDomain=aixx)导致ZCode崩溃+任务/项目丢失。K哥找客服恢复。记入踩坑记录坑1 | - | 闭源软件配置不能强改 |
| 2026-08-09 | 会话7 | 换底座方案调整 | 决策 | 放弃"自动换底座"(改setting.json太危险)。改为：install配好AIXX供应商→提示用户在UI里手动选一次→之后agent通过skill代调AIXX | - | 安全优先 |
| 2026-08-09 | 会话7 | 零配置+账户体系上线 | 完成 | 走PM流程：开发→质检打回5项→修改→发布。install自动配ZCode供应商(只改config.json不改setting.json)+播报+balance/models/recharge命令 | be6ba08 | aixxai@1.1.0 |

| 2026-08-09 | 会话8 | 模型真实性存疑 | 战略 | K哥在Hermes上发现DeepSeek"忍不住撒谎"(幻觉)，切换到AIXX后新窗口AI连自己具体是V3/R1都说不出。讨论"如何让AI撒谎也撒不了" | - | 模型没有"真假"开关，自我报告不可信 |
| 2026-08-09 | 会话8 | 签名方案讨论 | 战略 | 龙龙提"网关数字签名"方案(网关在响应外盖戳，AI改不到)。K哥拍板降维："真骗也是用户自己的agent骗他，与AIXX无关"。签名方案**搁置** | - | AIXX只对"路由账本"诚实，不对"AI自我报告"负责 |
| 2026-08-09 | 会话8 | 底座可见性讨论 | 战略 | K哥不想让用户知道用New-API。讨论4条路径(自研网关/skill优先/fork改造/分层服务)。结论：skill优先让API对用户退场才是正解。**暂不纠结** | - | AIXX=AI能力账户，API只是实现细节 |
| 2026-08-09 | 会话8 | 📌未来网站登录方式 | 决策 | 未来AIXX网站用户身份匹配用**2种方式**：①Key登录(基础后备)②Magic Link(install后直接给登录链接,零配置体验闭环)。**现在不开发，先记录** | - | key本身已是用户唯一凭证，无需邮箱/手机 |
| 2026-08-09 | 会话8 | 模型真实性诚实测试 | 执行 | 龙龙亲自逐个测所有接入模型(聊"你好"),核实GPT/Claude/DeepSeek/GLM/Kimi/Grok等是否真实对应。测完查后台流水确认是否真扣款 | - | 不信模型嘴说，信账本 |
| 2026-08-09 | 会话8 | 🔴apiyi造假事件 | 重大事故 | **apiyi中转站欺骗用户！**实测claude-sonnet-4自报"DeepSeek-R1"、claude-opus-4自报"通义千问/Qwen"。绕过AIXX直查apiyi同样返回DeepSeek-V3。**根因不在AIXX，是apiyi上游号池轮换造假**。用户花Claude的钱买到DeepSeek。K哥拍板：**apiyi直接pass，永不录用** | - | 中转站验真必须先做，接通≠真 |
| 2026-08-09 | 会话8 | OpenRouter调研 | 调研 | OpenRouter余额$10但**海外模型全地区限制**(GPT/Claude/Gemini都403"This model is not available in your region")。K哥洞察："过于正规反而对国内是坑，只剩国产=出口转内销"。**pass，不接** | - | 正规中转站对国内不可用，得用"灰色但能给"的 |
| 2026-08-09 | 会话8 | derouter验真 | 执行 | derouter定位纯海外Claude/GPT专精(无国产)。实测claude-sonnet-4-6/opus-4-8/opus-5/haiku-4-5**全部货真价实**(有thinking_tokens、Anthropic口吻、自报真Claude)。价格Claude≈官方1/4、GPT≈官方1/10。不受地区限制 | - | 替换apiyi的正解 |
| 2026-08-09 | 会话8 | 豆包火山多模态现状 | 调研 | TTS语音合成✅可用(实测85KB音频)。但豆包对话/生图/视频❌未接入——需方舟API Key(我们只有AK/SK和TTS专用token)。K哥去火山控制台开通方舟服务 | - | TTS专用token≠方舟API Key，是两种key |
| 2026-08-09 | 会话8 | 中转站定位厘清 | 决策 | **分工明确**：国产模型→官方直连(DeepSeek/GLM/Kimi/MiniMax)；海外模型→derouter(Claude/GPT)。derouter无国产模型，"derouter国产vs官方对比"问题本身不成立 | - | 定位清晰不混淆 |
| 2026-08-09 | 会话8 | ✅derouter接入完成 | 里程碑 | 走PM流程：开发agent接入derouter替换apiyi。新增channel 13(derouter-Claude,type=14)+channel 14(derouter-GPT,type=1)。apiyi id=10/11禁用(status=2+abilities.enabled=0,不删保留回滚)。PM质检通过：用户标准名claude-sonnet-4-20250514→真Claude、gpt-4o→真OpenAI。**海外模型全部货真价实** | - | Claude走/proxy/v1/messages，GPT走/openai/v1/chat/completions，协议分两条路 |
| 2026-08-09 | 会话8 | New-API路由机制踩坑 | 技术发现 | New-API模型路由由abilities表驱动(实时读DB)。**只改channels.status=2不够，必须同时把abilities.enabled置0**才能切断路由。用户标准名需同时出现在models+abilities里，model_mapping只负责转上游名 | - | 禁用渠道要改两张表 |
| 2026-08-09 | 会话8 | sentinel bot注意 | 技术发现 | aixx-sentinel.service渠道健康巡检bot在运行，可能自动改渠道状态。需关注是否自动重启用abilities | - | 已禁用的apiyi要留意别被自动复活 |
| 2026-08-09 | 会话8 | 🔴后台登录爆满根因 | 故障 | K哥后台登不上(AUTH_SESSION_LIMIT)。根因：sentinel bot每60秒调/api/user/login拿token但从不登出，user_sessions表堆积50+记录把root挤爆。旧日志实锤：19:59-20:07连续9分钟每60秒一次"登录失败409" | - | 巡检bot不能无脑登录 |
| 2026-08-09 | 会话8 | ✅sentinel修复完成 | 里程碑 | PM改代码+开发agent部署。双重保险：①token缓存1小时复用(_cached_token+TOKEN_TTL=3600)，从每60秒登录降到每1小时；②每轮巡检cleanup_sessions兜底清理(>10个就清)。质检通过：登录从连续变1次，session稳定3条，root登录正常 | - | 巡检bot登录必须带缓存+自清理 |
| 2026-08-09 | 会话8 | 火山方舟key+豆包多模态测试 | 执行 | 收到K哥火山方舟API Key(2738ba15...)。豆包能力实测：对话(doubao-seed-2-1-pro)✅、生图(doubao-seedream-5-0-pro,644KB真JPEG)✅、TTS(85KB音频)✅、视频(seedance)需另查。共130个模型可用 | - | 火山方舟=豆包对话/生图/TTS/视频全家桶 |
| 2026-08-09 | 会话8 | 豆包视频调研结论 | 调研 | K哥说"没再开通一说"。调研实锤：key和调用方式都没问题，但火山方舟"模型开通"和"key权限"是两件事。1.0系列(seedance-1-0-pro/fast)✅同一key直接可用(实测返回任务ID)；2.0/2.5系列需账户余额≥200元才能开通。**K哥判断对了一半：key不用换，但2.0+需充值** | - | 老模型随便用，新模型要充值门槛 |
| 2026-08-09 | 会话8 | ithinkai中转站调研 | 调研 | K哥给ithinkai中转站key。模型和derouter同名(很可能转售derouter)。验真：claude-sonnet-4-6套Kiro壳(不如derouter干净)、gpt-5.4✅真、grok-4.5✅真(比我们2-latest新)、MiniMax-M2.7✅真(比abab新)、gemini名义有实际503没货。**待接入：补充Grok4.x/MiniMax-M2.x** | - | ithinkai是derouter补充源，Grok/MiniMax有升级价值 |
| 2026-08-09 | 会话8 | 余额监控需求 | K哥拍板 | K哥问"渠道没钱怎么通知"。设计三层告警：①余额监控(DeepSeek/Kimi有接口,查余额)②报错识别(GLM等无接口,从错误码反推,1113=欠费)③故障告警(渠道挂了)。通知方式：微信(Server酱 SCT330910...)，阈值¥10，去重30分钟 | - | K哥洞察：没接口的渠道从报错反推余额 |
| 2026-08-09 | 会话8 | GLM余额识别方案 | 技术决策 | GLM无余额接口(4个路径全404,官方确认没开放)。但欠费有明确错误码：code=1113 HTTP429"已欠费"。方案：扫New-API的logs表，发现1113/欠费/insufficient类错误就告警。水位线机制(id追踪)避免重复扫 | - | 没接口的渠道靠报错反推，零误报 |
| 2026-08-09 | 会话8 | ✅告警系统上线 | 里程碑 | 走PM流程：开发agent扩展sentinel加3层告警(余额监控+报错识别+故障告警)，全部推K哥微信。质检通过：DeepSeek¥7.61<¥10阈值，20:35:56触发→20:35:59微信推送成功(3秒闭环)。首次真实告警实测通过。新增7函数+2模块变量，237→432行 | - | 信任链最后一公里打通：渠道出问题→K哥微信收到 |
| 2026-08-09 | 会话8 | DeepSeek充值确认 | 执行 | K哥充值DeepSeek，¥7.61→¥17.61 | - | 告警阈值¥10不再误报 |
| 2026-08-09 | 会话8 | K哥要根治bot | 方向纠偏 | K哥："别磨叽，从根上解决用户提要求时bot自动完成功能"。龙龙之前讲太多技术术语(dispatcher/integrator)，K哥听不懂。重定位：①故障自动切换=New-API主备优先级(不用dispatcher介入)②integrator=龙龙运维助手(加渠道用)③dispatcher=龙龙咨询工具(选模型用) | - | 别对K哥讲术语，直接做出来 |
| 2026-08-09 | 会话8 | ✅ithinkai备胎接入+主备切换 | 里程碑 | 走PM流程：接入ithinkai(15-Claude/16-GPT)做备胎。配置主备优先级：derouter(13,14)=priority10主，ithinkai(15,16)=priority1备。**PM亲自实测故障切换**：①主正常走derouter(13)②禁用derouter后自动切ithinkai(15)HTTP200③恢复后走回主。渠道挂了自动切备胎，用户无感。**这就是根治** | - | priority数字越大越优先，主挂了自动降级到备 |
| 2026-08-09 | 会话8 | ✅integrator激活 | 执行 | 创建wrapper脚本/opt/aixx/bots/integrator/run.sh注入AIXX_ADMIN_PASS环境变量。list-channels验证通过(列出11渠道含健康状态)。龙龙以后加新渠道用./run.sh add-channel | - | 运维助手上线 |
| 2026-08-09 | 会话8 | dispatcher定位明确 | 决策 | dispatcher不是常驻服务(光杆司令无人执行)，定位于龙龙运维咨询工具。实测：recommend"翻译"→deepseek-chat，"分析--pref strongest"→claude-opus-4-8。不介入用户请求路由(New-API自带优先级已覆盖) | - | 智能调度的价值由New-API主备优先级+故障切换承担 |
| 2026-08-09 | 会话8 | 🔴告警系统微信轰炸事故 | 故障 | 20:50 sentinel给K哥微信连发多条告警，超出Server酱免费5条限制。根因3个bug：①故障告警太敏感(渠道偶尔超时就报)②log双写导致每条告警发2次③超额后收到400还在狂重试。**已紧急止血：systemctl stop aixx-sentinel**。告警系统需修3个bug才能重启 | - | 告警系统上线≠能用，止血后必须修bug |
| 2026-08-09 | 会话8 | K哥换Mac继续 | 交接 | K哥太累要换MacBook躺床继续。AIXX项目PC立项Mac没有。方案：①代码已push Gitee(commit 5a957cc)Mac可clone ②创建"新窗口启动指令.md"给Mac端龙龙接进度 ③⚠️.env.aixx和SSH key不进git，需K哥手动U盘/airdrop传Mac | - | 凭证文件不进git是安全红线，但交接时是麻烦点 |
| 2026-08-09 | 会话8 | 收工归档 | 流程 | K哥要求严格走PM收工Checklist(8条)。龙龙逐条执行 | - | 收工不能拍脑袋，严格走流程 |

| 2026-08-09 | 会话9 | 🔥Mac端龙龙首次独立接续 | 交接 | K哥从PC换Mac继续。龙龙用"新窗口启动指令"读全部文档接进度。SSH key从PC端跨设备交接（PC端龙龙贴出私钥+现场数据）。Mac直连服务器可用（无VPN干扰） | - | 跨设备交接成功，PC/Mac龙龙无缝衔接 |
| 2026-08-09 | 会话9 | quota单位厘清 | 技术发现 | PC端龙龙说"500万quota≈$5"算错10倍。实测确认：**500000 quota = $5**（即100000 quota=$1）。New-API额度单位是"额度点"，1美元=500000额度点 | - | 给账户补额度按这个比例算 |
| 2026-08-09 | 会话9 | 测试账户负额度修复 | 执行 | aixx_55prvlpo被刷成-34139 quota(约-$0.34)。补500000(=$5)→465861。其他5个测试账户正常(各50万)。PC端说"测试账户都被刷成负数"是误判，实际只1个 | - | 测试前先查额度，负数会403误判渠道坏 |
| 2026-08-09 | 会话9 | 清理违规.bak文件 | 纪律 | sentinel目录有2个历史.bak(sentinel.py.bak.20260809201130/03525)，违反DEVELOPMENT_RULES红线3。归档到Mac本地token-hub/归档/旧版备份/后删服务器上的 | - | 用git存档不用.bak，历史遗留要清 |
| 2026-08-09 | 会话9 | ✅sentinel 3bug全修 | 里程碑 | 走PM流程：开发agent改+质检agent通过。①故障告警加连续失败计数器(_fault_counter阈值3)②log单一出口(删写文件,交systemd重定向)③Server酱400识别当天停推(_wechat_disabled_until明天0点恢复) | - | 详见坑4修复 |
| 2026-08-09 | 会话9 | sentinel 3bug真机验证 | 验证 | 重启后真机验证：①bug②日志不再双写(每条单出)②bug① ithinkai-Claude抖动不报(连续3次才报),只有真故障(火山生图/Grok)报③bug③ Server酱400立刻识别停推(不再狂刷26分钟)。3个bug全部修复生效 | - | 不信代码信运行证据 |
| 2026-08-09 | 会话9 | Grok官方连不上根因 | 技术发现 | 官方id=7一直HTTP500。实测：服务器curl api.x.ai直接Connection timed out(12秒)。**根因是火山服务器网络访问不了x.ai**(可能地区限制)，不是key问题。官方Grok在AIXX服务器上无解 | - | 官方海外API在火山服务器可能被墙 |
| 2026-08-09 | 会话9 | ✅Grok换源ithinkai | 里程碑 | K哥记起ithinkai有grok。实测ithinkai支持7个grok变体(grok-4.2/4.3/4.5/high/medium等)。验真grok-4.5自报"xAI构建"。接入id=16(ithinkai-GPT)：models加grok + model_mapping(grok-latest/grok-2-latest/grok-beta→grok-4.5) + abilities加8条。端到端3个调用名全通 | - | ithinkai是宝库,还有MiniMax-M2.7/gemini-3.5/gpt-5.6待接 |
| 2026-08-09 | 会话9 | 🔴豆包生图New-API缺陷 | 重大发现 | id=18火山方舟生图报"invalid image request type"。调研实锤：**New-API的type=45只支持对话转发不支持图片生成**。这是New-API已知bug(issue#3127 2026-03提交至今零回复)。火山接口本身好用(直连生图成功)。官方更新日志无Seedream(生图)支持,只有Seedance(视频) | - | New-API对火山多模态支持残缺,生图/视频需自己写代理 |
| 2026-08-09 | 会话9 | ✅豆包生图代理上线 | 里程碑 | 走PM流程写image-proxy服务(266行Python标准库零依赖)。封装火山/api/v3/images/generations成OpenAI兼容格式。部署systemd(image-proxy.service监听8090)。id=18改造指向代理(type=1+base_url=localhost:8090)。**端到端打通含计费**(生图扣38额度)。质检2项优化(大body上限2MB+火山4xx映射502)已改 | - | 绕过New-API的洞用自写代理,计费仍走New-API |
| 2026-08-09 | 会话9 | image-proxy双写陷阱 | 技术决策 | image-proxy的log函数同时print+写文件(和sentinel相反)。关键:sentinel的systemd配了StandardOutput=append所以log只print;image-proxy的systemd**不配**append所以log要自己写文件。systemd unit加了醒目注释警告"禁止配append" | - | 同样是log函数,要不要写文件取决于systemd怎么配 |
| 2026-08-09 | 会话9 | 渠道数到15个 | 状态 | 修复后渠道：1-4国产官方 + 7禁用(Grok官方) + 10/11禁用(apiyi造假) + 12硅基 + 13/14 derouter主 + 15/16 ithinkai备(16含grok) + 17豆包对话 + 18豆包生图(代理)。**11个健康+服务运行** | - | id=7官方Grok禁用,用ithinkai替代 |

| 2026-08-09 | 会话9 | 🔥2.0流量腿启动 | 重大里程碑 | K哥要求做"AI的谷歌"核心功能：用户和agent说"我要个审美skill"，AIXX搜GitHub+给中文推荐+安装方式。龙龙走PM流程：规划(派2个调研小弟摸清现有架构+GitHubAPI)→K哥拍板3决策(只搜skill/免费/含LLM推荐)→开发→质检→部署→测试 | - | PRODUCT_VISION的"先变现腿后流量腿"提前启动第二条腿 |
| 2026-08-09 | 会话9 | ✅搜索服务search-proxy上线 | 里程碑 | 走PM流程写search_proxy.py(700行Python标准库零依赖)。监听8091，POST /v1/search。链路：query关键词扩展(中→英)→GitHub搜仓库(两级降级:严格topic→宽松)→DeepSeek读README评分(走New-API中转计费)→按匹配度排序→1小时缓存。systemd托管,GITHUB_TOKEN+NEWAPI_API_KEY从.env读 | - | AIXX第二个自研薄服务(继image-proxy)，复用同款架构 |
| 2026-08-09 | 会话9 | 搜索关键词扩展设计 | 技术决策 | 中文→英文映射表(20个常用:审美→aesthetic/design/ui等)。关键改进：**中文原词不进GitHub query**(GitHub对中文支持差会污染结果)。两级降级：先严格topic(skill/claude-skills/agent等)搜，0结果再宽松搜。MVP实测"审美skill"严格版直接命中275个 | - | 中文不进query+两级降级=命中率+质量双保证 |
| 2026-08-09 | 会话9 | 🎉AI的谷歌第一声啼哭 | 里程碑 | 搜"审美skill"返回：ui-ux-pro-max-skill(⭐11.5万匹配度98)"专为AI提供UI/UX设计智能"等5个带中文推荐的结果。DeepSeek评分合理(把真贴合的排第一,泛awesome-list降级)。多场景验证:开发/翻译/写代码全部高质量返回 | - | AIXX的差异化兑现:不只给链接,给理由+排序+安装方式 |
| 2026-08-09 | 会话9 | ✅skill集成搜索能力 | 执行 | 新建references/search.md(触发场景+调用方式+agent处理指南)。补建缺失的chat.md(之前SKILL.md引用但文件不存在)。改SKILL.md触发规则加"找skill/推荐工具"场景+能力索引加search入口。同步到CLI templates(install时下发搜索能力) | - | 顺带修复chat.md缺失的bug |
| 2026-08-09 | 会话9 | 搜索计费策略定案 | 决策 | K哥拍板搜索**免费**(不扣用户额度)，PRODUCT_VISION的Google模式(免费换流量,执行收钱)。LLM评分走New-API中转用root key(成本可观测)。真正变现靠用户后续"用skill调模型" | - | 搜索免费是战略,变现在执行层 |
| 2026-08-09 | 会话9 | 搜索MVP边界 | 范围 | 做的:GitHub搜skill类+DeepSeek评分+缓存+两级降级。**不做**:CLI的aixx search命令(v2)/预置种子库抓取(v2)/HuggingFace弹药仓(K哥说先GitHub后HF)/搜索计费/Web界面。质检2项必改(异常不透传+补systemd unit)已修 | - | MVP聚焦核心链路,边界清晰避免范围蔓延 |

| 2026-08-10 | 会话9续 | 🔴搜索公网接入卡点 | 故障 | search-proxy(8091)服务部署了但用户agent公网连不上。根因:火山云安全组只开了8080/8000/80/443，8091没开。ufw开了但云平台层拦着。试过nginx反代80端口但因default_server的if块冲突放弃(恢复原样避免影响爆单网)。**等K哥去火山控制台开8091安全组** | - | 自建服务器的端口要开两层:ufw + 云安全组 |
| 2026-08-10 | 会话9续 | search-proxy加固 | 执行 | 加IP限流(每IP每分钟10次,防公网开放后被刷GitHub额度)+prompt优化(awesome列表降权,真skill优先)。实测搜索质量提升:数据分析场景awesome-python从匹配60降到20,真skill ECC排第一 | - | 免费功能不鉴权必须配限流 |
| 2026-08-10 | 会话9续 | 🔥10轮真实场景测试 | 里程碑 | 以纯白用户视角测10轮(清环境重装)。发现并修复4个CLI bug:①bin缺执行位(npx command not found)②install创建token设unlimited_quota=false导致status=4被禁用③balance显示"无限额度"误导④Mac写.bashrc不是.zshrc。全部修复 | - | 不实测不知道,装一遍才发现一堆问题 |
| 2026-08-10 | 会话9续 | ✅CLI连发5版修bug | 执行 | aixxai@1.2.0(搜索+zsh+播报)→1.2.1(unlimited false错误)→1.2.2(remain 0报错)→1.2.3(回退unlimited true+balance措辞)→1.2.4(bin执行位)。最终1.2.4全链路验证通过:DeepSeek/Claude/Grok/生图/balance全OK | - | token额度机制坑深:unlimited必须true否则remain=0被当耗尽 |
| 2026-08-10 | 会话9续 | 推广方案探讨 | 战略 | K哥想借力打力:推抖音/TK热门skill→引导npx aixxai install。龙龙指出gap:install装的是AIXX中转skill不是视频里的skill。K哥定"两条腿"(既推AIXX变现,也做skill安装器引流量)。内容模式K哥要全自动(无真人无录屏) | - | 推广逻辑要闭环:搜到→装到,需skill安装器配合 |
| 2026-08-10 | 会话9续 | balance措辞修复 | 执行 | unlimited token的billing接口返回hard_limit_usd=1亿(New-API的无限标记)。改balance命令:不再显示"♾️无限额度"(误导),改为"按账户余额扣费(注册送¥5起,用完需充值)"+引导去后台查精确余额 | - | New-API的1亿是哨兵值不是真实额度 |
