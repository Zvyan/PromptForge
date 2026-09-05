#!/usr/bin/env bash
# PromptForge Web UI 一键启动脚本 (Linux / macOS / WSL)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "======================================================================"
echo "   🚀 欢迎启动 PromptForge — 多平台 Agent 规范提示词引擎"
echo "   ⚡ 9 大场景分类 | 56 套工程级模板 | 8 大平台适配 | 实战预设支持"
echo "======================================================================"
echo ""

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "[错误] 未检测到 Python 环境，请先安装 Python 3.11+。"
        exit 1
    fi
fi

echo "[1/2] 正在启动 PromptForge Web 工作台..."
echo "[2/2] 访问地址: http://127.0.0.1:8000"
echo "提示: 按 Ctrl + C 即可安全退出服务。"
echo "----------------------------------------------------------------------"
echo ""

$PYTHON_CMD run.py web
