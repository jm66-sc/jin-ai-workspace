#!/bin/bash
# =============================================================================
# SmartScout 一键启动脚本
# 功能：自动检测依赖、校验配置、启动后端+前端服务
# 使用：双击运行，或在终端执行 ./start.sh
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路径设置
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SmartScout 一键启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# 1. 检查 Python 环境
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/6] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3，请先安装 Python 3.10+${NC}"
    echo "   Mac: brew install python@3.11"
    echo "   官网: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "   Python 版本: $PYTHON_VERSION ✓"

# -----------------------------------------------------------------------------
# 2. 检查并安装依赖
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[2/6] 检查依赖包...${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "   创建虚拟环境..."
    python3 -m venv venv
    echo -e "   虚拟环境已创建 ✓"
fi

# 激活虚拟环境
source venv/bin/activate

# 检查核心依赖
MISSING_DEPS=()
for pkg in crawl4ai fastapi uvicorn openai bs4; do
    if ! pip show "$pkg" &> /dev/null 2>&1; then
        MISSING_DEPS+=("$pkg")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "   安装缺失依赖: ${MISSING_DEPS[*]}"
    pip install -r requirements.txt -q
    echo -e "   依赖安装完成 ✓"
else
    echo -e "   依赖已完整 ✓"
fi

# -----------------------------------------------------------------------------
# 3. 检查配置文件
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[3/6] 检查配置文件...${NC}"

if [ ! -f "config/secrets.yaml" ]; then
    if [ -f "config/secrets.yaml.template" ]; then
        cp config/secrets.yaml.template config/secrets.yaml
        echo -e "   已从模板创建 config/secrets.yaml"
    else
        echo -e "${RED}❌ 配置文件不存在: config/secrets.yaml${NC}"
        exit 1
    fi
fi

# 提取 API Key
API_KEY=$(grep "api_key:" config/secrets.yaml | sed 's/.*api_key: *//' | sed 's/[[:space:]]*$//' | sed "s/['\"]//g")

if [ -z "$API_KEY" ] || [ "$API_KEY" = "YOUR_API_KEY_HERE" ] || [ "$API_KEY" = "sk-xxx" ]; then
    echo -e "${RED}❌ API Key 未配置！${NC}"
    echo ""
    echo -e "${YELLOW}请编辑 config/secrets.yaml，填入你的 DeepSeek API Key:${NC}"
    echo ""
    echo "   1. 打开 config/secrets.yaml"
    echo "   2. 找到 api_key: 那一行"
    echo "   3. 把 YOUR_API_KEY_HERE 替换成你的实际 Key"
    echo ""
    echo "   示例:"
    echo "   ${GREEN}api_key: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx${NC}"
    echo ""
    read -p "   按回车打开配置文件..."
    open config/secrets.yaml
    exit 1
fi

echo -e "   配置文件存在 ✓"

# -----------------------------------------------------------------------------
# 4. 校验 API Key 有效性
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[4/6] 校验 API Key...${NC}"

# 临时测试文件
TEST_FILE="/tmp/smartscout_apikey_test_$$.py"

cat > "$TEST_FILE" << 'EOF'
import sys
sys.path.insert(0, "src")
from openai import OpenAI

# 读取配置
import yaml
with open("config/secrets.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = config.get("deepseek", {}).get("api_key", "")
base_url = config.get("deepseek", {}).get("base_url", "https://api.deepseek.com/v1")

if not api_key or api_key in ["YOUR_API_KEY_HERE", "sk-xxx"]:
    print("EMPTY_KEY")
    sys.exit(1)

try:
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=5
    )
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF

# 先检查是否有 PyYAML
if ! pip show pyyaml &> /dev/null 2>&1; then
    pip install pyyaml -q
fi

# 运行测试
TEST_RESULT=$(python3 "$TEST_FILE" 2>&1)
rm -f "$TEST_FILE"

if echo "$TEST_RESULT" | grep -q "OK"; then
    echo -e "   API Key 有效 ✓"
else
    echo -e "${RED}❌ API Key 无效！${NC}"
    echo ""
    echo -e "${YELLOW}错误信息:${NC} $TEST_RESULT"
    echo ""
    echo -e "${YELLOW}请检查 config/secrets.yaml 中的 api_key 是否正确${NC}"
    read -p "   按回车打开配置文件..."
    open config/secrets.yaml
    exit 1
fi

# -----------------------------------------------------------------------------
# 5. 检查端口并启动服务
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[5/6] 启动服务...${NC}"

# 检查端口占用
check_port() {
    lsof -i:$1 >/dev/null 2>&1
}

start_backend() {
    if check_port 8000; then
        echo -e "   后端服务 (8000) 已在运行 ✓"
    else
        echo -e "   启动后端服务..."
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
        sleep 3
        if check_port 8000; then
            echo -e "   后端服务已启动 ✓"
        else
            echo -e "${RED}❌ 后端服务启动失败，请查看 logs/backend.log${NC}"
        fi
    fi
}

start_frontend() {
    if check_port 3001; then
        echo -e "   前端服务 (3001) 已在运行 ✓"
    else
        echo -e "   启动前端服务..."
        # 检查 Node.js
        if ! command -v npm &> /dev/null; then
            echo -e "   ${YELLOW}⚠️ 未找到 npm，跳过前端启动${NC}"
            echo -e "   ${YELLOW}  如需前端，请先安装 Node.js: brew install node${NC}"
            return
        fi
        
        # 检查前端依赖
        if [ ! -d "node_modules" ]; then
            echo -e "   安装前端依赖..."
            npm install --prefix frontend >/dev/null 2>&1
        fi
        
        # 启动前端
        cd frontend
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        cd ..
        sleep 5
        
        if check_port 3001; then
            echo -e "   前端服务已启动 ✓"
        else
            echo -e "${YELLOW}⚠️ 前端服务可能未启动，请查看 logs/frontend.log${NC}"
        fi
    fi
}

# 确保日志目录存在
mkdir -p logs

start_backend
start_frontend

# -----------------------------------------------------------------------------
# 6. 显示访问信息
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ SmartScout 启动完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "访问地址:"
echo -e "  ${GREEN}前端界面: http://localhost:3001${NC}"
echo -e "  ${GREEN}后端 API : http://localhost:8000${NC}"
echo -e "  ${GREEN}API 文档 : http://localhost:8000/docs${NC}"
echo ""
echo -e "日志文件:"
echo -e "  logs/backend.log"
echo -e "  logs/frontend.log"
echo ""
echo -e "${YELLOW}按回车打开浏览器访问...${NC}"
read

open http://localhost:3001
