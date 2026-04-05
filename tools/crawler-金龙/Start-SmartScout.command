#!/bin/bash

# SmartScout macOS 启动器
# 双击此文件将在终端中启动 SmartScout 系统

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "   SmartScout 智能招标爬虫系统"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "项目目录: $SCRIPT_DIR"
echo ""

# 检查依赖函数
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓ 已安装: $1${NC}"
        return 0
    else
        echo -e "${RED}✗ 未安装: $1${NC}"
        return 1
    fi
}

echo -e "${YELLOW}检查系统依赖...${NC}"
check_command "python3"
PYTHON_INSTALLED=$?
check_command "node"
NODE_INSTALLED=$?
check_command "npm"
NPM_INSTALLED=$?

# 检查所有依赖是否都已安装
ALL_DEPS_INSTALLED=true
if [ $PYTHON_INSTALLED -ne 0 ] || [ $NODE_INSTALLED -ne 0 ] || [ $NPM_INSTALLED -ne 0 ]; then
    ALL_DEPS_INSTALLED=false
fi

echo ""

# 如果缺少依赖，提供安装选项
if [ "$ALL_DEPS_INSTALLED" = false ]; then
    echo -e "${YELLOW}缺少必要的依赖！${NC}"
    echo ""
    echo "SmartScout 需要以下依赖才能运行:"
    [ $PYTHON_INSTALLED -ne 0 ] && echo "• Python 3"
    [ $NODE_INSTALLED -ne 0 ] && echo "• Node.js"
    [ $NPM_INSTALLED -ne 0 ] && echo "• npm"
    echo ""
    echo "请选择操作:"
    echo "1. 自动安装依赖（推荐）"
    echo "2. 手动安装指导"
    echo "3. 继续尝试运行（可能失败）"
    echo "4. 退出"
    echo ""
    read -p "请输入选项 [1-4]: " install_choice

    case $install_choice in
        1)
            echo -e "${YELLOW}正在启动依赖安装助手...${NC}"
            if [ -f "./install-dependencies.sh" ]; then
                chmod +x ./install-dependencies.sh
                ./install-dependencies.sh

                # 重新检查依赖
                echo ""
                echo -e "${YELLOW}重新检查依赖...${NC}"
                check_command "python3"
                PYTHON_INSTALLED=$?
                check_command "node"
                NODE_INSTALLED=$?
                check_command "npm"
                NPM_INSTALLED=$?

                if [ $PYTHON_INSTALLED -ne 0 ] || [ $NODE_INSTALLED -ne 0 ] || [ $NPM_INSTALLED -ne 0 ]; then
                    echo -e "${RED}依赖安装不完整，请重新运行安装程序。${NC}"
                    echo "按 Enter 键退出..."
                    read -r
                    exit 1
                else
                    echo -e "${GREEN}✓ 所有依赖安装成功！${NC}"
                    echo ""
                fi
            else
                echo -e "${RED}找不到依赖安装脚本${NC}"
                echo "请从项目目录运行此脚本。"
                echo "按 Enter 键退出..."
                read -r
                exit 1
            fi
            ;;
        2)
            echo -e "${BLUE}=== 手动安装指导 ===${NC}"
            echo ""
            echo "macOS 安装方法:"
            echo ""
            echo "1. 安装 Python 3:"
            echo "   方法 A: 使用 Homebrew"
            echo "     brew install python@3.11"
            echo "   方法 B: 从官网下载"
            echo "     https://www.python.org/downloads/macos/"
            echo ""
            echo "2. 安装 Node.js (包含 npm):"
            echo "   方法 A: 使用 Homebrew"
            echo "     brew install node@18"
            echo "   方法 B: 从官网下载"
            echo "     https://nodejs.org/"
            echo "   方法 C: 使用 nvm (推荐)"
            echo "     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
            echo "     然后重新打开终端，运行: nvm install 18"
            echo ""
            echo "安装完成后，请重新运行此启动器。"
            echo "按 Enter 键退出..."
            read -r
            exit 0
            ;;
        3)
            echo -e "${YELLOW}警告: 缺少依赖，继续运行可能失败！${NC}"
            echo ""
            ;;
        4)
            echo "退出"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项${NC}"
            echo "按 Enter 键退出..."
            read -r
            exit 1
            ;;
    esac
else
    echo -e "${GREEN}✓ 所有依赖检查通过${NC}"
    echo ""
fi

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