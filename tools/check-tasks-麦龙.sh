#!/bin/bash
# 麦龙任务轮询脚本
# 每天 09:00 / 21:00 自动运行
# 安装方式：见 tools/setup-cron-麦龙.md

REPO_DIR="/workspace/jin-ai-workspace"
LOG_FILE="$REPO_DIR/tools/poll-log-麦龙.txt"
AGENT_NAME="麦龙"

# 钉钉机器人配置（发通知用）
DINGTALK_TOKEN="$DINGTALK_WEBHOOK_TOKEN"  # 从环境变量读取，勿硬编码

echo "=============================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') 开始轮询" >> "$LOG_FILE"

# 1. 拉取最新任务
cd "$REPO_DIR" || exit 1
git pull >> "$LOG_FILE" 2>&1

# 2. 扫描属于麦龙的待执行任务
TASKS=$(grep "| $AGENT_NAME |" TASKS.md | grep -v "执行中\|已完成")

if [ -z "$TASKS" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 无新任务" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') 发现新任务：" >> "$LOG_FILE"
    echo "$TASKS" >> "$LOG_FILE"

    # 3. 提取任务ID列表
    TASK_IDS=$(echo "$TASKS" | grep -o 'T[0-9]\+' | tr '\n' ' ')

    # 4. 通过钉钉机器人通知自己（发到群）
    if [ -n "$DINGTALK_TOKEN" ]; then
        MSG="【麦龙任务提醒】发现新任务：$TASK_IDS\n请前往 GitHub 查看：https://github.com/jm66-sc/jin-ai-workspace/blob/main/TASKS.md"
        curl -s -X POST "https://oapi.dingtalk.com/robot/send?access_token=$DINGTALK_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"msgtype\":\"text\",\"text\":{\"content\":\"$MSG\"}}" >> "$LOG_FILE" 2>&1
    fi
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') 轮询完成" >> "$LOG_FILE"
