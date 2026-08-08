#!/usr/bin/env python3
"""
AIXX 调度bot（Dispatcher）
职责：根据用户意图 + 哨兵健康状态，推荐一个最优模型
原则：只做"选模型"的决策，不执行调用、不健康巡检（执行是别的bot的活）

工作方式：
  - 读哨兵写下的渠道状态文件（channel_states.json）
  - 用关键词识别用户意图（翻译/分析/编程/写作/长文本），不走LLM
  - 按任务→模型优先级，从【健康渠道支持】的模型里选第一个
  - 支持 --pref 偏好覆盖（cheapest/strongest/fastest）
  - 首选不健康自动切下一个；全挂返回任意健康模型并标"降级"

运行：python3 dispatcher.py recommend "用户的请求文本" [--pref cheapest|strongest|fastest]
依赖：仅Python标准库（json/os/sys/datetime），零依赖
"""

import json
import os
import sys
from datetime import datetime

# ============ 配置 ============
NEWAPI_URL = "http://localhost:8080"
# 生产路径写死；AIXX_STATE_FILE 留给自测覆盖，平时用不到
STATE_FILE = os.environ.get("AIXX_STATE_FILE", "/opt/aixx/bots/sentinel/channel_states.json")
LOG_FILE = "/opt/aixx/bots/logs/dispatcher.log"

# 状态过期阈值（秒）。哨兵每60秒巡检一次，2个周期=120秒，留余量取300秒（5分钟）。
STATE_STALE_SECONDS = 300

# 模型价格表（元/千token，输入价）—— cheapest 偏好用
MODEL_PRICES = {
    "deepseek-chat": 0.001,
    "deepseek-reasoner": 0.004,
    "glm-4-flash": 0.0001,
    "glm-4-plus": 0.05,
    "moonshot-v1-8k": 0.012,
    "moonshot-v1-128k": 0.024,
    "claude-sonnet-4-20250514": 0.021,
    "claude-opus-4-8": 0.105,
    "gpt-4o": 0.0175,
    "gpt-4o-mini": 0.001,
    "grok-2-latest": 0.002,
}

# 任务→模型映射（按优先级，首选在前）—— 兜底用 moonshot-v1-32k 不在价格表，按需补
TASK_MODEL_MAP = {
    "翻译": ["deepseek-chat", "gpt-4o-mini", "glm-4-flash"],
    "分析": ["claude-opus-4-8", "claude-sonnet-4-20250514", "deepseek-reasoner"],
    "编程": ["deepseek-chat", "claude-sonnet-4-20250514", "gpt-4o"],
    "写作": ["glm-4-plus", "deepseek-chat", "claude-sonnet-4-20250514"],
    "长文本": ["moonshot-v1-128k", "moonshot-v1-32k"],
    "默认": ["deepseek-chat", "glm-4-flash", "gpt-4o-mini"],
}

# 任务识别关键词表（顺序即优先级：长文本要先于写作/翻译判断，避免被吞掉）
TASK_KEYWORDS = [
    ("长文本", ["长文", "long", "文档", "document", "论文", "总结全书", "万字"]),
    ("翻译", ["翻译", "translate", "convert", "译成", "中翻英", "英翻中"]),
    ("分析", ["分析", "analyze", "商业", "计划", "report", "报告", "战略", "研究", "评估", "洞察"]),
    ("编程", ["代码", "code", "编程", "bug", "program", "函数", "脚本", "debug", "算法", "接口"]),
    ("写作", ["写作", "write", "文章", "文案", "撰写", "起草", "润色", "扩写"]),
]

# 最强模型（strongest 偏好用）
STRONGEST_MODEL = "claude-opus-4-8"
STRONGEST_FALLBACK = ["claude-sonnet-4-20250514", "deepseek-reasoner"]

# 默认模型（哨兵状态文件读不到/全挂时的最终兜底）
DEFAULT_FALLBACK_MODEL = "deepseek-chat"


