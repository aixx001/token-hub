#!/usr/bin/env python3
"""
AIXX AI能力搜索代理（Search Proxy）
职责：实现 AIXX 2.0 的"AI的谷歌"核心功能——用户 agent 说"我要个审美skill/开发skill"，
      本服务去 GitHub 搜相关开源工具，再用 DeepSeek 读 README 信息打分 + 生成中文推荐理由，
      返回结构化结果给用户 agent（含安装方式）。

定位：和 image_proxy.py 是兄弟服务——同样的部署模式、同样的零依赖 Python 标准库、
      同样的日志/错误格式（OpenAI 兼容）。第一步只搜 GitHub 的 skill/agent 类项目，
      未来加 HuggingFace。

核心链路：
  用户agent POST /v1/search {query:"审美skill", n:5}
    ↓ 1. 查缓存（query 的 MD5 哈希 + n，1小时TTL，命中直接返回）
    ↓ 2. 关键词扩展（中文→英文，如"审美"→ aesthetic/design/ui）+ 质量过滤模板
    ↓ 3. 调 GitHub /search/repositories（带 token，监控限流）
    ↓ 4. 取 top 候选（默认 n=5，最多 10）→ 提取元数据
    ↓ 5. 调 DeepSeek（走 New-API 中转：http://localhost:8080）批量评分 + 生成中文推荐
    ↓ 6. 缓存结果 + 返回结构化 JSON 给 agent

运行：python3 search_proxy.py  （或 systemd 托管）
依赖：仅 Python 标准库（http.server + urllib + json + hashlib + threading，零依赖，
      参照 image_proxy.py 风格）
"""

import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ============ 配置 ============
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8091

# GitHub Search API（v3 REST）
GITHUB_API_BASE = "https://api.github.com"
GITHUB_SEARCH_PATH = "/search/repositories"

# New-API 中转地址（DeepSeek 评分走它，走 AIXX 计费系统，成本可观测）
NEWAPI_URL = os.environ.get("NEWAPI_URL", "http://localhost:8080")
NEWAPI_DEEPSEEK_PATH = "/v1/chat/completions"

# 凭据（从环境变量读，绝不硬编码——红线）
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")   # GitHub PAT，调搜索接口
NEWAPI_API_KEY = os.environ.get("NEWAPI_API_KEY", "")  # New-API 的 root key，调 DeepSeek 评分

# DeepSeek 评分用模型名（走 New-API 中转，New-API 内部路由到真实 DeepSeek 渠道）
DEEPSEEK_MODEL = "deepseek-chat"

# 超时（秒）：GitHub 搜索 20 秒，DeepSeek 评分 60 秒（批量评分可能慢）
GITHUB_TIMEOUT = 20
DEEPSEEK_TIMEOUT = 60

# 请求体大小上限（字节）：抄 image_proxy 的 MAX_BODY，2MB 足够
MAX_BODY = 2 * 1024 * 1024

# 缓存
CACHE_TTL = 3600  # 1 小时
SEARCH_CACHE_DIR = os.environ.get("SEARCH_CACHE_DIR", "/opt/aixx/bots/search-proxy/cache")

# 日志文件路径（可被环境变量覆盖，方便本地测试）
LOG_FILE = os.environ.get("SEARCH_LOG_FILE", "/opt/aixx/bots/logs/search-proxy.log")

# ============ IP 限流（公网开放后防滥用）============
# 免费功能不鉴权，但防有人刷接口消耗 GitHub 额度（30次/分钟）和 DeepSeek 计费。
# 真实用户1分钟搜不了几次（打字都要时间），10次/分钟/IP 足够用。
RATE_LIMIT_PER_MIN = int(os.environ.get("SEARCH_RATE_LIMIT", "10"))  # 每IP每分钟最多N次
_rate_bucket = {}  # {ip: [(timestamp, ...)]}
_rate_lock = threading.Lock()


def check_rate_limit(client_ip):
    """检查IP限流。返回True=放行，False=超限。"""
    now = time.time()
    window = 60  # 1分钟窗口
    with _rate_lock:
        history = _rate_bucket.get(client_ip, [])
        # 清掉1分钟前的记录
        history = [t for t in history if now - t < window]
        if len(history) >= RATE_LIMIT_PER_MIN:
            _rate_bucket[client_ip] = history
            return False
        history.append(now)
        _rate_bucket[client_ip] = history
        return True

