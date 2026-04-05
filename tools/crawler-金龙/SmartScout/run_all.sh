#!/bin/bash

# SmartScout 一键启动脚本
# 同时启动后端API服务和前端开发服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 日志文件
BACKEND_LOG="logs/backend.log"
FRONTEND_LOG="logs/frontend.log"
mkdir -p logs

echo -e "${GREEN}=== SmartScout 一键启动脚本 ===${NC}"
echo "项目目录: $SCRIPT_DIR"
echo "后端日志: $BACKEND_LOG"
echo "前端日志: $FRONTEND_LOG"
echo

# 函数：清理子进程
cleanup() {
    echo -e "\n${YELLOW}正在停止所有服务...${NC}"

    if [ ! -z "$BACKEND_PID" ]; then
        echo "停止后端进程 (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        echo "停止前端进程 (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    echo -e "${GREEN}所有服务已停止${NC}"
    exit 0
}

# 设置信号处理
trap cleanup INT TERM EXIT

# 检查依赖
echo -e "${YELLOW}检查依赖...${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3${NC}"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到Node.js${NC}"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到npm${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 所有依赖检查通过${NC}"

# 启动后端API服务
echo -e "\n${YELLOW}启动后端API服务...${NC}"
echo "后端服务将运行在: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "使用虚拟环境"
fi

# 安装后端依赖（如果需要）
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "安装后端依赖..."
    pip install -r requirements_api.txt
fi

# 在后台启动后端服务器
python3 run.py > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo "后端进程ID: $BACKEND_PID"

# 等待后端启动
echo -e "${YELLOW}等待后端服务启动...${NC}"
sleep 3

# 检查后端是否运行
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务启动成功${NC}"
else
    echo -e "${RED}✗ 后端服务启动失败，请检查日志: $BACKEND_LOG${NC}"
    echo "最后几行日志:"
    tail -10 "$BACKEND_LOG"
    exit 1
fi

# 启动前端开发服务器
echo -e "\n${YELLOW}启动前端开发服务器...${NC}"
echo "前端服务将运行在: http://localhost:3001"

# 进入前端目录
cd frontend

# 检查前端依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install --legacy-peer-deps
fi

# 在后台启动前端服务器
npm run dev > "../$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

cd ..

echo "前端进程ID: $FRONTEND_PID"

# 等待前端启动
echo -e "${YELLOW}等待前端服务启动...${NC}"
sleep 5

# 检查前端是否运行
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端服务启动成功${NC}"
else
    echo -e "${YELLOW}⚠ 前端服务可能启动较慢，请检查日志: $FRONTEND_LOG${NC}"
    echo "最后几行日志:"
    tail -10 "$FRONTEND_LOG"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}系统启动完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}访问地址:${NC}"
echo -e "前端界面: ${GREEN}http://localhost:3001${NC}"
echo -e "后端API:  ${GREEN}http://localhost:8000${NC}"
echo -e "API文档: ${GREEN}http://localhost:8000/docs${NC}"

# 自动打开浏览器
echo -e "\n${YELLOW}正在打开浏览器...${NC}"
sleep 2
open "http://localhost:3001"

echo -e "\n${YELLOW}日志文件:${NC}"
echo -e "后端日志: $BACKEND_LOG"
echo -e "前端日志: $FRONTEND_LOG"
echo -e "\n${YELLOW}按 Ctrl+C 停止所有服务${NC}"

# 显示实时日志
echo -e "\n${YELLOW}=== 实时日志 (Ctrl+C 退出) ===${NC}"
echo -e "${GREEN}后端日志:${NC}"
tail -f "$BACKEND_LOG" &
TAIL_BACKEND_PID=$!

echo -e "\n${GREEN}前端日志:${NC}"
tail -f "$FRONTEND_LOG" &
TAIL_FRONTEND_PID=$!

# 等待用户中断
wait $BACKEND_PID $FRONTEND_PID

# 停止日志输出
kill $TAIL_BACKEND_PID $TAIL_FRONTEND_PID 2>/dev/null || true