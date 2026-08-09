#!/usr/bin/env python3
"""
AIXX 哨兵bot（Sentinel）
职责：健康巡检 + 故障标记
原则：只发现故障，不负责修复（修复是别的bot的活）

工作方式：
  - 每60秒ping所有渠道
  - 记录每个渠道的健康状态（健康/超时/错误）
  - 状态写入共享文件（给其他bot读）
  - 异常时记日志（供龙龙/K哥查看）

运行：python3 sentinel.py
依赖：仅Python标准库（requests用urllib替代，零依赖）
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# ============ 配置 ============
NEWAPI_URL = "http://localhost:8080"
ADMIN_USER = "root"
ADMIN_PASS = os.environ.get("AIXX_ADMIN_PASS", "")
CHECK_INTERVAL = 60  # 巡检间隔（秒）
TIMEOUT = 10  # 单次ping超时（秒）

# token缓存：避免每次巡检都登录导致session堆积（坑：曾每60秒登录一次，一天刷爆user_sessions表，root都登不上后台）
_cached_token = None
_cached_token_at = 0  # 登录时间戳
TOKEN_TTL = 3600  # token有效期（秒），1小时复用一个，避免反复登录
STATE_FILE = "/opt/aixx/bots/sentinel/channel_states.json"
LOG_FILE = "/opt/aixx/bots/logs/sentinel.log"

# 故障连续失败计数器：避免渠道偶尔一次超时（网络抖动）就被误报故障（坑：5个渠道同时timeout其实是网络抖动，不是真挂了）
# key=渠道id(str), value=连续不健康次数。连续N次（FAULT_ALERT_THRESHOLD）才告警
_fault_counter = {}
FAULT_ALERT_THRESHOLD = 3  # 连续3次失败才告警

# Server酱额度用完时：到这个时间戳之前停止推送（坑：免费版每天5条，用完返回HTTP 400，之前狂刷400错误26分钟）
# 0表示不限制。设置为明天0点的时间戳表示"今天额度用完，明天再试"
_wechat_disabled_until = 0

# ============ 告警配置 ============
SERVERCHAN_KEY = os.environ.get("AIXX_SERVERCHAN_KEY", "SCT330910T4DJHDPe1Tlm662420YTIcxsY")
BALANCE_CHECK_INTERVAL = 600  # 余额检查间隔（秒），10分钟一次
BALANCE_ALERT_THRESHOLD = 10  # 余额告警阈值（元）
ALERT_DEDUP_WINDOW = 1800  # 告警去重窗口（秒），30分钟内同问题只发1次

# 各官方渠道余额查询配置（只有这几个能查）
BALANCE_ENDPOINTS = {
    "DeepSeek官方": {
        "url": "https://api.deepseek.com/user/balance",
        "key_env": "AIXX_DEEPSEEK_KEY",
        "key_default": "sk-ffb538d1183a414aa874c21185ba7101",
        "parser": "deepseek"
    },
    "Kimi月之暗面": {
        "url": "https://api.moonshot.cn/v1/users/me/balance",
        "key_env": "AIXX_KIMI_KEY",
        "key_default": "sk-36fxgEh4dmoAv3msTocxxtIaxutfufI2E2Yvdrq28Cml8ASC",
        "parser": "kimi"
    }
}

# 欠费/余额不足错误特征（用于第2层报错识别）
INSUFFICIENT_BALANCE_PATTERNS = ["1113", "欠费", "余额不足", "insufficient_balance", "insufficient_quota", "exceeded your current"]

# 启动前校验：缺环境变量拒绝启动
if not ADMIN_PASS:
    print("[ERROR] 未设置AIXX_ADMIN_PASS环境变量，拒绝启动", flush=True)
    sys.exit(1)

# ============ 工具函数 ============
def log(msg, level="INFO"):
    """记日志（只print，写文件交给systemd的StandardOutput重定向）
    注：曾经同时print+写文件，导致每条日志在sentinel.log里出现2次（systemd又把print的输出append进同一个文件）。
    现在单一出口，文件写入完全由systemd负责。LOG_FILE常量保留以对得上systemd配置里的路径。"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{level}] {ts} | {msg}"
    print(line, flush=True)

def api_request(path, method="GET", data=None, token=None):
    """调New-API接口"""
    url = f"{NEWAPI_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode())

