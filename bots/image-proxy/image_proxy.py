#!/usr/bin/env python3
"""
AIXX 豆包生图代理（Image Proxy）
职责：把火山方舟的生图接口封装成 OpenAI 兼容格式
原因：New-API 的火山方舟渠道（type=45）只支持对话转发，不支持图片生成转发
      （调生图会报 "invalid image request type"）。这是 New-API 已知缺陷
      （issue #3127，2026-03 提交至今没人理）。所以 AIXX 自己写个薄代理绕过这个洞。

工作方式：
  - 监听 0.0.0.0:8090
  - 接收 OpenAI 格式的 POST /v1/images/generations（用户/agent 像调普通 OpenAI 生图一样调）
  - 把用户友好的模型名映射成火山真实模型名
  - 转发到火山方舟生图接口（用 ARK_API_KEY 鉴权）
  - 把火山响应精简成标准 OpenAI 格式返回
  - GET /health 健康检查，返回 {"status":"ok"}，给 systemd 和 New-API 探活用

运行：python3 image_proxy.py  （或 systemd 托管）
依赖：仅 Python 标准库（http.server + urllib，零依赖，参照 sentinel.py 风格）
"""

import json
import os
import sys
import threading
import urllib.request
import urllib.error
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ============ 配置 ============
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8090

# 火山方舟生图接口地址（PM 已实测确认）
ARK_BASE_URL = "https://ark.cn-beijing.volces.com"
ARK_IMAGES_PATH = "/api/v3/images/generations"

# 火山方舟 API Key（从环境变量读，绝不硬编码——红线）
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")

# 生图接口超时（秒）：生图慢，给足 120 秒（对话类接口 10 秒够，生图不够）
ARK_TIMEOUT = 120

# 请求体大小上限（字节）：生图请求 2MB 足够，防止超大 Content-Length 撑爆内存
MAX_BODY = 2 * 1024 * 1024

# 日志文件路径（可被环境变量覆盖，方便本地测试）
LOG_FILE = os.environ.get("IMAGE_PROXY_LOG_FILE", "/opt/aixx/bots/logs/image-proxy.log")

# ============ 模型名映射表 ============
# 用户传友好名（如 doubao-seedream），代理转成火山真实模型名。
# 直接传火山全名（如 doubao-seedream-5-0-pro-260628）也认，会原样透传交给火山。
MODEL_ALIASES = {
    "doubao-seedream": "doubao-seedream-5-0-pro-260628",        # 默认主力
    "doubao-seedream-5-0-pro": "doubao-seedream-5-0-pro-260628",
    "doubao-seedream-4-0": "doubao-seedream-4-0-250828",
}

# 启动前校验：缺 API Key 拒绝启动（和 sentinel 校验 ADMIN_PASS 一个思路）
if not ARK_API_KEY:
    print("[ERROR] 未设置 ARK_API_KEY 环境变量，拒绝启动", flush=True)
    sys.exit(1)

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

def resolve_model(user_model):
    """把用户传的友好模型名映射成火山真实模型名。
    命中映射表就替换；没命中（已经是全名或未知）就原样返回，让火山自己处理/报错。"""
    if not user_model:
        return "doubao-seedream-5-0-pro-260628"  # 没传 model 时用默认主力
    return MODEL_ALIASES.get(user_model, user_model)


class ArkError(Exception):
    """调火山方舟失败时用的异常，带 HTTP 状态码（透传给用户）"""
    def __init__(self, message, http_status=502):
        super().__init__(message)
        self.http_status = http_status


