#!/usr/bin/env python3
"""
AIXX 接入bot（Integrator）
职责：渠道接入 + 配置指南生成
原则：只负责"加新渠道"和"生成配置文档"，不碰日常巡检（那是哨兵）

功能：
  1. add-channel: 添加新渠道到New-API
  2. list-channels: 列出所有渠道+状态
  3. gen-config: 为用户的agent生成配置指南（Claude Code/Cursor等）

运行：python3 integrator.py [命令] [参数]
依赖：仅Python标准库
"""

import json
import sys
import os
import urllib.request
from datetime import datetime

NEWAPI_URL = "http://localhost:8080"
ADMIN_USER = "root"
ADMIN_PASS = os.environ.get("AIXX_ADMIN_PASS", "")
if not ADMIN_PASS:
    print("[ERROR] 未设置AIXX_ADMIN_PASS环境变量，拒绝启动", flush=True)
    sys.exit(1)

# ============ 工具 ============
def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {ts} | {msg}", flush=True)

def api_request(path, method="GET", data=None, token=None):
    url = f"{NEWAPI_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def login():
    data = api_request("/api/user/login", "POST", {"username": ADMIN_USER, "password": ADMIN_PASS})
    return data["data"]["access_token"]

# ============ 渠道类型映射（New-API的type数字）============
CHANNEL_TYPES = {
    "openai": 1, "custom": 8, "anthropic": 14, "baidu": 15,
    "zhipu": 16, "glm": 16, "ali": 17, "qwen": 17,
    "moonshot": 25, "kimi": 25, "minimax": 35,
    "siliconflow": 40, "deepseek": 43, "xai": 48, "grok": 48,
    "volcengine": 45, "doubao": 45, "vidu": 52,
}

# ============ 命令：添加渠道 ============
def cmd_add_channel(args):
    """添加新渠道
    用法：python3 integrator.py add-channel <name> <type> <key> [models] [base_url]
    例：python3 integrator.py add-channel "Claude-apiyi" custom sk-xxx "claude-3-opus,claude-3-sonnet" "https://api.apiyi.com"
    """
    if len(args) < 4:
        print("用法: add-channel <名称> <类型> <key> [模型列表] [base_url]")
        print(f"类型可选: {', '.join(CHANNEL_TYPES.keys())}")
        return

    name = args[1]
    type_name = args[2].lower()
    key = args[3]
    models = args[4] if len(args) > 4 else ""
    base_url = args[5] if len(args) > 5 else ""

    if type_name not in CHANNEL_TYPES:
        # 如果传的是数字也支持
        if type_name.isdigit():
            type_id = int(type_name)
        else:
            print(f"❌ 未知类型: {type_name}")
            print(f"可选: {', '.join(CHANNEL_TYPES.keys())}")
            return
    else:
        type_id = CHANNEL_TYPES[type_name]

    token = login()
    data = api_request("/api/channel/", "POST", {
        "mode": "single",
        "channel": {
            "type": type_id,
            "name": name,
            "key": key,
            "models": models,
            "base_url": base_url,
            "group": "default",
            "groups": ["default"],
            "priority": 0,
            "weight": 100,
            "status": 1
        }
    }, token=token)

    if data.get("success"):
        print(f"✅ 渠道添加成功: {name} (type={type_id})")
        print(f"   模型: {models}")
    else:
        print(f"❌ 添加失败: {data.get('message')}")