# 返回结果数量上下限（接口层防御）
MAX_N = 10
DEFAULT_N = 5

# 启动前校验：缺凭据拒绝启动（和 image_proxy 校验 ARK_API_KEY 一个思路）
if not GITHUB_TOKEN:
    print("[ERROR] 未设置 GITHUB_TOKEN 环境变量，拒绝启动", flush=True)
    sys.exit(1)
if not NEWAPI_API_KEY:
    print("[ERROR] 未设置 NEWAPI_API_KEY 环境变量，拒绝启动", flush=True)
    sys.exit(1)

# ============ 关键词扩展表（中文→英文 GitHub 搜索词） ============
# 用户常用中文需求 → GitHub 上更可能命中的英文关键词。命中哪个中文词，就把对应英文词
# 全加进去；没命中的英文词（如用户直接用英文 query）原样保留使用。
KEYWORD_MAP = {
    "审美": ["aesthetic", "design", "ui", "visual"],
    "开发": ["developer", "coding", "programming", "development"],
    "写作": ["writing", "content", "copywriting"],
    "翻译": ["translation", "translate", "i18n"],
    "分析": ["analysis", "analytics", "data"],
    "代码": ["code", "coding", "programming"],
    "设计": ["design", "ui", "ux"],
    "绘画": ["drawing", "painting", "image", "art"],
    "画图": ["image", "drawing", "generation", "diffusion"],
    "音乐": ["music", "audio", "sound"],
    "视频": ["video", "movie", "ffmpeg"],
    "搜索": ["search", "retrieval", "rag"],
    "知识库": ["knowledge", "rag", "memory", "kb"],
    "爬虫": ["crawler", "scraper", "spider"],
    "测试": ["test", "testing", "qa"],
    "自动化": ["automation", "automate", "workflow"],
    "办公": ["office", "document", "docx", "xlsx"],
    "表格": ["spreadsheet", "excel", "xlsx", "table"],
    "聊天": ["chat", "conversation", "dialogue"],
    "客服": ["customer", "support", "service"],
}

# ============ 工具函数 ============
_log_lock = threading.Lock()  # 多线程写日志文件用，防多行交错