def call_ark(payload):
    """调火山方舟生图接口，返回解析后的 JSON 响应 dict。
    失败抛 ArkError，异常 message 已带火山返回的原始错误信息。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{ARK_BASE_URL}{ARK_IMAGES_PATH}",
        data=body,
        headers={
            "Authorization": f"Bearer {ARK_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=ARK_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 火山报错（4xx/5xx）：把响应体读出来，封装成可读错误给上层
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        # 火山的4xx（401/403/429等）统一映射成502，避免误导客户端以为是自己的鉴权问题
        # 实际是代理后端ARK_API_KEY的问题。日志里保留原始code方便排查。
        log(f"火山方舟返回 HTTP {e.code}: {err_body[:200]}", "WARN")
        raise ArkError(f"上游火山方舟错误（原始HTTP {e.code}）", http_status=502)
    except urllib.error.URLError as e:
        # 网络层错误（超时/连不上火山）
        raise ArkError(f"连接火山方舟失败: {e}", http_status=502)


# ============ HTTP 请求处理 ============
class ImageProxyHandler(BaseHTTPRequestHandler):
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
        """POST 路由：/v1/images/generations"""
        path = self.path.split("?", 1)[0]
        if path != "/v1/images/generations":
            self._send_openai_error(404, f"路径不存在: {self.path}", "not_found")
            return

        # 1. 读请求体
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

        prompt = req_json.get("prompt", "")
        user_model = req_json.get("model", "")

        # prompt 必填校验（OpenAI 标准里 prompt 是必填）
        if not prompt:
            self._send_openai_error(400, "缺少必填字段 prompt", "invalid_request_error")
            return

        # 2. 模型名映射：友好名 -> 火山真实名
        ark_model = resolve_model(user_model)

        # 3. 组装火山请求体：模型名用映射后的，透传 prompt/n/size，固定返回 url
        ark_payload = {
            "model": ark_model,
            "prompt": prompt,
            "response_format": "url",
        }
        if "n" in req_json:
            ark_payload["n"] = req_json["n"]
        if "size" in req_json:
            ark_payload["size"] = req_json["size"]

        prompt_preview = prompt[:30]  # 日志里只记前 30 字（prompt 可能很长/含敏感信息）
        log(f"收到生图请求 model={user_model}->{ark_model} prompt={prompt_preview!r}")

        # 4. 转发到火山方舟
        try:
            ark_resp = call_ark(ark_payload)
        except ArkError as e:
            log(f"生图失败 model={ark_model} prompt={prompt_preview!r} 原因={e}", "ERROR")
            self._send_openai_error(e.http_status, str(e), "upstream_error")
            return
        except Exception as e:
            log(f"生图异常 model={ark_model} prompt={prompt_preview!r} 异常={e}", "ERROR")
            self._send_openai_error(500, f"代理内部错误: {e}", "internal_error")
            return

        # 5. 精简成 OpenAI 标准格式返回（data[].url，加 created 字段）
        try:
            ark_data = ark_resp.get("data", [])
            openai_data = []
            for item in ark_data:
                # 标准 OpenAI 格式只保留 url（或 b64_json）。火山默认返回 url。
                entry = {}
                if "url" in item:
                    entry["url"] = item["url"]
                if "b64_json" in item:
                    entry["b64_json"] = item["b64_json"]
                # 万一一条都没有（异常情况），原样透传整个 item 兜底
                openai_data.append(entry if entry else item)

            openai_resp = {
                "created": ark_resp.get("created", int(datetime.now().timestamp())),
                "data": openai_data,
            }
            log(f"生图成功 model={ark_model} prompt={prompt_preview!r} 数量={len(openai_data)}")
            self._send_json(200, openai_resp)
        except Exception as e:
            log(f"组装响应失败 model={ark_model} 异常={e} 原始={ark_resp}", "ERROR")
            self._send_openai_error(500, f"代理组装响应失败: {e}", "internal_error")


# ============ 启动入口 ============
def main():
    # ThreadingHTTPServer：每个请求开一个线程，生图慢不会阻塞别的请求
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), ImageProxyHandler)
    log("=" * 50)
    log("AIXX 豆包生图代理启动")
    log(f"监听: {LISTEN_HOST}:{LISTEN_PORT}")
    log(f"火山方舟: {ARK_BASE_URL} 超时={ARK_TIMEOUT}秒")
    log(f"模型映射: {MODEL_ALIASES}")
    log(f"日志文件: {LOG_FILE}（同时输出到 stdout/journal）")
    log("鉴权: 不校验请求方 Authorization（由前面的 New-API 负责）")
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
