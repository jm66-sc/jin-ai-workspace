#!/bin/bash

# SmartScout 依赖安装脚本
# 此脚本帮助安装运行 SmartScout 所需的依赖

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SmartScout 依赖安装助手 ===${NC}"
echo "此脚本将帮助安装运行 SmartScout 所需的依赖"
echo ""

# 检查系统类型
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    echo -e "${RED}不支持的操作系统: $OSTYPE${NC}"
    exit 1
fi

echo -e "${GREEN}检测到操作系统: $OS${NC}"
echo ""

# 检查当前已安装的依赖
check_dependency() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓ 已安装: $1${NC}"
        return 0
    else
        echo -e "${RED}✗ 未安装: $1${NC}"
        return 1
    fi
}

echo -e "${YELLOW}检查当前依赖状态...${NC}"
check_dependency "python3"
PYTHON_INSTALLED=$?
check_dependency "node"
NODE_INSTALLED=$?
check_dependency "npm"
NPM_INSTALLED=$?

echo ""

# 如果所有依赖都已安装
if [ $PYTHON_INSTALLED -eq 0 ] && [ $NODE_INSTALLED -eq 0 ] && [ $NPM_INSTALLED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有依赖都已安装！${NC}"
    echo "SmartScout 可以正常运行。"
    exit 0
fi

echo -e "${YELLOW}缺少以下依赖:${NC}"
[ $PYTHON_INSTALLED -ne 0 ] && echo "• Python 3 (python3)"
[ $NODE_INSTALLED -ne 0 ] && echo "• Node.js (node)"
[ $NPM_INSTALLED -ne 0 ] && echo "• npm (通常随 Node.js 一起安装)"

echo ""
echo -e "${BLUE}请选择安装方式:${NC}"
echo "1. 自动安装（推荐）"
echo "2. 手动安装指导"
echo "3. 退出"
echo ""
read -p "请输入选项 [1-3]: " choice

case $choice in
    1)
        echo -e "${YELLOW}开始自动安装...${NC}"

        # macOS 自动安装
        if [ "$OS" = "macOS" ]; then
            echo "检测到 macOS，使用 Homebrew 进行安装"

            # 检查是否已安装 Homebrew
            if ! command -v brew &> /dev/null; then
                echo -e "${YELLOW}正在安装 Homebrew...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

                # 配置环境变量（针对 Apple Silicon Mac）
                if [[ $(uname -m) == "arm64" ]]; then
                    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
            fi

            # 安装 Python 3（如果需要）
            if [ $PYTHON_INSTALLED -ne 0 ]; then
                echo -e "${YELLOW}正在安装 Python 3...${NC}"
                brew install python@3.11
            fi

            # 安装 Node.js（如果需要）
            if [ $NODE_INSTALLED -ne 0 ]; then
                echo -e "${YELLOW}正在安装 Node.js (包含 npm)...${NC}"
                brew install node@18

                # 配置环境变量
                echo 'export PATH="/usr/local/opt/node@18/bin:$PATH"' >> ~/.zprofile
                source ~/.zprofile
            fi

        else
            # Linux 自动安装
            echo "检测到 Linux，使用系统包管理器"
            echo "此功能需要管理员权限 (sudo)"

            # 检查包管理器
            if command -v apt-get &> /dev/null; then
                # Debian/Ubuntu
                echo "使用 apt-get 安装"

                # 安装 Python 3（如果需要）
                if [ $PYTHON_INSTALLED -ne 0 ]; then
                    echo -e "${YELLOW}正在安装 Python 3...${NC}"
                    sudo apt-get update
                    sudo apt-get install -y python3 python3-pip
                fi

                # 安装 Node.js（如果需要）
                if [ $NODE_INSTALLED -ne 0 ]; then
                    echo -e "${YELLOW}正在安装 Node.js...${NC}"
                    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                    sudo apt-get install -y nodejs
                fi

            elif command -v yum &> /dev/null; then
                # CentOS/RHEL
                echo "使用 yum 安装"

                # 安装 Python 3（如果需要）
                if [ $PYTHON_INSTALLED -ne 0 ]; then
                    echo -e "${YELLOW}正在安装 Python 3...${NC}"
                    sudo yum install -y python3 python3-pip
                fi

                # 安装 Node.js（如果需要）
                if [ $NODE_INSTALLED -ne 0 ]; then
                    echo -e "${YELLOW}正在安装 Node.js...${NC}"
                    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                    sudo yum install -y nodejs
                fi
            else
                echo -e "${RED}无法识别包管理器，请手动安装${NC}"
                exit 1
            fi
        fi

        # 验证安装
        echo ""
        echo -e "${YELLOW}验证安装结果...${NC}"
        check_dependency "python3"
        check_dependency "node"
        check_dependency "npm"

        echo ""
        echo -e "${GREEN}✓ 安装完成！${NC}"
        echo "现在可以运行 SmartScout 了。"
        ;;

    2)
        echo -e "${BLUE}=== 手动安装指导 ===${NC}"
        echo ""

        if [ "$OS" = "macOS" ]; then
            echo "macOS 安装方法:"
            echo ""

            if [ $PYTHON_INSTALLED -ne 0 ]; then
                echo "1. 安装 Python 3:"
                echo "   方法 A: 使用 Homebrew"
                echo "     brew install python@3.11"
                echo "   方法 B: 从官网下载"
                echo "     https://www.python.org/downloads/macos/"
                echo ""
            fi

            if [ $NODE_INSTALLED -ne 0 ]; then
                echo "2. 安装 Node.js (包含 npm):"
                echo "   方法 A: 使用 Homebrew"
                echo "     brew install node@18"
                echo "   方法 B: 从官网下载"
                echo "     https://nodejs.org/"
                echo "   方法 C: 使用 nvm (推荐)"
                echo "     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
                echo "     然后重新打开终端，运行: nvm install 18"
                echo ""
            fi

        else
            echo "Linux 安装方法:"
            echo ""

            if [ $PYTHON_INSTALLED -ne 0 ]; then
                echo "1. 安装 Python 3:"
                echo "   Debian/Ubuntu: sudo apt-get install python3 python3-pip"
                echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
                echo ""
            fi

            if [ $NODE_INSTALLED -ne 0 ]; then
                echo "2. 安装 Node.js:"
                echo "   推荐使用 nvm (Node Version Manager):"
                echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
                echo "   然后重新打开终端，运行: nvm install 18"
                echo ""
            fi
        fi

        echo "安装完成后，请重新运行 SmartScout 启动器。"
        ;;

    3)
        echo "退出安装"
        exit 0
        ;;

    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac