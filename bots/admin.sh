#!/usr/bin/env bash
# AIXX 后台管理脚本
# 给龙龙/K哥用的运维工具箱
#
# 用法：./admin.sh [命令]
# 命令：
#   status        查看AIXX整体状态（服务+渠道+用户+收款）
#   users         查看所有用户
#   channels      查看所有渠道+健康（调接入bot）
#   quota <用户名> <额度>   给用户加额度
#   logs [行数]   看最新日志
#   restart       重启New-API+哨兵bot
#   backup        备份数据库
#   help          帮助

set -e

SSH_KEY="${HOME}/.ssh/aixx_key"
SERVER="aixx@14.103.27.195"
NEWAPI_URL="http://localhost:8080"
ADMIN_USER="root"
ADMIN_PASS="${AIXX_ADMIN_PASS:-}"
if [ -z "$ADMIN_PASS" ]; then
    echo "❌ 未设置AIXX_ADMIN_PASS环境变量，拒绝执行" >&2
    exit 1
fi

# 远程执行
re() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "$1"
}

# ============ 命令实现 ============

cmd_status() {
    echo "╔══════════════════════════════════════════╗"
    echo "║      AIXX 系统状态                         ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    echo "=== 服务状态 ==="
    re "systemctl is-active aixx-newapi aixx-sentinel 2>&1 | xargs echo '  New-API / 哨兵bot:'"
    echo ""
    echo "=== 渠道状态 ==="
    re "python3 /opt/aixx/bots/integrator/integrator.py list-channels 2>&1"
    echo ""
    echo "=== 用户统计 ==="
    re "sqlite3 /opt/aixx/new-api/one-api.db 'SELECT COUNT(*) as 用户数, SUM(quota) as 总额度 FROM users;'"
    echo ""
    echo "=== 最近注册 ==="
    re "sqlite3 /opt/aixx/new-api/one-api.db 'SELECT username, created_at FROM users ORDER BY id DESC LIMIT 5;'"
    echo ""
    echo "=== 服务器资源 ==="
    re "echo '内存:' \$(free -h | awk '/Mem/{print \$3\"/\"\$2}') && echo '磁盘:' \$(df -h / | awk 'NR==2{print \$3\"/\"\$2\" (\"\$5\")\"}')"
}

cmd_users() {
    echo "=== AIXX 所有用户 ==="
    re "sqlite3 -header -column /opt/aixx/new-api/one-api.db 'SELECT id, username, role, status, quota, used_quota FROM users;'"
}

cmd_channels() {
    re "python3 /opt/aixx/bots/integrator/integrator.py list-channels"
}

cmd_quota() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "用法: quota <用户名> <额度>"
        echo "例: quota testuser 1000000"
        return
    fi
    [[ "$2" =~ ^[0-9]+$ ]] || { echo "❌ 额度必须是数字"; return 1; }
    [[ "$1" =~ ^[a-zA-Z0-9_]+$ ]] || { echo "❌ 用户名含非法字符"; return 1; }
    re "sqlite3 /opt/aixx/new-api/one-api.db \"UPDATE users SET quota = quota + $2 WHERE username = '$1'; SELECT username, quota FROM users WHERE username='$1';\""
    echo "✅ 已给 $1 加 $2 额度"
}

cmd_logs() {
    LINES=${1:-30}
    echo "=== New-API 最新 $LINES 行日志 ==="
    re "tail -$LINES /var/log/aixx-newapi.log"
}

cmd_restart() {
    echo "=== 重启服务 ==="
    re "echo '需要root权限重启，用root执行...'" 2>&1
    ssh -o StrictHostKeyChecking=no root@14.103.27.195 "systemctl restart aixx-newapi aixx-sentinel && sleep 2 && systemctl is-active aixx-newapi aixx-sentinel"
    echo "✅ 重启完成"
}

cmd_backup() {
    echo "=== 备份数据库 ==="
    re "mkdir -p /opt/aixx/backup && cd /opt/aixx/new-api && sqlite3 one-api.db \".backup /opt/aixx/backup/one-api_\$(date +%Y%m%d_%H%M%S).db\" && echo '✅ 备份完成' && ls -la /opt/aixx/backup/ | tail -5"
}

cmd_help() {
    echo "
AIXX 后台管理脚本
用法: ./admin.sh [命令]

命令：
  status                  查看整体状态（服务+渠道+用户+资源）
  users                   查看所有用户
  channels                查看渠道+健康状态
  quota <用户名> <额度>    给用户加额度
  logs [行数]             看最新日志（默认30行）
  restart                 重启New-API+哨兵bot
  backup                  备份数据库
  help                    显示此帮助
"
}

# ============ 主入口 ============
case "${1:-help}" in
    status) cmd_status ;;
    users) cmd_users ;;
    channels) cmd_channels ;;
    quota) shift; cmd_quota "$@" ;;
    logs) shift; cmd_logs "$@" ;;
    restart) cmd_restart ;;
    backup) cmd_backup ;;
    help|--help|-h) cmd_help ;;
    *) echo "未知命令: $1"; cmd_help ;;
esac
