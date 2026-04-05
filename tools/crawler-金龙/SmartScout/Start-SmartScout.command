#!/bin/bash

# SmartScout macOS 启动器
# 双击此文件将在终端中启动 SmartScout 系统

echo "========================================"
echo "   SmartScout 智能招标爬虫系统"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "项目目录: $SCRIPT_DIR"
echo ""

# 检查是否已安装必要命令
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "错误: 未找到 $1"
        echo "请先安装 $1"
        exit 1
    fi
}

echo "检查系统依赖..."
check_command "python3"
check_command "node"
check_command "npm"

echo "✓ 所有依赖检查通过"
echo ""

# 检查服务是否已在运行
check_running() {
    echo "检查服务状态..."

    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ 后端服务已在运行 (端口 8000)"
        BACKEND_RUNNING=true
    else
        echo "○ 后端服务未运行"
        BACKEND_RUNNING=false
    fi

    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo "✓ 前端服务已在运行 (端口 3001)"
        FRONTEND_RUNNING=true
    else
        echo "○ 前端服务未运行"
        FRONTEND_RUNNING=false
    fi

    echo ""
}

check_running

# 如果服务都在运行，直接打开浏览器
if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
    echo "所有服务已在运行，正在打开浏览器..."
    sleep 1
    open "http://localhost:3001"

    echo ""
    echo "访问地址:"
    echo "• 前端界面: http://localhost:3001"
    echo "• 后端API:  http://localhost:8000"
    echo "• API文档: http://localhost:8000/docs"
    echo ""
    echo "按 Enter 键退出..."
    read -r
    exit 0
fi

# 显示启动选项
echo "请选择操作:"
echo "1. 启动完整系统（前端 + 后端）"
echo "2. 仅启动后端服务"
echo "3. 仅启动前端服务"
echo "4. 退出"
echo ""
read -p "请输入选项 [1-4]: " choice

case $choice in
    1)
        echo "正在启动完整系统..."
        ./run_all.sh
        ;;
    2)
        echo "正在启动后端服务..."
        python3 run.py
        ;;
    3)
        echo "正在启动前端服务..."
        cd frontend
        npm run dev
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项，退出"
        exit 1
        ;;
esac

echo ""
echo "SmartScout 系统已停止"
echo "按 Enter 键关闭窗口..."
read -r