# ============ 命令：列出渠道 ============
def cmd_list_channels(args):
    """列出所有渠道+状态"""
    token = login()
    data = api_request("/api/channel/?p=0&page_size=100", token=token)
    result = data.get("data")
    channels = result if isinstance(result, list) else result.get("items", [])

    # 读哨兵的状态
    states = {}
    try:
        with open("/opt/aixx/bots/sentinel/channel_states.json", "r") as f:
            states = json.load(f).get("channels", {})
    except Exception:
        pass

    print(f"\n{'ID':<4} {'名称':<25} {'类型':<6} {'状态':<10} {'健康':<8} {'模型'}")
    print("-" * 80)
    for ch in channels:
        cid = str(ch.get("id"))
        health = states.get(cid, {}).get("status", "未知")
        health_emoji = {"healthy": "🟢", "error": "🔴", "timeout": "🟡"}.get(health, "❓")
        status_str = "启用" if ch.get("status") == 1 else "禁用"
        print(f"{ch.get('id'):<4} {ch.get('name',''):<25} {ch.get('type'):<6} {status_str:<10} {health_emoji+' '+health:<8} {(ch.get('models','')[:30])}")

# ============ 命令：生成配置指南 ============
def cmd_gen_config(args):
    """为用户的agent生成配置指南
    用法：gen-config <agent类型> [用户key]
    例：gen-config claude-code
    """
    if len(args) < 2:
        print("用法: gen-config <claude-code|cursor|zcode|opencode>")
        return

    agent_type = args[1]
    user_key = args[2] if len(args) > 2 else "sk-你的key"
    base_url = "http://14.103.27.195:8080/v1"
    # Claude Code会自己补/v1/messages，base_url不能带/v1，否则变成/v1/v1/messages -> 404
    anthropic_base_url = "http://14.103.27.195:8080"

    configs = {
        "claude-code": f"""# Claude Code 配置

## 方式1：环境变量（推荐）
```bash
export ANTHROPIC_BASE_URL="{anthropic_base_url}"
export ANTHROPIC_AUTH_TOKEN="{user_key}"
```

## 方式2：配置文件
编辑 ~/.claude.json：
```json
{{
  "primaryApiKey": "{user_key}",
  "apiBaseUrl": "{anthropic_base_url}"
}}
```

然后直接用 claude 命令，模型走AIXX。
""",
        "cursor": f"""# Cursor 配置

Settings → Models → OpenAI API:
- API Key: {user_key}
- Base URL: {base_url}
- 勾选 Override

模型名用: deepseek-chat 或 glm-4-flash
""",
        "zcode": f"""# ZCode 配置

在ZCode的环境变量或配置中设置：
- AIXX_API_KEY={user_key}
- AIXX_BASE_URL={base_url}

或直接装skill: npx aixx-cli install
""",
        "opencode": f"""# OpenCode / 通用OpenAI兼容配置

Base URL: {base_url}
API Key: {user_key}
Model: deepseek-chat
""",
    }

    if agent_type not in configs:
        print(f"不支持的agent类型: {agent_type}")
        print(f"可选: {', '.join(configs.keys())}")
        return

    print(configs[agent_type])

# ============ 命令：查看帮助 ============
def cmd_help():
    print("""
AIXX 接入bot（Integrator）
职责：渠道接入 + 配置生成

命令：
  add-channel <名称> <类型> <key> [模型] [base_url]   添加新渠道
  list-channels                                        列出所有渠道+健康状态
  gen-config <claude-code|cursor|zcode|opencode> [key] 生成配置指南
  help                                                 显示此帮助

渠道类型：
  deepseek(43) glm(16) kimi(25) minimax(35)
  openai(1) anthropic(14) custom(8)
  siliconflow(40) xai(48) doubao(45)

示例：
  python3 integrator.py add-channel "Claude-apiyi" custom sk-xxx "claude-3-opus" "https://api.apiyi.com"
  python3 integrator.py list-channels
  python3 integrator.py gen-config claude-code sk-xxxx
""")

# ============ 主入口 ============
def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    cmd = sys.argv[1]
    args = sys.argv[1:]

    if cmd == "add-channel":
        cmd_add_channel(args)
    elif cmd == "list-channels":
        cmd_list_channels(args)
    elif cmd == "gen-config":
        cmd_gen_config(args)
    elif cmd in ("help", "-h", "--help"):
        cmd_help()
    else:
        print(f"未知命令: {cmd}")
        cmd_help()

if __name__ == "__main__":
    main()
