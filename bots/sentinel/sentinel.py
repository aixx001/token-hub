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
import os
import sys
from datetime import datetime

# ============ 配置 ============
NEWAPI_URL = "http://localhost:8080"
ADMIN_USER = "root"
ADMIN_PASS = os.environ.get("AIXX_ADMIN_PASS", "Aixx@2026!K8")
CHECK_INTERVAL = 60  # 巡检间隔（秒）
TIMEOUT = 10  # 单次ping超时（秒）
STATE_FILE = "/opt/aixx/bots/sentinel/channel_states.json"
LOG_FILE = "/opt/aixx/bots/logs/sentinel.log"

# ============ 工具函数 ============
def log(msg, level="INFO"):
    """记日志"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{level}] {ts} | {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

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
    """管理员登录拿token"""
    data = api_request("/api/user/login", "POST", {"username": ADMIN_USER, "password": ADMIN_PASS})
    if not data.get("success"):
        raise Exception(f"登录失败: {data.get('message')}")
    return data["data"]["access_token"]

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

# ============ 主循环 ============
def run_check():
    """执行一次巡检"""
    try:
        token = login()
    except Exception as e:
        log(f"管理员登录失败，跳过本轮: {e}", "ERROR")
        return

    try:
        channels = get_channels(token)
    except Exception as e:
        log(f"获取渠道列表失败: {e}", "ERROR")
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
    log(f"巡检完成: {health_count}健康 {issue_count}异常")

def main():
    log("=" * 50)
    log("AIXX哨兵bot启动")
    log(f"巡检间隔: {CHECK_INTERVAL}秒 | New-API: {NEWAPI_URL}")
    log("=" * 50)

    # 首次立即巡检
    run_check()

    # 定时循环
    while True:
        time.sleep(CHECK_INTERVAL)
        run_check()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("哨兵bot手动停止")
        sys.exit(0)
    except Exception as e:
        log(f"哨兵bot崩溃: {e}", "ERROR")
        sys.exit(1)
