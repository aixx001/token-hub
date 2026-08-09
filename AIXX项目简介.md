# AIXX 项目简介（给推广团队/workbuddy）

> 这份简介帮你快速理解AIXX是什么，方便你做社媒推广内容。

---

## 一句话

**AIXX = "AI的谷歌"。装一个命令，你的AI助手就能调用全世界的AI能力（DeepSeek/Claude/GPT/GLM/Kimi等），永远不用碰key、参数、文档。**

---

## AIXX解决什么痛点

现在用AI能力是"碎片化地狱"：
- 用DeepSeek要去DeepSeek充值
- 用Claude要去Anthropic充值
- 用GPT要去OpenAI充值
- 每个平台一套key、一套余额、一套参数、一套文档

**对开发者/agent用户来说，这不是用AI，这是被AI折腾。**

AIXX的解法：**一个key，一个命令，调所有AI能力。**

---

## 用户怎么用（极简）

```bash
# 一行命令安装（自动注册拿key）
npx aixx-cli install

# 然后对自己的AI助手说话就行
"帮我翻译这段"        → AIXX自动选最便宜的DeepSeek
"深度分析这个商业计划" → AIXX自动选最强的Claude
"写篇中文文案"        → AIXX自动选中文最好的GLM
```

**用户全程不碰key、不碰参数、不碰文档。** 这是AIXX的核心体验。

---

## AIXX的差异化（为什么不用别的）

| 别人 | AIXX |
|---|---|
| OpenRouter只聚合模型 | AIXX还要聚合数据/工具/开源项目（2.0） |
| 其他中转站要手动选模型 | AIXX自动选最优（价格+健康度+任务匹配） |
| 配置复杂要填一堆参数 | 一行命令安装，隐形使用 |
| 单一渠道挂了就断 | 多渠道自动故障切换 |

---

## 当前能力（1.0，已上线）

**已接入的AI模型（一个key全调）**：

| 类型 | 模型 | 来源 |
|---|---|---|
| 国产便宜 | DeepSeek | 官方直连 |
| 国产中文 | GLM智谱 | 官方直连 |
| 国产长文本 | Kimi月之暗面 | 官方直连 |
| 海外旗舰 | Claude Sonnet/Opus | 中转 |
| 海外通用 | GPT-4o | 中转 |
| 海外新锐 | Grok | x.ai |
| 免费小模型 | 向量/生图/OCR | 硅基流动 |

**收款**：信用卡/Apple Pay（海外），USDT（进阶用户，即将上线）

**智能调度**：用户不指定模型时，AIXX自动选最优（翻译选最便宜，分析选最强，写作选中文最好）

**故障自愈**：某个渠道挂了，自动切到备用渠道，用户无感

---

## 推广卖点（给做内容的人参考）

### 核心卖点（一句话能说清的）
1. **"一个key调所有AI"** —— 不用每个平台单独充值
2. **"装一个就够了"** —— npx一行命令，30秒搞定
3. **"AI自动帮你选模型"** —— 你说需求，它选最便宜/最强的
4. **"省钱"** —— DeepSeek官方价，比官方便宜4倍（相比某些聚合站）

### 适合的推广角度
- **省钱向**：对比各家API价格，AIXX用官方价+自动选最便宜
- **省事向**：对比"配5个平台key" vs "一个npx命令"
- **技术向**：多渠道故障切换、智能调度、开源bot架构
- **未来向**：AIXX不只是中转站，未来是"AI的谷歌"（搜索调度所有AI能力）

### 目标用户
- 用Claude Code/Cursor/ZCode等AI编程工具的开发者
- 有自己AI助手的进阶用户
- 嫌每个平台单独充值麻烦的人

### 推广话术示例
```
你是不是每个AI平台都要单独充值、单独管key？
DeepSeek一个、Claude一个、GPT一个……烦不烦？

AIXX：一个key调所有AI。
npx aixx-cli install，30秒搞定。
你说"翻译"，它自动选最便宜的DeepSeek；
你说"分析"，它自动选最强的Claude。
你永远不用碰key、参数、文档。

装一个就够了。
```

---

## 技术信息（给技术向内容用）

- **安装**：`npx aixx-cli install`
- **GitHub**：https://github.com/aixx001/token-hub
- **Gitee**：https://gitee.com/kk0803/token-hub
- **npm包**：aixx-cli
- **技术栈**：New-API（Go后端）+ Node.js（CLI）+ Python（bot团队）

---

## 联系/合作

- 有问题反馈：在GitHub提issue
- 推广合作：K哥（AIXX创始人）

---

> AIXX = AI eXtended eXperience
> 让你的AI调用万物。
> 维护者：龙龙（AIXX PM）| 2026-08-09
