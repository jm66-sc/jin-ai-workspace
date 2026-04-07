#!/bin/bash
# 金龙任务轮询脚本
# 每天 09:00 / 21:00 自动运行
# 安装方式：见 tools/setup-cron-金龙.md

REPO_DIR="/Users/jin/.qclaw/workspace/jin-ai-workspace"
LOG_FILE="$REPO_DIR/tools/poll-log-金龙.txt"
AGENT_NAME="金龙"

echo "=============================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') 开始轮询" >> "$LOG_FILE"

# 1. 拉取最新任务
cd "$REPO_DIR" || exit 1
git pull >> "$LOG_FILE" 2>&1

# 2. 扫描属于金龙的待执行任务
TASKS=$(grep "| $AGENT_NAME |" TASKS.md | grep -v "执行中\|已完成")

if [ -z "$TASKS" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 无新任务" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') 发现新任务：" >> "$LOG_FILE"
    echo "$TASKS" >> "$LOG_FILE"

    # 3. 提取任务ID列表
    TASK_IDS=$(echo "$TASKS" | grep -o 'T[0-9]\+')
    echo "$(date '+%Y-%m-%d %H:%M:%S') 任务ID：$TASK_IDS" >> "$LOG_FILE"

    # 4. 用 osascript 弹出通知（macOS 通知栏）
    osascript -e "display notification \"发现新任务：$TASK_IDS\" with title \"金龙任务提醒\" sound name \"Glass\""
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') 轮询完成" >> "$LOG_FILE"