# ============ 工具函数 ============
def log(msg, level="INFO"):
    """记日志（同时打屏 + 写文件，文件不可写也不崩）"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{level}] {ts} | {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_states():
    """读哨兵的状态文件。不存在/损坏都不崩，返回空状态（调用方走兜底）。"""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("channels"), dict):
            return data
    except FileNotFoundError:
        log(f"哨兵状态文件不存在: {STATE_FILE}（用默认模型兜底）", "WARN")
    except json.JSONDecodeError:
        log(f"哨兵状态文件损坏（非法JSON）: {STATE_FILE}（用默认模型兜底）", "WARN")
    except Exception as e:
        log(f"读哨兵状态文件失败: {e}（用默认模型兜底）", "WARN")
    return {"updated_at": None, "channels": {}}


def is_states_stale(states):
    """
    判断哨兵状态是否过期。

    updated_at 是哨兵写下的 isoformat 字符串。读不到/解析失败/超过
    STATE_STALE_SECONDS（默认5分钟=2个巡检周期余量）都视为过期，
    返回 (是否过期, 过期分钟数)。过期分钟数仅用于日志，过期时恒有意义。
    """
    updated_at = states.get("updated_at")
    if not updated_at:
        return True, None
    try:
        updated_dt = datetime.fromisoformat(str(updated_at))
    except (ValueError, TypeError):
        # 时间戳不可解析 → 当作过期（没法判断新鲜度，宁走兜底）
        return True, None
    age_seconds = (datetime.now() - updated_dt).total_seconds()
    stale = age_seconds > STATE_STALE_SECONDS
    return stale, int(age_seconds // 60) if age_seconds >= 0 else 0


def parse_channel_models(models_field):
    """渠道的 models 字段是逗号分隔的字符串，拆成干净的模型名集合。"""
    if not models_field:
        return []
    if isinstance(models_field, list):
        items = models_field
    else:
        items = str(models_field).split(",")
    return [m.strip() for m in items if m and m.strip()]


def build_model_health(states):
    """
    把【按渠道】的健康状态，转成【按模型】的健康视图。

    返回三样：
      model_to_latency: {模型名: 该模型当前最低延迟}（fastest 偏好用）
      healthy_models:   set(健康渠道支持的模型名)
      has_data:         哨兵是否有任何渠道数据（用于区分"没数据"和"全挂"）
    """
    model_to_latency = {}
    healthy_models = set()
    channels = states.get("channels", {})
    has_data = len(channels) > 0  # 区分"哨兵没数据"和"哨兵有数据但全挂"
    for _cid, info in channels.items():
        if not isinstance(info, dict):
            continue
        is_healthy = info.get("status") == "healthy"
        latency = info.get("latency") or 0
        for model in parse_channel_models(info.get("models")):
            # 延迟取最小（同一模型多渠道时，选最快的那个代表）
            if model not in model_to_latency or (latency and latency < model_to_latency[model]):
                model_to_latency[model] = latency
            if is_healthy:
                healthy_models.add(model)
    return model_to_latency, healthy_models, has_data


def is_model_healthy(model, healthy_models):
    """模型是否可用：看是否在哨兵判定的健康集合里。集合由上层决定是否为空。"""
    return model in healthy_models


def model_price(model):
    """取模型价格，价格表没有的给个极大值（排序时排到最后，不影响功能）。"""
    return MODEL_PRICES.get(model, float("inf"))


# ============ 核心：意图识别 ============
def detect_task(text):
    """关键词匹配识别任务类型。匹配不上返回"默认"。"""
    lowered = text.lower()
    for task, keywords in TASK_KEYWORDS:
        for kw in keywords:
            if kw in lowered:
                return task
    return "默认"


# ============ 核心：候选 → 选定 ============
def select_by_priority(candidates, healthy_models):
    """从候选列表里挑第一个健康的模型，返回 (模型名, 是否降级)。"""
    for m in candidates:
        if is_model_healthy(m, healthy_models):
            return m, False
    # 候选全不健康，进降级
    return None, True


def select_cheapest(healthy_models):
    """cheapest：在健康模型里选价格最低的。全挂则返回 None（交给上层降级）。"""
    pool = [m for m in (MODEL_PRICES.keys()) if is_model_healthy(m, healthy_models)]
    if not pool:
        return None, True
    return min(pool, key=model_price), False


def select_strongest(healthy_models):
    """strongest：优先 Claude Opus，不健康就退 Sonnet/reasoner。"""
    for m in [STRONGEST_MODEL] + STRONGEST_FALLBACK:
        if is_model_healthy(m, healthy_models):
            return m, False
    return None, True


def select_fastest(healthy_models, model_to_latency):
    """fastest：在健康模型里选延迟最低的。无延迟数据时退化为优先级。"""
    pool = {m: model_to_latency.get(m) for m in healthy_models}
    # 只看有延迟数据的；全没数据则 healthy_models 任选一个
    with_latency = {m: v for m, v in pool.items() if v}
    if with_latency:
        return min(with_latency, key=lambda m: with_latency[m]), False
    for m in healthy_models:
        return m, False
    return None, True


def fallback_any_healthy(healthy_models, model_to_latency):
    """全挂降级：任意挑一个健康模型。一个都没有就返回硬兜底。"""
    if healthy_models:
        # 优先挑有延迟数据里最快的，体现降级也尽量挑能用的
        best = None
        best_lat = None
        for m in healthy_models:
            lat = model_to_latency.get(m)
            if lat and (best_lat is None or lat < best_lat):
                best, best_lat = m, lat
        return best or next(iter(healthy_models)), True
    return DEFAULT_FALLBACK_MODEL, True


# ============ 主入口：recommend ============
def recommend(text, pref=None):
    """
    主流程：意图识别 → 偏好/任务选模型 → 故障降级。
    返回 dict（model, task, reason, degraded）。
    """
    task = detect_task(text)
    states = load_states()
    model_to_latency, healthy_models, has_data = build_model_health(states)

    # 哨兵没数据（文件不存在/为空）：不能误判所有模型不可用。
    # 此时认为"全部已知模型都可用"，走正常优先级，不标降级。
    stale, stale_minutes = is_states_stale(states)
    if not has_data:
        # 文件不存在/为空：load_states 已记 WARN，静默走兜底
        healthy_models = set(MODEL_PRICES.keys())
    elif stale:
        # 有数据但过期（>STATE_STALE_SECONDS）：健康集合不可信，用全部已知模型兜底
        log(
            f"哨兵状态过期({stale_minutes}分钟)，使用全量兜底",
            "WARN",
        )
        healthy_models = set(MODEL_PRICES.keys())

    reason_hint = ""
    degraded = False
    model = None

    # 1) 偏好覆盖优先于任务
    if pref == "cheapest":
        model, degraded = select_cheapest(healthy_models)
        reason_hint = "偏好=最低价"
    elif pref == "strongest":
        model, degraded = select_strongest(healthy_models)
        reason_hint = "偏好=最强"
    elif pref == "fastest":
        model, degraded = select_fastest(healthy_models, model_to_latency)
        reason_hint = "偏好=最快"

    # 2) 没指定偏好 / 偏好也选不出来 → 走任务→模型优先级
    if model is None:
        candidates = TASK_MODEL_MAP.get(task, TASK_MODEL_MAP["默认"])
        model, degraded = select_by_priority(candidates, healthy_models)
        reason_hint = reason_hint or f"任务={task}按优先级"

    # 3) 仍选不出来（任务候选全不健康）→ 全挂降级
    if model is None:
        model, degraded = fallback_any_healthy(healthy_models, model_to_latency)
        reason_hint = "任务首选全不健康，降级"

    # 组理由
    price = model_price(model)
    price_str = f"{price}元/千token" if price != float("inf") else "价格未知"
    degrade_tag = " [降级]" if degraded else ""
    reason = (
        f"{reason_hint}{degrade_tag} -> {model}（{price_str}）"
    )

    log(f"recommend | 意图={task} 偏好={pref or '无'} -> {model}{degrade_tag} | 文本=\"{text[:40]}\"")

    return {
        "model": model,
        "task": task,
        "reason": reason,
        "degraded": degraded,
    }


# ============ 命令行入口 ============
USAGE = (
    '用法: python3 dispatcher.py recommend "用户的请求文本" '
    '[--pref cheapest|strongest|fastest]'
)


def parse_args(argv):
    """简单解析命令行。子命令 recommend + 文本 + 可选 --pref。"""
    if len(argv) < 2 or argv[1] != "recommend":
        return None, None, False
    text = None
    pref = None
    rest = argv[2:]
    i = 0
    while i < len(rest):
        tok = rest[i]
        if tok == "--pref" and i + 1 < len(rest):
            pref = rest[i + 1]
            i += 2
        elif tok.startswith("--pref="):
            pref = tok.split("=", 1)[1]
            i += 1
        else:
            if text is None:
                text = tok
            i += 1
    ok = text is not None and (pref in (None, "cheapest", "strongest", "fastest"))
    return text, pref, ok


def main(argv):
    text, pref, ok = parse_args(argv)
    if not ok:
        print(USAGE, file=sys.stderr)
        return 2

    result = recommend(text, pref)
    # 给调用方一份结构化输出（机器可读 + 人可读）
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        log("调度bot手动停止")
        sys.exit(0)
    except Exception as e:
        log(f"调度bot崩溃: {e}", "ERROR")
        sys.exit(1)
