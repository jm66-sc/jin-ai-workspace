#!/usr/bin/env python3
"""
重置任务队列状态为pending
"""
import json
import os

queue_file = "data/temp/tasks.jsonl"

if not os.path.exists(queue_file):
    print(f"队列文件不存在: {queue_file}")
    exit(1)

# 读取所有任务
tasks = []
with open(queue_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            task = json.loads(line.strip())
            tasks.append(task)
        except json.JSONDecodeError:
            continue

print(f"找到 {len(tasks)} 个任务")

# 重置状态为pending
for task in tasks:
    task["status"] = "pending"
    task["processed_at"] = None
    task["error"] = None

# 写回文件
with open(queue_file, 'w', encoding='utf-8') as f:
    for task in tasks:
        f.write(json.dumps(task, ensure_ascii=False) + '\n')

print(f"已将 {len(tasks)} 个任务状态重置为pending")