def login():
    """管理员登录拿token（带缓存：1小时内复用，避免session堆积）"""
    global _cached_token, _cached_token_at
    now = time.time()
    if _cached_token and (now - _cached_token_at) < TOKEN_TTL:
        return _cached_token
    data = api_request("/api/user/login", "POST", {"username": ADMIN_USER, "password": ADMIN_PASS})
    if not data.get("success"):
        raise Exception(f"登录失败: {data.get('message')}")
    _cached_token = data["data"]["access_token"]
    _cached_token_at = now
    log(f"已登录获取新token（缓存{TOKEN_TTL}秒）")
    return _cached_token

def invalidate_token():
    """token失效时清除缓存，强制下次重新登录"""
    global _cached_token, _cached_token_at
    _cached_token = None
    _cached_token_at = 0

def cleanup_sessions():
    """兜底清理：直接清空user_sessions表，防止历史token堆积把后台登录挤爆（坑：曾堆积50+session导致root登录返回AUTH_SESSION_LIMIT）"""
    db_path = "/opt/aixx/new-api/one-api.db"
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM user_sessions")
        count = cur.fetchone()[0]
        if count > 10:  # 超过10个就清（正常应该个位数）
            cur.execute("DELETE FROM user_sessions")
            conn.commit()
            log(f"清理了{count}个堆积session（防止后台登录爆满）")
        conn.close()
    except Exception as e:
        log(f"清理session失败（非致命，忽略）: {e}", "WARN")

def get_channels(token):
    """获取所有渠道"""
    data = api_request("/api/channel/?p=0&page_size=100", token=token)
    if not data.get("success"):
        raise Exception(f"获取渠道失败: {data.get('message')}")
    result = data.get("data")
    if isinstance(result, list):
        return result
    return result.get("items", []) if isinstance(result, dict) else []

def test_channel(channel, token):
    """测试单个渠道（调New-API的渠道测试接口）"""
    channel_id = channel.get("id")
    channel_name = channel.get("name", f"渠道{channel_id}")
    try:
        data = api_request(f"/api/channel/test/{channel_id}", "GET", token=token)
        if data.get("success"):
            elapsed = data.get("data", {}).get("time", 0)
            return {"status": "healthy", "latency": elapsed, "msg": "OK", "name": channel_name}
        else:
            return {"status": "error", "latency": 0, "msg": data.get("message", "未知错误"), "name": channel_name}
    except urllib.error.URLError as e:
        return {"status": "timeout", "latency": TIMEOUT * 1000, "msg": f"超时: {e}", "name": channel_name}
    except Exception as e:
        return {"status": "error", "latency": 0, "msg": str(e), "name": channel_name}

def save_states(states):
    """保存状态到共享文件（给其他bot读）"""
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "channels": states
        }, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)  # 原子写入，避免读到半个文件

def load_states():
    """读取上次状态（用于对比变化）"""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"channels": {}}

