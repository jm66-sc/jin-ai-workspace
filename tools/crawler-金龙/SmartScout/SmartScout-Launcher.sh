#!/bin/bash

# SmartScout 桌面启动器
# 双击此脚本启动 SmartScout 系统

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SmartScout 桌面启动器 ===${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "项目目录: $SCRIPT_DIR"
echo "正在启动系统..."

# 检查是否已经在运行
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ 后端服务已在运行，跳过启动${NC}"
    BACKEND_RUNNING=true
else
    BACKEND_RUNNING=false
fi

if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ 前端服务已在运行，跳过启动${NC}"
    FRONTEND_RUNNING=true
else
    FRONTEND_RUNNING=false
fi

# 如果服务都在运行，直接打开浏览器
if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
    echo -e "${GREEN}✓ 所有服务已在运行${NC}"
    echo -e "${YELLOW}正在打开浏览器...${NC}"
    sleep 1
    open "http://localhost:3001"
    echo -e "\n${GREEN}系统访问地址:${NC}"
    echo -e "前端界面: ${GREEN}http://localhost:3001${NC}"
    echo -e "后端API:  ${GREEN}http://localhost:8000${NC}"
    echo -e "API文档: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "\n${YELLOW}按 Enter 键退出...${NC}"
    read -r
    exit 0
fi

# 执行一键启动脚本
echo -e "\n${YELLOW}正在启动 SmartScout 系统...${NC}"
echo -e "${YELLOW}请保持此窗口打开以运行系统${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 运行主启动脚本
./run_all.sh

echo -e "\n${GREEN}SmartScout 系统已停止${NC}"
echo -e "${YELLOW}按 Enter 键关闭窗口...${NC}"
read -r