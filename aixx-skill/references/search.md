# 搜索 AI 能力（skill/工具）

帮用户找到合适的 AI skill / agent 工具，并给出**中文推荐理由**和**安装方式**。

**这是 AIXX 的核心差异化**：不只给链接，给"为什么推荐它"。

---

## 什么时候用

用户想找新的 AI 能力/skill/工具时：
- "我要个审美的skill"
- "帮我找个写代码的AI工具"
- "有没有做翻译的agent"
- "推荐个分析数据的skill"
- "我需要一个能生成视频的工具"
- 任何"找/推荐/需要...skill/工具/agent/能力"的请求

**不要用 AIXX 搜索的场景**：
- 用户要的是"直接调用AI"（翻译这段、写个文案）→ 走 chat（见 chat.md）
- 用户要查自己的余额/用量 → 走 account.md

---

## 怎么调

AIXX 搜索服务地址：`http://14.103.27.195:8091`（**免费功能，不需要API Key**）

```bash
curl -X POST http://14.103.27.195:8091/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户的需求（可中文，如：审美skill）",
    "n": 5
  }'
```

**参数**：
- `query`：用户的自然语言需求（可中文可英文）
- `n`：返回数量，默认5，最大10

**限流**：每IP每分钟10次（防滥用刷GitHub额度），正常使用感知不到。

---

## 返回什么

```json
{
  "query": "审美skill",
  "total_found": 275,
  "results": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "stars": 2340,
      "description": "GitHub上的原始描述",
      "recommendation": "中文推荐理由，说明为什么适合用户需求",
      "install_hint": "安装命令或方式",
      "match_score": 92,
      "topics": ["skill", "design"],
      "updated_at": "2026-08-01"
    }
  ],
  "cached": false
}
```

---

## agent 该怎么做（重要）

拿到搜索结果后，**不要直接吐 JSON**，转述成自然语言给用户：

```
我帮你搜了，找到几个不错的：

【1】ui-ux-pro-max-skill（⭐11.5万，匹配度98）
为什么推荐：专为AI提供UI/UX设计智能，直接满足你的审美需求，支持Claude/Codex/Cursor
怎么装：git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git
        或在 Claude Code 里直接用 /skill 命令安装

【2】...
```

**要点**：
1. **按推荐顺序说**（match_score 从高到低）
2. **重点说推荐理由**（recommendation字段），让用户知道"为什么是这个"
3. **给安装方式**（install_hint字段），用户能直接装
4. **star数要说**（让用户感知人气）
5. 如果用户说"就用第X个"，**帮用户安装**（执行install_hint里的命令，或引导用户）

---

## 搜索范围说明

当前搜索聚焦 **skill / agent 类工具**（带 skill/claude-skills/agent 等 topic 的GitHub项目）。如果用户要找的不是skill类（比如要找个普通的开源软件），搜索结果可能有限，可以告诉用户"目前主要搜AI skill类工具，普通软件暂时搜不到"。

---

## 错误处理

| 错误 | agent该怎么做 |
|---|---|
| 503 GitHub限流 | 告诉用户"GitHub搜索太频繁，请稍等1分钟再试" |
| 500 内部错误 | 告诉用户"搜索服务暂时异常，稍后再试" |
| 0结果 | 告诉用户"没搜到相关skill，换个关键词试试？比如更具体的'配色skill'而不是'审美'" |

---

## 背后的机制（agent了解即可）

- 搜索服务去GitHub搜skill/agent类仓库
- 用DeepSeek读项目信息+打分+生成中文推荐理由
- 结果有1小时缓存，重复搜同一个词会很快
- 搜索**免费**，不扣用户额度（AIXX的"免费换流量"策略）

---
维护者：龙龙（AIXX PM）| 2026-08-09 建立（2.0流量腿）