# ============ 告警系统（三层） ============
def push_wechat(title, content):
    """通过Server酱推送到K哥微信"""
    global _wechat_disabled_until
    # 额度用完时跳过推送（今天不再试，避免狂刷400错误26分钟）
    if time.time() < _wechat_disabled_until:
        return False
    try:
        data = urllib.parse.urlencode({"title": title, "desp": content}).encode()
        req = urllib.request.Request(f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if result.get("code") == 0:
                log(f"微信推送成功: {title}")
                return True
            else:
                log(f"微信推送失败: {result}", "WARN")
                return False
    except urllib.error.HTTPError as e:
        # Server酱额度用完会返回HTTP 400（免费版每天5条）。
        # 识别到这个状态就今天不再推送，避免每轮都试狂刷400错误。
        if e.code == 400:
            # 算明天0点的时间戳（到点自动恢复推送）
            now = datetime.now()
            tomorrow_midnight = datetime(now.year, now.month, now.day) + timedelta(days=1)
            _wechat_disabled_until = tomorrow_midnight.timestamp()
            log("Server酱额度用完，停止今日推送（明天0点自动恢复）", "WARN")
            return False
        log(f"微信推送HTTP异常: {e}", "WARN")
        return False
    except Exception as e:
        log(f"微信推送异常: {e}", "WARN")
        return False

def check_balance(channel_name, config):
    """查询渠道余额，返回(余额float或None)"""
    key = os.environ.get(config["key_env"], config["key_default"])
    try:
        req = urllib.request.Request(config["url"], headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        if config["parser"] == "deepseek":
            return float(data["balance_infos"][0]["total_balance"])
        elif config["parser"] == "kimi":
            return float(data["data"]["available_balance"])
    except Exception as e:
        log(f"查询{channel_name}余额失败: {e}", "WARN")
        return None

_last_alert_time = {}  # 去重: {告警key: 上次时间}

def should_alert(alert_key):
    """去重判断：30分钟内同问题只告警1次。返回True表示可以告警"""
    now = time.time()
    last = _last_alert_time.get(alert_key, 0)
    if now - last < ALERT_DEDUP_WINDOW:
        return False
    _last_alert_time[alert_key] = now
    return True

def run_balance_check():
    """第1层：余额监控，低余额告警"""
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for channel_name, config in BALANCE_ENDPOINTS.items():
        balance = check_balance(channel_name, config)
        if balance is None:
            continue
        if balance < BALANCE_ALERT_THRESHOLD:
            alert_key = f"balance_{channel_name}"
            if not should_alert(alert_key):
                continue
            title = f"🚨{channel_name}余额低"
            content = f"""**AIXX余额告警**

渠道：{channel_name}
当前余额：¥{balance:.2f}
阈值：¥{BALANCE_ALERT_THRESHOLD}
时间：{now_str}

**请尽快充值**"""
            log(f"触发余额告警: {channel_name} ¥{balance:.2f}")
            push_wechat(title, content)

_last_scanned_log_id = 0  # 日志水位线

def scan_error_logs():
    """第2层：扫描New-API日志，发现欠费/余额不足类错误就告警"""
    global _last_scanned_log_id
    try:
        conn = sqlite3.connect("/opt/aixx/new-api/one-api.db", timeout=5)
        cur = conn.cursor()
        # 首次运行：从最近100条错误日志开始扫（避免一次扫全表）
        if _last_scanned_log_id == 0:
            cur.execute("SELECT MAX(id) FROM logs WHERE type=2")
            row = cur.fetchone()
            _last_scanned_log_id = (row[0] or 0) - 100
        # 扫新增的错误日志（id大于水位线的）
        cur.execute("SELECT id, content, channel_name, model_name FROM logs WHERE type=2 AND id > ? ORDER BY id ASC", (_last_scanned_log_id,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        found_issues = {}  # {渠道: [(model, content)]}
        for log_id, content, channel_name, model_name in rows:
            _last_scanned_log_id = max(_last_scanned_log_id, log_id)
            # 检查是否是欠费类错误
            content_lower = (content or "").lower()
            if any(p.lower() in content_lower for p in INSUFFICIENT_BALANCE_PATTERNS):
                ch = channel_name or "未知渠道"
                found_issues.setdefault(ch, []).append((model_name, content[:80]))

        # 对发现的欠费错误告警（带去重）
        for channel, issues in found_issues.items():
            alert_key = f"insufficient_{channel}"
            if not should_alert(alert_key):
                continue
            title = f"🚨{channel}可能欠费"
            issue_text = "\n".join([f"- 模型{m}: {c}" for m, c in issues[:3]])
            content = f"""**AIXX欠费告警（从调用报错识别）**

渠道：{channel}
时间：{now_str}
检测到余额不足类错误：
{issue_text}

**请登录该渠道后台检查余额/充值**"""
            log(f"触发欠费告警: {channel} (从日志识别)")
            push_wechat(title, content)
    except Exception as e:
        log(f"扫描错误日志失败（非致命）: {e}", "WARN")

def run_fault_alert(states, prev):
    """第3层：渠道连续多次故障才告警，恢复时通知
    用连续失败计数器(_fault_counter)防误报：网络抖动导致偶尔一次超时不算故障，
    要连续FAULT_ALERT_THRESHOLD次（默认3次，即3分钟）都失败才告警。"""
    global _fault_counter
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for cid, state in states.items():
        curr_status = state["status"]
        prev_status = prev.get(cid, {}).get("status")
        name = state.get("name", f"渠道{cid}")

        # 健康→故障：要连续多次失败才告警（防网络抖动误报）
        if curr_status != "healthy":
            # 不健康：累加连续失败计数
            _fault_counter[cid] = _fault_counter.get(cid, 0) + 1
            fail_count = _fault_counter[cid]
            # 不足阈值：只记日志，不告警（给网络抖动一个缓冲）
            if fail_count < FAULT_ALERT_THRESHOLD:
                continue
            # 达到阈值：告警（注意去重逻辑should_alert保留，30分钟窗口防同一故障重复报）
            alert_key = f"fault_{cid}"
            if not should_alert(alert_key):
                continue
            title = f"🚨{name}渠道故障"
            content = f"""**AIXX渠道故障**

渠道：{name}（id:{cid}）
状态：{curr_status}
连续失败：{fail_count}次
原因：{state.get('msg', '未知')}
时间：{now_str}"""
            log(f"触发故障告警: {name} {curr_status}（连续失败{fail_count}次）")
            push_wechat(title, content)

        # 故障→恢复：清零失败计数，通知恢复
        elif curr_status == "healthy" and prev_status and prev_status != "healthy":
            _fault_counter[cid] = 0  # 恢复健康，清零失败计数
            title = f"✅{name}已恢复"
            content = f"渠道{name}已恢复正常。之前状态：{prev_status}"
            push_wechat(title, content)

# ============ 主循环 ============
def run_check():
    """执行一次巡检"""
    # 兜底：清理堆积session（防止后台登录爆满）
    cleanup_sessions()

    try:
        token = login()
    except Exception as e:
        log(f"管理员登录失败，跳过本轮: {e}", "ERROR")
        return

    try:
        channels = get_channels(token)
    except Exception as e:
        msg = str(e)
        # token失效（401/未授权）→ 清缓存重新登录一次
        if "401" in msg or "unauthorized" in msg.lower() or "无效" in msg:
            log(f"token失效，清除缓存重新登录: {msg}", "WARN")
            invalidate_token()
            try:
                token = login()
                channels = get_channels(token)
            except Exception as e2:
                log(f"重新登录后仍失败，跳过本轮: {e2}", "ERROR")
                return
        else:
            log(f"获取渠道列表失败: {msg}", "ERROR")
            return

    log(f"开始巡检 {len(channels)} 个渠道")

    prev = load_states().get("channels", {})
    states = {}
    health_count = 0
    issue_count = 0

    for ch in channels:
        cid = str(ch.get("id"))
        result = test_channel(ch, token)
        states[cid] = {
            **result,
            "channel_id": cid,
            "type": ch.get("type"),
            "models": ch.get("models", ""),
            "checked_at": datetime.now().isoformat()
        }

        # 状态变化告警
        prev_status = prev.get(cid, {}).get("status")
        curr_status = result["status"]

        if curr_status == "healthy":
            health_count += 1
            if prev_status and prev_status != "healthy":
                log(f"✅ 渠道恢复: {result['name']} (之前{prev_status})")
        else:
            issue_count += 1
            if prev_status != curr_status:
                log(f"🚨 渠道异常: {result['name']} 状态={curr_status} 原因={result['msg']}", "WARN")

    save_states(states)
    run_fault_alert(states, prev)  # 第3层：故障告警
    log(f"巡检完成: {health_count}健康 {issue_count}异常")

def main():
    log("=" * 50)
    log("AIXX哨兵bot启动（含告警系统：余额监控+报错识别+故障告警）")
    log(f"巡检间隔: {CHECK_INTERVAL}秒 | New-API: {NEWAPI_URL}")
    log(f"告警: 余额<{BALANCE_ALERT_THRESHOLD}元 + 欠费错误识别 + 渠道故障 → 微信推送")
    log("=" * 50)

    # 首次立即执行
    run_check()
    run_balance_check()  # 第1层
    scan_error_logs()    # 第2层

    balance_counter = 0
    error_scan_counter = 0
    while True:
        time.sleep(CHECK_INTERVAL)
        # 第3层故障告警随每轮巡检走
        try:
            run_check()
        except Exception as e:
            log(f"单次巡检失败（不影响bot运行）: {e}", "ERROR")
        # 第1层余额检查（每10分钟）
        balance_counter += 1
        if balance_counter * CHECK_INTERVAL >= BALANCE_CHECK_INTERVAL:
            balance_counter = 0
            try:
                run_balance_check()
            except Exception as e:
                log(f"余额检查失败: {e}", "ERROR")
        # 第2层报错扫描（每3分钟，比余额勤，因为要尽快发现欠费）
        error_scan_counter += 1
        if error_scan_counter * CHECK_INTERVAL >= 180:
            error_scan_counter = 0
            try:
                scan_error_logs()
            except Exception as e:
                log(f"报错扫描失败: {e}", "ERROR")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("哨兵bot手动停止")
        sys.exit(0)
    except Exception as e:
        log(f"哨兵bot崩溃: {e}", "ERROR")
        sys.exit(1)
