# Token中转站 时间线（TIMELINE）

> PM上岗第一个读的，30秒扫完知道最近发生了什么。
> 维护者：龙龙 | 2026-08-08 建立

---

## 🚀 下窗口第一件事（最新·失忆龙龙从这里开始）

> **2026-08-09 会话7接续点·质检复盘完成+调度bot上线。等K哥给钱包私钥部署USDT收款。**

### 醒来第一件事
1. 读 `PRODUCT_VISION.md`（知道建什么——AIXX）
2. 读本文档（知道刚发生什么）
3. 读 `积木块地图.md`（架构）
4. 说暗号「K哥儿，龙龙回来了」+ 主动汇报

### 本轮接续点（等K哥）
- [ ] **K哥给TRON钱包私钥** → 龙龙部署USDT收款（BEpusdt）
- [ ] K哥体验一次 `npx aixx-cli install`（还没体验过）
- [ ] K哥配Creem提现方式（Alipay）
- [ ] 服务器环境变量AIXX_ADMIN_PASS已配到systemd（admin.sh本地用要export）

### 昨天完成的（会话6，2026-08-08深夜）
- ✅ 调度bot上线（走PM流程：开发→质检→修改→部署）
- ✅ 质检复盘完成（CLI+哨兵+接入+admin全部走质检，修复7个必改项）
- ✅ CLI 0.3.0发布（含质检修复）
- ✅ 硅基流动渠道接入
- ✅ Claude/GPT/Grok调通

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
