#!/bin/bash

# SmartScout 启动脚本
# 双击此文件将启动后端服务并自动打开浏览器

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "   SmartScout 智能招标爬虫系统"
echo "========================================"
echo "项目目录: $SCRIPT_DIR"
echo ""

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    echo "请安装Python3后重试"
    exit 1
fi

# 检查服务是否已在运行
echo "检查服务状态..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ 后端服务已在运行 (端口 8000)"
    echo ""
    echo "正在打开浏览器..."
    open "http://localhost:8000"
    echo ""
    echo "访问地址:"
    echo "• API文档: http://localhost:8000/docs"
    echo "• 健康检查: http://localhost:8000/health"
    echo "• 重定向文档: http://localhost:8000/redoc"
    echo ""
    echo "按 Enter 键退出..."
    read -r
    exit 0
else
    echo "○ 后端服务未运行，正在启动..."
fi

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查依赖
echo "检查Python依赖..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "安装后端依赖..."
    pip install -r requirements_api.txt
fi

# 启动后端服务器（后台运行）
echo "启动后端服务器..."
echo "服务将运行在: http://localhost:8000"
echo ""

# 创建日志目录
mkdir -p logs

# 启动服务器并保存PID
python3 run.py > logs/startup.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > .server_pid
echo "服务器进程ID: $SERVER_PID"

# 等待服务器启动（最多30秒）
echo "等待服务器启动..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ 服务器启动成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  服务器启动较慢，请检查日志: logs/startup.log"
        echo "继续尝试打开浏览器..."
    fi
    sleep 1
done

# 自动打开浏览器
echo "正在打开浏览器..."
open "http://localhost:8000"

echo ""
echo "========================================"
echo "启动完成！"
echo "========================================"
echo "访问地址:"
echo "• 主页面: http://localhost:8000"
echo "• API文档: http://localhost:8000/docs"
echo "• 健康检查: http://localhost:8000/health"
echo "• 重定向文档: http://localhost:8000/redoc"
echo ""
echo "日志文件: logs/startup.log"
echo "进程ID文件: .server_pid"
echo ""
echo "要停止服务，请双击运行 '停止SmartScout.command'"
echo "或在此窗口按 Ctrl+C"
echo ""

# 显示实时日志
echo "=== 实时日志 (Ctrl+C 停止服务) ==="
tail -f logs/startup.log

# 捕获Ctrl+C，停止服务器
cleanup() {
    echo ""
    echo "正在停止服务器..."
    kill $SERVER_PID 2>/dev/null || true
    rm -f .server_pid
    echo "服务器已停止"
    exit 0
}

trap cleanup INT TERM

# 等待服务器进程结束
wait $SERVER_PID
cleanup