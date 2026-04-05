#!/bin/bash

# SmartScout 停止脚本
# 双击此文件将停止由启动脚本运行的服务

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "   停止 SmartScout 服务"
echo "========================================"
echo "项目目录: $SCRIPT_DIR"
echo ""

# 检查PID文件
PID_FILE=".server_pid"
if [ ! -f "$PID_FILE" ]; then
    echo "未找到进程ID文件 ($PID_FILE)"
    echo "可能服务未启动，或已停止"

    # 尝试通过端口查找进程
    echo ""
    echo "尝试通过端口8000查找进程..."
    PORT_PID=$(lsof -ti:8000 2>/dev/null | head -1)
    if [ ! -z "$PORT_PID" ]; then
        echo "发现进程 $PORT_PID 正在使用端口8000"
        read -p "是否停止此进程？ [y/N] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill $PORT_PID 2>/dev/null
            echo "已停止进程 $PORT_PID"
        else
            echo "取消操作"
        fi
    else
        echo "未找到使用端口8000的进程"
    fi

    echo ""
    echo "按 Enter 键退出..."
    read -r
    exit 0
fi

# 读取PID
SERVER_PID=$(cat "$PID_FILE")
echo "找到进程ID: $SERVER_PID"

# 检查进程是否存在
if ps -p $SERVER_PID > /dev/null; then
    echo "进程正在运行，正在停止..."
    kill $SERVER_PID 2>/dev/null

    # 等待进程结束（最多5秒）
    for i in {1..5}; do
        if ! ps -p $SERVER_PID > /dev/null; then
            echo "✓ 服务已停止"
            break
        fi
        sleep 1
    done

    # 强制终止（如果仍在运行）
    if ps -p $SERVER_PID > /dev/null; then
        echo "强制终止进程..."
        kill -9 $SERVER_PID 2>/dev/null
        echo "服务已强制停止"
    fi
else
    echo "进程不存在（可能已停止）"
fi

# 删除PID文件
rm -f "$PID_FILE"
echo "已清理进程ID文件"

echo ""
echo "服务停止完成"
echo "按 Enter 键退出..."
read -r