def log(msg, level="INFO"):
    """记日志（同时 print 到 stdout + 写文件）

    注意：这里和 sentinel 的 log 函数【相反】。
    - sentinel 只 print，依赖 systemd 的 StandardOutput=append 把 stdout 重定向进文件；
      如果 sentinel 同时 print 又写文件，会导致每条日志在文件里出现 2 次（双写 bug）。
    - 本代理反过来：systemd unit 里【不】配 StandardOutput=append（让 stdout 默认走 journal），
      所以 log 函数需要自己写文件。print 给 journal 看（journalctl / systemctl status），
      文件给运维 tail -f 看。这样避免重蹈 sentinel 双写覆辙。
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{level}] {ts} | {msg}"
    # 1. print 给 systemd journal（systemctl status 能看到）
    print(line, flush=True)
    # 2. 写文件给运维 tail -f 看
    try:
        with _log_lock:
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception as e:
        # 写文件失败不能影响主流程（比如本地测试目录没权限），print 一条兜底
        print(f"[WARN] 写日志文件失败: {e}", flush=True)


class SearchError(Exception):
    """搜索流程中可预期失败的异常，带 HTTP 状态码（透传给用户）"""
    def __init__(self, message, http_status=502, err_type="upstream_error"):
        super().__init__(message)
        self.http_status = http_status
        self.err_type = err_type


# ============ 关键词扩展 + 质量过滤模板 ============
def expand_query(raw_query):
    """把用户 query（可中文可英文）扩展成 GitHub 搜索 query 字符串。

    逻辑：
      1. 遍历 KEYWORD_MAP，用户 query 里命中哪个中文词，把对应英文词加进来；
      2. 中文原词本身【不进】query（GitHub对中文支持差，会污染结果）；
         只保留：英文扩展词 + 用户原query里的英文词 + "skill"/"agent"等通用词；
      3. 返回 (主query, 质量过滤) 两个部分，由调用方拼装。

    返回值：(keyword_part, quality_filter)
      keyword_part: 主搜索词（空格分隔的英文词）
      quality_filter: 质量过滤模板字符串
    """
    terms = []
    seen = set()

    def add_term(t):
        t = t.strip().strip("-").lower()
        if t and t not in seen and not _has_chinese(t):
            seen.add(t)
            terms.append(t)

    # 1) 用户原 query 里的【英文/数字词】保留（中文词跳过，靠映射增强）
    for tok in re.split(r"[\s,，、/]+", raw_query):
        add_term(tok)

    # 2) 命中中文关键词的，把对应英文词加进来（核心：中文→英文翻译）
    for cn, en_list in KEYWORD_MAP.items():
        if cn in raw_query:
            for en in en_list:
                add_term(en)

    # 3) skill/agent 类通用词兜底（用户一般是在找"skill"，这个词要带上）
    # 只在用户意图明显是找工具/skill时加（避免搜非skill类项目时强加）
    if any(k in raw_query for k in ["skill", "工具", "tool", "插件", "plugin", "能力"]):
        add_term("skill")
        add_term("agent")

    # 兜底：如果扩展后啥也没有（纯中文没命中映射），用原串的拼音/原样兜底
    if not terms:
        # 极端情况：原query纯中文且没命中任何映射，用原串硬搜（GitHub会尽量匹配）
        terms = [raw_query.strip()]

    keyword_part = " ".join(terms)

    # 质量过滤模板（写死，每次都加）
    quality_filter = "stars:>10 pushed:>2025-01-01 archived:false"

    return keyword_part, quality_filter


def _has_chinese(text):
    """判断字符串是否含中文字符（用于过滤掉中文原词不进GitHub query）"""
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def build_github_queries(raw_query):
    """构造两级 GitHub query（严格→宽松），用于降级搜索策略。

    返回 [严格query, 宽松query]：
      - 严格：带 topic 限定（只搜 skill/agent 类项目），精准但可能0结果
      - 宽松：去掉 topic 限定（靠关键词+质量过滤），命中率高
    调用方应先试严格，0结果再用宽松。
    """
    keyword_part, quality_filter = expand_query(raw_query)
    in_fields = f"{keyword_part} in:name,description,topics,readme"

    # skill/agent 类 topic 过滤（严格版用，必须括号包起来防优先级错乱）
    topic_filter = (
        "(topic:skill OR topic:claude-skills OR topic:agent "
        "OR topic:ai-agent OR topic:ai-tools OR topic:llm-agent OR topic:cursor)"
    )

    strict = f"{in_fields} {topic_filter} {quality_filter}"
    loose = f"{in_fields} {quality_filter}"
    return [strict, loose]


# ============ GitHub 搜索 ============
def search_github(query, per_page):
    """调 GitHub /search/repositories，返回 (total_count, items_list)。

    items_list 里每个元素是已经提取好的元数据 dict（name/url/stars/desc/topics/updated）。
    失败抛 SearchError（已带 HTTP 状态码 + 友好提示）。
    """
    params = urllib.parse.urlencode({
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    })
    url = f"{GITHUB_API_BASE}{GITHUB_SEARCH_PATH}?{params}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",  # GitHub 要求 Bearer 或 token 前缀
            "Accept": "application/vnd.github+json",     # GitHub v3 推荐的 Accept
            "User-Agent": "AIXX-Search",                 # GitHub 强制要求带 UA，否则 403
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=GITHUB_TIMEOUT) as resp:
            # 监控限流余量（x-ratelimit-remaining 头），余量 < 5 警告一下
            remaining = resp.headers.get("x-ratelimit-remaining")
            if remaining is not None and remaining.isdigit() and int(remaining) < 5:
                log(f"GitHub 限流余量告急: x-ratelimit-remaining={remaining}", "WARN")
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 403/429 通常是限流，读 retry-after 头给客户端友好提示
        if e.code in (403, 429):
            retry_after = e.headers.get("retry-after", "未知")
            log(f"GitHub 限流 HTTP {e.code} retry-after={retry_after}", "WARN")
            raise SearchError(
                "GitHub 搜索被限流，请稍后重试",
                http_status=503,
                err_type="rate_limit",
            )
        # 422 通常是 query 语法错误（比如 OR 拼错），提示客户端检查 query
        if e.code == 422:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            log(f"GitHub query 语法错误 422: {err_body[:200]}", "WARN")
            raise SearchError(
                "搜索 query 语法不被 GitHub 接受，请调整关键词",
                http_status=400,
                err_type="invalid_request_error",
            )
        # 其他 HTTP 错误，读响应体辅助排查
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        log(f"GitHub 搜索返回 HTTP {e.code}: {err_body[:200]}", "WARN")
        raise SearchError(
            f"GitHub 搜索失败（原始HTTP {e.code}）",
            http_status=502,
            err_type="upstream_error",
        )
    except urllib.error.URLError as e:
        # 网络层错误（超时/连不上 GitHub）
        raise SearchError(
            f"连接 GitHub 失败: {e}",
            http_status=502,
            err_type="upstream_error",
        )

    # 提取需要的元数据字段，丢掉 GitHub 返回的一大堆冗余字段
    total = data.get("total_count", 0)
    items = []
    for it in data.get("items", []):
        items.append({
            "name": it.get("full_name", ""),               # owner/repo-name
            "url": it.get("html_url", ""),
            "stars": it.get("stargazers_count", 0),
            "description": it.get("description") or "",     # description 可能为 None
            "topics": it.get("topics", []) or [],
            "updated_at": it.get("pushed_at", "")[:10],     # 截到日期 YYYY-MM-DD
        })
    return total, items


# ============ DeepSeek 评分（走 New-API 中转） ============
def build_score_prompt(query, items):
    """构造给 DeepSeek 的一次性批量评分 prompt（省 token）。

    返回 (system_prompt, user_prompt)。
    """
    system_prompt = (
        "你是AI skill/工具评估专家。用户想找一个【可直接安装使用】的AI skill或工具。"
        "根据用户需求，评估下面这些GitHub项目哪个最适合，给出中文推荐理由和安装方式。"
    )

    # 拼候选项目清单（按 star 排序，编号方便模型对齐）
    lines = [f"用户需求：{query}", "", "候选项目（按star排序）："]
    for i, it in enumerate(items, 1):
        topics_str = ",".join(it.get("topics", [])) or "无"
        lines.append(
            f"{i}. {it['name']} (⭐{it['stars']}) - {it['description']} "
            f"[topics: {topics_str}] 更新于{it['updated_at']}"
        )

    lines.append("")
    lines.append(
        "评分规则（重要）：\n"
        "- 用户要的是【可直接装的skill/工具】，不是资源汇总\n"
        "- 仓库名含 awesome 或 纯资源列表（只罗列别人的项目）→ 降权，match_score 不超过 50\n"
        "- 真正可安装的 skill/工具（有自己的功能，能 clone/装了就用）→ 优先，高分\n"
        "- 和用户需求贴合度越高分越高，完全不相关给 0-20\n\n"
        "请对每个项目输出JSON（严格按格式，便于解析）：\n"
        "[\n"
        "  {\"name\":\"owner/repo1\", \"match_score\":92, "
        "\"recommendation\":\"中文推荐理由1-2句\", \"install_hint\":\"安装命令或方式\"},\n"
        "  ...\n"
        "]\n"
        "只输出JSON，不要其他文字。match_score 0-100。"
    )

    user_prompt = "\n".join(lines)
    return system_prompt, user_prompt


def _strip_json_fence(text):
    """去掉模型可能包裹的 ```json ... ``` 围栏，纯化成 JSON 文本。"""
    text = text.strip()
    # 去开头的 ```json 或 ```
    if text.startswith("```"):
        # 去第一行（可能是 ```json）
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl + 1:]
        else:
            text = text[3:]
        # 去结尾的 ```
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def parse_deepseek_scores(raw_text, items, max_stars):
    """解析 DeepSeek 返回的 JSON 评分列表。

    容错策略：
      - 先尝试整体解析为 JSON 数组；
      - 失败则尝试用正则抠出第一个 [ ... ] 块再解析；
      - 还失败则降级：recommendation=原description，分数按 star 归一化到 0-100。

    返回 dict: {full_name: {match_score, recommendation, install_hint}}
    """
    result = {}

    # 尝试解析
    parsed = None
    candidates = []
    cleaned = _strip_json_fence(raw_text)
    candidates.append(cleaned)
    # 正则抠第一个数组块（防止模型在 JSON 前后多说了几句话）
    m = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if m:
        candidates.append(m.group(0))

    for c in candidates:
        try:
            obj = json.loads(c)
            if isinstance(obj, list):
                parsed = obj
                break
        except Exception:
            continue

    if parsed:
        # 按 name 建索引，name 大小写不敏感匹配
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            name = entry.get("name", "")
            if not name:
                continue
            result[name.lower()] = {
                "match_score": _safe_score(entry.get("match_score")),
                "recommendation": str(entry.get("recommendation", "")).strip(),
                "install_hint": str(entry.get("install_hint", "")).strip(),
            }

    # 降级 + 补全：对每个候选项目，没拿到评分的就按 star 归一化兜底
    for it in items:
        key = it["name"].lower()
        if key not in result:
            score = 0
            if max_stars > 0:
                score = int(round(it["stars"] / max_stars * 100))
            result[key] = {
                "match_score": score,
                "recommendation": it["description"] or "（暂无描述）",
                "install_hint": "",
            }
        else:
            # 拿到评分但 recommendation/install_hint 为空，也用 description 兜底
            r = result[key]
            if not r["recommendation"]:
                r["recommendation"] = it["description"] or "（暂无描述）"

    return result


def _safe_score(val):
    """把模型的 match_score 收敛到 0-100 整数。"""
    try:
        s = int(round(float(val)))
    except Exception:
        s = 50
    return max(0, min(100, s))


def score_with_deepseek(query, items):
    """调 DeepSeek（走 New-API 中转）批量评分，返回 dict（同 parse_deepseek_scores 返回）。

    失败时降级：所有项目按 star 归一化打分，recommendation=原description。
    """
    if not items:
        return {}

    max_stars = max((it["stars"] for it in items), default=0)
    system_prompt, user_prompt = build_score_prompt(query, items)

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 2000,
        "temperature": 0.3,  # 评分要稳定，不要发散
        "stream": False,
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{NEWAPI_URL.rstrip('/')}{NEWAPI_DEEPSEEK_PATH}",
        data=body,
        headers={
            "Authorization": f"Bearer {NEWAPI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    raw_text = ""
    try:
        with urllib.request.urlopen(req, timeout=DEEPSEEK_TIMEOUT) as resp:
            resp_json = json.loads(resp.read().decode("utf-8"))
        # OpenAI 兼容格式：choices[0].message.content
        choices = resp_json.get("choices", [])
        if choices:
            raw_text = choices[0].get("message", {}).get("content", "")
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        log(f"DeepSeek 评分返回 HTTP {e.code}: {err_body[:200]}，降级按star打分", "WARN")
    except Exception as e:
        log(f"DeepSeek 评分异常: {e}，降级按star打分", "WARN")

    if not raw_text:
        log("DeepSeek 未返回内容，降级按star打分", "WARN")

    return parse_deepseek_scores(raw_text, items, max_stars)


# ============ 缓存层 ============
def _cache_key(query, n):
    """缓存 key = MD5(query)_n{n}.json"""
    md5 = hashlib.md5(query.encode("utf-8")).hexdigest()
    return f"{md5}_n{n}.json"


def cache_get(query, n):
    """读缓存。命中且未过期返回缓存的响应 dict（含 cached=True）；否则返回 None。"""
    try:
        path = os.path.join(SEARCH_CACHE_DIR, _cache_key(query, n))
        if not os.path.exists(path):
            return None
        # 检查 mtime 是否过期
        age = time.time() - os.path.getmtime(path)
        if age > CACHE_TTL:
            # 过期就删，重新搜
            try:
                os.remove(path)
            except Exception:
                pass
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 命中标记为 cached=True（写盘时存的是 cached=False 的原始结果）
        data["cached"] = True
        return data
    except Exception as e:
        log(f"读缓存失败（忽略，继续走正常流程）: {e}", "WARN")
        return None


def cache_put(query, n, response_obj):
    """写缓存。response_obj 里的 cached 字段会被强制写成 False（命中时由 cache_get 改回 True）。"""
    try:
        os.makedirs(SEARCH_CACHE_DIR, exist_ok=True)
        to_save = dict(response_obj)
        to_save["cached"] = False  # 原始结果不是来自缓存
        path = os.path.join(SEARCH_CACHE_DIR, _cache_key(query, n))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(to_save, f, ensure_ascii=False)
    except Exception as e:
        log(f"写缓存失败（不影响返回，只是下次还得重搜）: {e}", "WARN")


# ============ 主搜索流程 ============
def do_search(query, n):
    """主搜索流程：缓存 → 关键词扩展 → GitHub → DeepSeek 评分 → 缓存 → 返回。

    返回最终要发给客户端的响应 dict。失败抛 SearchError（已带 HTTP 状态码）。
    """
    # 1. 查缓存
    cached = cache_get(query, n)
    if cached is not None:
        log(f"缓存命中 query={query!r} n={n}")
        return cached

    # 2. 关键词扩展 + 质量过滤（两级降级：严格topic版→宽松版）
    candidate_queries = build_github_queries(query)  # [严格, 宽松]
    per_page = min(n * 2, 30)  # 多取给 LLM 筛选留余地

    total, items = 0, []
    used_query = ""
    for i, gh_query in enumerate(candidate_queries):
        level = "严格" if i == 0 else "宽松(降级)"
        log(f"尝试搜索[{level}] query={gh_query[:120]}")
        try:
            total, items = search_github(gh_query, per_page=per_page)
        except SearchError as e:
            # GitHub限流/422语法错等：严格版失败就试宽松版，宽松版还失败才抛
            if i == 0:
                log(f"严格版搜索失败({e})，降级到宽松版", "WARN")
                continue
            raise
        if items:
            used_query = gh_query
            log(f"[{level}]搜到 {total} 个结果，取 {len(items)} 个")
            break
        # 严格版0结果，降级到宽松版继续

    if not items:
        # 两级都0结果，返回空（合法结果）
        log(f"GitHub 未搜到结果 query={query!r}（严格+宽松都试过）")
        return {
            "query": query,
            "total_found": total,
            "results": [],
            "cached": False,
        }

    # 4. 调 DeepSeek 批量评分
    scores = score_with_deepseek(query, items)

    # 5. 合并元数据 + 评分，组装最终 results
    results = []
    for it in items:
        sc = scores.get(it["name"].lower(), {})
        results.append({
            "name": it["name"],
            "url": it["url"],
            "stars": it["stars"],
            "description": it["description"],
            "recommendation": sc.get("recommendation", it["description"] or "（暂无描述）"),
            "install_hint": sc.get("install_hint", ""),
            "match_score": sc.get("match_score", 0),
            "topics": it["topics"],
            "updated_at": it["updated_at"],
        })

    # 6. 按匹配分排序（高分在前），再截到 n 个
    #    说明：GitHub 已经按 star 排过序，这里再用 LLM 的 match_score 重排，把真正贴合
    #    用户需求的提到前面（star 高不一定最匹配，比如用户要"审美"但高star的是通用UI库）。
    results.sort(key=lambda x: x["match_score"], reverse=True)
    results = results[:n]

    response = {
        "query": query,
        "total_found": total,
        "results": results,
        "cached": False,
    }

    # 7. 写缓存 + 返回
    cache_put(query, n, response)
    log(f"搜索完成 query={query!r} total={total} 返回={len(results)}")
    return response


# ============ HTTP 请求处理 ============
class SearchProxyHandler(BaseHTTPRequestHandler):
    """处理进来的 HTTP 请求（OpenAI 兼容格式）"""

    # 关掉默认的请求日志（BaseHTTPRequestHandler 默认会把每条请求打到 stderr，太吵）
    def log_message(self, format, *args):
        pass

    def _send_json(self, status_code, obj):
        """统一 JSON 响应出口"""
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_openai_error(self, http_status, message, err_type="internal_error"):
        """返回标准 OpenAI 错误格式 {"error": {"message":..., "type":...}}"""
        self._send_json(http_status, {
            "error": {"message": message, "type": err_type}
        })

    def do_GET(self):
        """GET 路由：只有 /health（健康检查）"""
        # 去掉 query 部分，允许 /health?xxx 这种探活
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send_json(200, {"status": "ok"})
        else:
            self._send_openai_error(404, f"路径不存在: {self.path}", "not_found")

    def do_POST(self):
        """POST 路由：/v1/search"""
        path = self.path.split("?", 1)[0]
        if path != "/v1/search":
            self._send_openai_error(404, f"路径不存在: {self.path}", "not_found")
            return

        # 0. IP 限流（公网开放后防滥用，真实用户感知不到）
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self._send_openai_error(429, f"搜索太频繁，每分钟限{RATE_LIMIT_PER_MIN}次，请稍后再试", "rate_limit_exceeded")
            return

        # 1. 读请求体（带大小上限，抄 image_proxy）
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > MAX_BODY:
                self._send_openai_error(413, f"请求体过大（限制{MAX_BODY//1024}KB）", "request_too_large")
                return
            raw = self.rfile.read(length) if length > 0 else b"{}"
            req_json = json.loads(raw.decode("utf-8"))
        except (ValueError, json.JSONDecodeError) as e:
            self._send_openai_error(400, f"请求体不是合法 JSON: {e}", "invalid_request_error")
            return

        # 2. 参数校验：query 必填、非空字符串；n 可选默认 5，范围 1~10
        query = req_json.get("query", "")
        if not isinstance(query, str) or not query.strip():
            self._send_openai_error(400, "缺少必填字段 query（用户需求，非空字符串）", "invalid_request_error")
            return
        query = query.strip()

        n = req_json.get("n", DEFAULT_N)
        try:
            n = int(n)
        except (TypeError, ValueError):
            n = DEFAULT_N
        if n < 1:
            n = 1
        if n > MAX_N:
            n = MAX_N

        # 不校验 Authorization（免费功能，和 image_proxy 思路一致——鉴权由前面的 New-API 负责）
        query_preview = query[:30]  # 日志只记前 30 字
        log(f"收到搜索请求 query={query_preview!r} n={n}")

        # 3. 主流程
        try:
            response = do_search(query, n)
            self._send_json(200, response)
        except SearchError as e:
            # 可预期的上游错误（限流/GitHub失败等），透传状态码 + 友好提示
            log(f"搜索失败 query={query_preview!r} 原因={e}", "ERROR")
            self._send_openai_error(e.http_status, str(e), e.err_type)
        except Exception as e:
            # 兜底：未预期的内部错误
            # 注意：响应里只给通用文案，详情留日志（避免异常repr泄露内网拓扑如localhost:8080）
            log(f"搜索异常 query={query_preview!r} 异常={e}", "ERROR")
            self._send_openai_error(500, "代理内部错误", "internal_error")


# ============ 启动入口 ============
def main():
    # ThreadingHTTPServer：每个请求开一个线程，GitHub/DeepSeek 调用慢不会阻塞别的请求
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), SearchProxyHandler)
    log("=" * 50)
    log("AIXX AI能力搜索代理启动")
    log(f"监听: {LISTEN_HOST}:{LISTEN_PORT}")
    log(f"GitHub: {GITHUB_API_BASE} 超时={GITHUB_TIMEOUT}秒")
    log(f"DeepSeek中转(New-API): {NEWAPI_URL} 模型={DEEPSEEK_MODEL} 超时={DEEPSEEK_TIMEOUT}秒")
    log(f"缓存: 目录={SEARCH_CACHE_DIR} TTL={CACHE_TTL}秒")
    log(f"关键词映射表覆盖: {len(KEYWORD_MAP)} 个中文需求")
    log(f"日志文件: {LOG_FILE}（同时输出到 stdout/journal）")
    log("鉴权: 不校验请求方 Authorization（免费功能）")
    log("=" * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("代理手动停止")
        server.shutdown()
        sys.exit(0)
    except Exception as e:
        log(f"代理崩溃: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
